"""Safety graphics preserve source conditions and empty-state meaning."""
import unittest
from html import escape
from pathlib import Path
from composition import parse_spl
from label_safety import safety_model
from label_safety_ui import safety_html, urgent_html
ROOT=Path(__file__).resolve().parents[1]
class SafetyGraphicsTests(unittest.TestCase):
    def test_all_categories_and_original_conditions_survive_both_languages(self):
        for name in ['mucinex-solution','fexofenadine','artificial-tears','metoprolol-er']:
            r=parse_spl((ROOT/'tests/fixtures'/(name+'.xml')).read_bytes());p=r['products'][0]
            model=safety_model(r,p)
            for lang in ['en','ko']:
                html=safety_html(r,p,lang)
                for key,entries in model['groups'].items():
                    self.assertIn('safety-kind-'+key,html)
                    for entry in entries:self.assertIn(escape(entry['text']),html)
                self.assertNotIn('<script',html)
    def test_urgent_conditions_default_open(self):
        r=parse_spl((ROOT/'tests/fixtures/mucinex-solution.xml').read_bytes())
        html=urgent_html(r,r['products'][0])
        self.assertEqual(html.count('<details open>'),2)
    def test_no_cross_product_reuse(self):
        r=parse_spl((ROOT/'tests/fixtures/mucinex-solution.xml').read_bytes())
        other=parse_spl((ROOT/'tests/fixtures/fexofenadine.xml').read_bytes())
        html=safety_html(r,other['products'][0])
        self.assertIn('unavailable',html)
        self.assertNotIn('safety-card',html)
if __name__=='__main__':unittest.main()
