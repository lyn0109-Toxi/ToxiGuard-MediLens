import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from composition import parse_spl
import molecular_assets as m
from composition_visuals import dose_visual_html
ROOT=Path(__file__).resolve().parents[1]
def product(name='excedrin'):
    return parse_spl((ROOT/'tests/fixtures'/(name+'.xml')).read_bytes())['products'][0]
def active():return [i for i in product()['ingredients'] if i['active']]
class MolecularTests(unittest.TestCase):
    def test_exact_unii_name_cid(self):
        for ingredient,cid in zip(active(),[1983,2244,2519]):
            e=m.lookup_structure(ingredient)
            self.assertEqual(e['CID'],cid);self.assertEqual(e['entity'],ingredient['name'])
            self.assertTrue(e['data_uri'].startswith('data:image/png;base64,'))
    def test_wrong_identifier(self):
        i=copy.deepcopy(active()[0]);i['unii']='R16CO5Y76E'
        self.assertIsNone(m.lookup_structure(i))
    def test_missing_identifier(self):
        i=copy.deepcopy(active()[0]);i.pop('unii')
        self.assertIsNone(m.lookup_structure(i))
    def test_salt_name_is_never_parent_substitution(self):
        i=copy.deepcopy(active()[0]);i['name']='ACETAMINOPHEN SODIUM'
        self.assertIsNone(m.lookup_structure(i))
        for ingredient in product('metoprolol-er')['ingredients']:
            if ingredient['active']:
                self.assertIsNone(m.lookup_structure(ingredient))
                self.assertIn('not a molecule',m.structure_tile(ingredient))
    def test_stereoisomer_not_fuzzy_matched(self):
        i=copy.deepcopy(active()[0]);i['name']='(R)-ACETAMINOPHEN'
        self.assertIsNone(m.lookup_structure(i))
    def test_case_and_whitespace_only_normalization(self):
        i=copy.deepcopy(active()[0]);i['name']='  acetaminophen  '
        self.assertEqual(m.lookup_structure(i)['CID'],1983)
    def test_missing_manifest_or_image(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(m.lookup_structure(active()[0],d))
            (Path(d)/'manifest.json').write_bytes((m.ASSET_DIR/'manifest.json').read_bytes())
            self.assertIsNone(m.lookup_structure(active()[0],d))
            with patch.object(m,'ASSET_DIR',Path(d)):
                self.assertIn('Generic symbol',m.structure_tile(active()[0]))
                self.assertNotIn('<img',m.structure_tile(active()[0]))
    def test_corrupt_image(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'manifest.json').write_bytes((m.ASSET_DIR/'manifest.json').read_bytes())
            (Path(d)/'cid-1983.png').write_bytes(b'not a png')
            self.assertIsNone(m.lookup_structure(active()[0],d))
    def test_bad_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            for raw in ['bad','[]','{"362O9ITL9D":{}}']:
                (Path(d)/'manifest.json').write_text(raw)
                self.assertIsNone(m.lookup_structure(active()[0],d))
    def test_manifest_identifiers_in_original_source(self):
        manifest=json.loads((m.ASSET_DIR/'manifest.json').read_text())
        synonyms={r['CID']:{s.upper() for s in r['Synonym']} for r in json.loads((m.ASSET_DIR/'pubchem-synonyms.json').read_text())['InformationList']['Information']}
        for unii,e in manifest.items():
            self.assertIn(unii,synonyms[e['CID']]);self.assertIn(e['entity'],synonyms[e['CID']])
    def test_equal_png_canvas_and_stable_colors(self):
        import struct
        seen=set()
        for i in active():
            entry=m.lookup_structure(i);data=(m.ASSET_DIR/entry['image']).read_bytes()
            self.assertEqual(struct.unpack('>II',data[16:24]),(600,420))
            seen.add(m.accent(i))
        self.assertEqual(len(seen),3)
        self.assertEqual(m.accent(active()[0]),m.accent(product('liquid')['ingredients'][4]))
    def test_integrated_image_bar_and_basis(self):
        html=dose_visual_html(product())
        self.assertEqual(html.count('class="molecule-image"'),3)
        self.assertEqual(html.count('class="dose-bar"'),3)
        self.assertIn('width:26.000000%',html)
        self.assertIn('Strength basis: ASPIRIN',html)
        self.assertIn('not potency or risk',html)
if __name__=='__main__':unittest.main()
