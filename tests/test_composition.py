import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch
from composition import parse_spl, chart_groups, strength, search_labels, load_label, SourceError

FIX = Path(__file__).parent / 'fixtures'
def fixture(name):
    return parse_spl((FIX / (name + '.xml')).read_bytes(), 'https://dailymed.nlm.nih.gov/test', '2026-10-16T00:00:00Z')

class CompositionTests(unittest.TestCase):
    def test_single_tablet(self):
        r=fixture('acetaminophen');p=r['products'][0]
        self.assertEqual(p['ingredients'][0]['name'],'ACETAMINOPHEN')
        self.assertEqual(chart_groups(p['ingredients'])['mg / unit'][0]['amount'],500)
        self.assertEqual(p['release'],'unspecified')
        self.assertEqual(r['setid'],'00146b91-008d-4b16-95b0-6077f98821be')
        self.assertTrue(r['sections'])
        self.assertIsNone(p['manufacturer'])
        self.assertEqual(p['labeler'],'Amazon.com Services LLC')
    def test_undisclosed_inactive_is_not_zero(self):
        p=fixture('acetaminophen')['products'][0]
        for i in p['ingredients'][1:]:
            self.assertFalse(i['active']);self.assertIsNone(strength(i))
        self.assertEqual(len(chart_groups(p['ingredients'])['mg / unit']),1)
    def test_liquid(self):
        p=fixture('liquid')['products'][0]
        self.assertEqual(strength(next(i for i in p['ingredients'] if i['active'])),'160 mg / 5 mL')
        self.assertEqual(chart_groups(p['ingredients'])['mg / mL'][0]['amount'],32)
    def test_combination(self):
        p=fixture('excedrin')['products'][0]
        active=[i for i in p['ingredients'] if i['active']]
        self.assertEqual(len(active),3)
        self.assertEqual(sorted(x['amount'] for x in chart_groups(active)['mg / unit']),[65,250,250])
    def test_er_salt_and_reference_basis(self):
        p=fixture('metoprolol-er')['products']
        self.assertEqual(len(p),4)
        self.assertEqual(p[0]['release'],'extended')
        i=p[0]['ingredients'][0]
        self.assertEqual(i['name'],'METOPROLOL SUCCINATE')
        self.assertEqual(i['active_moieties'],['METOPROLOL'])
        self.assertEqual(i['basis'],'METOPROLOL TARTRATE')
        self.assertIn('asEquivalentSubstance',i['original_xml'])
    def test_unit_conversions(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']))
        for unit,value in [('g','.160'),('mg','160'),('ug','160000')]:
            i['quantity']['numerator']={'value':value,'unit':unit}
            self.assertEqual(chart_groups([i])['mg / mL'][0]['amount'],32)
        i['quantity']['denominator']={'value':'.005','unit':'L'}
        self.assertEqual(chart_groups([i])['mg / mL'][0]['amount'],32)
    def test_incompatible_and_missing_units(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']))
        for unit in ['[iU]','mEq','%','']:
            i['quantity']['numerator']['unit']=unit
            self.assertEqual(chart_groups([i]),{})
        i['quantity']['numerator']={'value':'160','unit':'mg'}
        i['quantity']['denominator']['unit']='unknown'
        self.assertEqual(chart_groups([i]),{})
    def test_invalid_amounts(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']))
        for value in ['NaN','Infinity','0','-2','','not a number']:
            i['quantity']['denominator']['value']=value
            self.assertEqual(chart_groups([i]),{});self.assertIsNone(strength(i))
    def test_unknown_basis_excluded(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']));i['basis']=None
        self.assertEqual(chart_groups([i]),{})
    def test_chart_numeric_render_range(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']))
        for value in ['1e9999','1e-9999','1e999999999']:
            i['quantity']['numerator']['value']=value
            for basis in ['label','normalized']:
                self.assertEqual(chart_groups([i],basis),{})
            self.assertIsNotNone(strength(i))  # Preserve evidence even when unchartable.

    def test_chart_denominator_render_range(self):
        i=copy.deepcopy(next(i for i in fixture('liquid')['products'][0]['ingredients'] if i['active']))
        for unit in ['mL','L','uL']:
            for value in ['1e999999999','1e-999999999']:
                i['quantity']['denominator']={'unit':unit,'value':value}
                self.assertEqual(chart_groups([i],'normalized'),{})

    def test_blank_search(self):
        for q in ['', ' ', 'a']:
            with self.assertRaises(ValueError): search_labels(q)
    def test_ambiguous_search_preserves_all(self):
        results={'data':[{'setid':'a','title':'drug 10 mg'},{'setid':'b','title':'drug 20 mg'}],'metadata':{'total_elements':2}}
        with patch('composition.fetch',return_value=json.dumps(results).encode()) as f:
            r=search_labels('drug','Maker','manufacturer',2)
        self.assertEqual(len(r['data']),2)
        self.assertIn('manufacturer=Maker',f.call_args.args[0]);self.assertIn('page=2',r['url'])
    def test_empty_search(self):
        with patch('composition.fetch',return_value=b'{"data": [], "metadata": {}}'):
            self.assertEqual(search_labels('missing')['data'],[])
    def test_source_failure(self):
        with patch('composition.fetch',side_effect=SourceError('offline')):
            with self.assertRaises(SourceError): search_labels('drug')
            with self.assertRaises(SourceError):load_label('00146b91-008d-4b16-95b0-6077f98821be')
    def test_explicit_release_variants(self):
        raw=(FIX/'acetaminophen.xml').read_bytes()
        for text,expected in [(b'TABLET, IMMEDIATE RELEASE','immediate'),(b'TABLET, DELAYED RELEASE','delayed')]:
            r=parse_spl(raw.replace(b'TABLET, FILM COATED',text))
            self.assertEqual(r['products'][0]['release'],expected)
    def test_malformed_search(self):
        for raw in [b'bad json',b'{"data":null}',b'{"data":[{}]}']:
            with patch('composition.fetch',return_value=raw):
                with self.assertRaises(SourceError):search_labels('drug')
    def test_wrong_source_identity(self):
        with patch('composition.fetch',return_value=(FIX/'acetaminophen.xml').read_bytes()):
            with self.assertRaises(SourceError):load_label('11111111-1111-1111-1111-111111111111')
    def test_invalid_xml(self):
        for raw in [b'not xml',b'<!DOCTYPE x><x/>']:
            with self.assertRaises(SourceError):parse_spl(raw)
    def test_kit_missing_not_fabricated(self):
        self.assertEqual(fixture('combination')['products'],[])

if __name__=='__main__':unittest.main()
