import copy
import unittest
from pathlib import Path
from composition import parse_spl,chart_groups
from ingredient_evidence import inactive_evidence
from ingredient_map import map_data
from composition_visuals import dose_visual_html,excipient_visual_html
from streamlit.testing.v1 import AppTest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]

def record():return parse_spl((ROOT/'tests/fixtures/mucinex-solution.xml').read_bytes(),retrieved_at='2026-10-16T00:00:00Z')
class MapTests(unittest.TestCase):
    def test_mucinex_label_and_normalized(self):
        r=record();p=r['products'][0]
        self.assertEqual([i['amount'] for i in chart_groups(p['ingredients'],'label')['mg / 20 mL']],[650,20,400,10])
        self.assertEqual([i['amount'] for i in chart_groups(p['ingredients'])['mg / mL']],[32.5,1,20,.5])
        self.assertEqual(p['ndc'],'63824-548');self.assertIsNone(p['manufacturer'])
        self.assertEqual(r['version'],'9')
    def test_map_basis_and_structure(self):
        r=record();p=r['products'][0];d=map_data(p,r)
        active=[n for n in d['nodes'] if n['active']]
        self.assertEqual(len(active),4);self.assertEqual(active[0]['amount'],'650 mg · per 20 mL')
        self.assertTrue(active[0]['image'].startswith('data:image/png;base64,'));self.assertIsNone(active[1]['image'])
        self.assertEqual(active[1]['moiety'],'DEXTROMETHORPHAN');self.assertEqual(active[1]['basis'],'DEXTROMETHORPHAN HYDROBROMIDE')
        self.assertEqual(map_data(p,r,basis='normalized')['nodes'][0]['amount'],'32.5 mg · per mL')
    def test_narrative_qualifiers_and_no_fuzzy_identity(self):
        r=record();p=r['products'][0];rows=inactive_evidence(p,r['inactive_narrative'])
        citrate=next(i for i in rows if i['name']=='TRISODIUM CITRATE DIHYDRATE')
        self.assertEqual(citrate['presence'],'conditional');self.assertIn('[may contain this ingredient]',citrate['narrative'][0])
        glycerin=next(i for i in rows if i['name']=='GLYCERIN');self.assertEqual(glycerin['narrative'],['glycerin (soy)'])
        flavor=next(i for i in rows if i['name']=='flavor');self.assertEqual(flavor['origin'],'narrative-only');self.assertIsNone(flavor['unii'])
        water=next(i for i in rows if i['name']=='purified water');self.assertEqual(water['origin'],'narrative-only')
        html=excipient_visual_html(p,'en',r['inactive_narrative']);self.assertIn('conditional',html);self.assertIn('flavor',html)
    def test_denominators_not_combined(self):
        p=record()['products'][0];p=copy.deepcopy(p);p['ingredients'][1]['quantity']['denominator']['value']='5'
        groups=chart_groups(p['ingredients'],'label');self.assertEqual(set(groups),{'mg / 20 mL','mg / 5 mL'})
        with self.assertRaises(ValueError):chart_groups(p['ingredients'],'unsupported')
    def test_missing_narrative_and_many_nodes(self):
        r=record();p=r['products'][0];self.assertEqual(len(inactive_evidence(p,[])),14)
        p=copy.deepcopy(p);p['ingredients']=[{**p['ingredients'][0],'name':'Synthetic '+str(j),'unii':None} for j in range(18)]
        r['inactive_narrative']=[];d=map_data(p,r,'ko');self.assertEqual(len(d['nodes']),18);self.assertTrue(all(x['image'] is None for x in d['nodes']))
    def test_ui_default_label_and_switch(self):
        r=record();a=AppTest.from_string("from composition_ui import render_composition\nrender_composition('en')").run()
        a.session_state['composition_results']={'data':[{'setid':r['setid'],'title':r['title']}],'metadata':{},'url':'mucinex'}
        a.session_state['composition_label_mucinex']=0;a.session_state['composition_product_'+r['setid']]=0
        with patch('composition_ui.label',return_value=r):
            a.run();self.assertFalse(a.exception)
            basis=next(x for x in a.radio if x.label=='Amount display basis');self.assertEqual(basis.value,'label')
            self.assertTrue(any('650 mg per 20 mL' in m.value for m in a.markdown))
            basis.set_value('normalized').run();self.assertFalse(a.exception)
            self.assertTrue(any('32.5 mg per mL' in m.value for m in a.markdown))
        self.assertTrue(any('Advanced evidence' in e.label for e in a.expander))
    def test_reference_basis_is_visible_on_map_card(self):
        r=parse_spl((ROOT/'tests/fixtures/metoprolol-er.xml').read_bytes())
        node=map_data(r['products'][0],r)['nodes'][0]
        self.assertEqual(node['name'],'METOPROLOL SUCCINATE')
        self.assertEqual(node['basis'],'METOPROLOL TARTRATE')
        js=(ROOT/'ingredient_map_assets/map.js').read_text()
        self.assertIn("n.active&&n.basis!==n.name",js)
        self.assertIn("'Strength basis: ')+n.basis",js)

    def test_text_only_rendering_contract(self):
        js=(ROOT/'ingredient_map_assets/map.js').read_text()
        self.assertNotIn('innerHTML',js);self.assertIn('textContent=text',js)
        self.assertIn("dialog.addEventListener('cancel'",js);self.assertIn("origin.focus()",js)
if __name__=='__main__':unittest.main()
