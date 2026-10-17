import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MotionTests(unittest.TestCase):
    def test_system_and_in_app_reduced_motion_disable_backdrop(self):
        css=(ROOT/'ingredient_map_assets/map.css').read_text();js=(ROOT/'ingredient_map_assets/map.js').read_text()
        self.assertIn('@media(prefers-reduced-motion:reduce)',css)
        self.assertIn('dialog::backdrop{animation:none!important',css)
        self.assertIn('.reduce-motion dialog::backdrop',css)
        self.assertIn("window.matchMedia('(prefers-reduced-motion: reduce)')",js)
        self.assertIn('media.matches||userReduced',js)
        self.assertIn("if(reduced()){finishClose();return}",js)
    def test_close_timer_is_cancelled_on_cleanup_and_new_open(self):
        js=(ROOT/'ingredient_map_assets/map.js').read_text()
        self.assertIn('window.clearTimeout(closeTimer)',js)
        self.assertIn('function open(n,button){resetClose()',js)
        self.assertIn('abort.abort();resetClose()',js)
    def test_no_continuous_motion_or_visibility_delay_on_urgent(self):
        css=(ROOT/'ingredient_map_assets/map.css').read_text()
        self.assertNotIn('infinite',css);self.assertNotIn('rotate(',css)
        js=(ROOT/'ingredient_map_assets/map.js').read_text()
        self.assertIn('Math.min(j,5)*26',js)
        self.assertIn('iterations:1',js)
        self.assertIn('revealAnimations.forEach(a=>a.cancel())',js)
        self.assertIn('observer?.disconnect()',js)
        self.assertIn("if(reduced())clearReveal()",js)
        self.assertNotIn('animation:node-arrive',css)
        from label_safety_ui import STYLE
        safety=STYLE
        self.assertIn('animation:none!important;transition:none!important;opacity:1!important',safety)
if __name__=='__main__':unittest.main()
