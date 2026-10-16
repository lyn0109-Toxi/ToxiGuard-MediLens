import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from composition import parse_spl,SourceError
ROOT=Path(__file__).resolve().parents[1]
class SafetyUITests(unittest.TestCase):
    def fixture(self,n):return parse_spl((ROOT/'tests/fixtures'/(n+'.xml')).read_bytes(),retrieved_at='fixture date 2026-10-16')
    def test_selected_label_switch_does_not_leak_food_or_warnings(self):
        a=AppTest.from_string("from composition_ui import render_composition\nrender_composition('en')").run()
        for n,must,absent in [('mucinex-solution','3 or more alcoholic drinks','fruit juices'),('fexofenadine','not to take it with fruit juices','3 or more alcoholic drinks'),('artificial-tears','not an oral product','fruit juices')]:
            r=self.fixture(n);url='test:'+n
            a.session_state['composition_results']={'data':[{'setid':r['setid'],'title':r['title']}],'metadata':{},'url':url};a.session_state['composition_label_'+url]=0;a.session_state['composition_product_'+r['setid']]=0
            with patch('composition_ui.label',return_value=r):a.run()
            self.assertFalse(a.exception)
            html=' '.join(x.value for x in a.markdown if 'class="label-safety"' in x.value)
            self.assertIn(must,html);self.assertNotIn(absent,html)
    def test_missing_label_clears_existing_safety(self):
        a=AppTest.from_string("from composition_ui import render_composition\nrender_composition('ko')").run();r=self.fixture('mucinex-solution')
        a.session_state['composition_results']={'data':[{'setid':r['setid'],'title':r['title']}],'metadata':{},'url':'test'};a.session_state['composition_label_test']=0;a.session_state['composition_product_'+r['setid']]=0
        with patch('composition_ui.label',return_value=r):a.run()
        self.assertTrue(any('class="label-safety"' in x.value for x in a.markdown))
        with patch('composition_ui.label',side_effect=SourceError('synthetic offline')):a.run()
        self.assertTrue(a.error);self.assertFalse(any('class="label-safety"' in x.value for x in a.markdown))
if __name__=='__main__':unittest.main()
