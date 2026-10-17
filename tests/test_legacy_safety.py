import ast
import subprocess
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
class LegacySafetyTests(unittest.TestCase):
    def test_clinical_functions_and_constants_unchanged(self):
        before=ast.parse(subprocess.check_output(['git','show','54a5f32:app.py'],cwd=ROOT,text=True))
        after=ast.parse((ROOT/'app.py').read_text())
        def stable(tree):
            return {node.name:ast.dump(node) for node in tree.body if isinstance(node,ast.FunctionDef) and not node.name.startswith('render_') and node.name not in {'main','card','avoid_card'}}
        self.assertEqual(stable(before),stable(after))
        self.assertEqual([ast.dump(n) for n in before.body if isinstance(n,ast.Assign)],[ast.dump(n) for n in after.body if isinstance(n,ast.Assign)])
    def test_legacy_language_and_product_switch(self):
        app=AppTest.from_file(str(ROOT/'app.py')).run()
        app.sidebar.radio[0].set_value('safety').run()
        self.assertFalse(app.exception)
        self.assertTrue(any('legacy-safety-icon' in x.value for x in app.markdown))
        self.assertGreaterEqual(len(app.expander),3)
        initial=app.sidebar.selectbox[0].value
        choices=app.sidebar.selectbox[0].options
        if len(choices)>1:app.sidebar.selectbox[0].select(choices[1]).run()
        self.assertFalse(app.exception)
        app.sidebar.segmented_control[0].set_value('en').run()
        self.assertFalse(app.exception)
        self.assertTrue(any('legacy-safety-icon' in x.value for x in app.markdown))
    def test_empty_model_panels(self):
        app=AppTest.from_string("import streamlit as st\nfrom app import render_side_effect_gallery,render_action_board,render_image_check_map\nfrom legacy_safety_ui import install_legacy_style\ninstall_legacy_style()\nwith st.container(key='legacy-safety'):\n render_side_effect_gallery({},'ko')\n render_action_board({},[],'ko')\n render_image_check_map({},[],'ko')").run()
        self.assertFalse(app.exception)
        self.assertFalse(any('class="legacy-safety-icon' in x.value for x in app.markdown))
if __name__=='__main__':unittest.main()
