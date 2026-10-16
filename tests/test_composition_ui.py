import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from composition import parse_spl, SourceError

ROOT=Path(__file__).resolve().parents[1]
class UITests(unittest.TestCase):
    def app(self,lang='en'):
        a=AppTest.from_string("from composition_ui import render_composition\nrender_composition('"+lang+"')")
        return a.run()
    def seed(self,a):
        r=parse_spl((ROOT/'tests/fixtures/excedrin.xml').read_bytes(),'https://dailymed.nlm.nih.gov/example')
        a.session_state['composition_results']={'data':[{'setid':r['setid'],'title':r['title']}],'metadata':{'total_elements':1},'url':'test'}
        return r
    def test_english_and_korean(self):
        for lang in ['en','ko']:
            a=self.app(lang);self.assertFalse(a.exception)
            self.assertEqual(len(a.text_input),2)
            a.radio[0].set_value('KR').run()
            self.assertFalse(a.exception)
            self.assertTrue(any(('MFDS' in x.value) for x in a.info))
            self.assertEqual(len(a.text_input),0)
    def test_explicit_selection_and_bars(self):
        a=self.app();r=self.seed(a);a.run()
        self.assertIsNone(a.selectbox[-1].value)
        with patch('composition_ui.label',return_value=r):
            a.selectbox[-1].select(0).run();self.assertFalse(a.exception)
            self.assertIsNone(a.selectbox[-1].value)
            a.selectbox[-1].select(0).run();self.assertFalse(a.exception)
        cards=[x.value for x in a.markdown if '<figure class="dose-figure"' in x.value]
        self.assertTrue(any('250 mg per tablet' in x for x in cards))
        self.assertTrue(any('65 mg per tablet' in x for x in cards))
    def test_label_failure(self):
        a=self.app();self.seed(a);a.run()
        with patch('composition_ui.label',side_effect=SourceError('offline')):
            a.selectbox[-1].select(0).run()
        self.assertFalse(a.exception);self.assertTrue(a.error)
    def test_search_failure_clears_previous(self):
        a=self.app();self.seed(a);a.run()
        with patch('composition_ui.search',side_effect=SourceError('offline')):
            a.text_input[0].set_value('Excedrin');a.button[0].click().run()
        self.assertFalse(a.exception);self.assertTrue(a.error)
        self.assertNotIn('composition_results',a.session_state)
    def test_existing_app_starts(self):
        a=AppTest.from_file(str(ROOT/'app.py')).run()
        self.assertFalse(a.exception)
    def test_existing_safety_workspace(self):
        a=AppTest.from_file(str(ROOT/'app.py')).run()
        next(r for r in a.radio if r.label=='보기 / Workspace').set_value('safety').run()
        self.assertFalse(a.exception)
        self.assertTrue(any(m.value == '### 근거' for m in a.markdown))
if __name__=='__main__':unittest.main()
