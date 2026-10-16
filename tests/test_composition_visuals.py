import copy
import unittest
from pathlib import Path
from composition import parse_spl
from composition_visuals import dose_visual_html, excipient_visual_html, per_unit, fmt
F=Path(__file__).parent/'fixtures'
def product(name):return parse_spl((F/(name+'.xml')).read_bytes())['products'][0]
class VisualTests(unittest.TestCase):
    def test_small_nonzero_strength_is_not_displayed_as_zero(self):
        for value in [1e-9,1e-7,5e-324]:
            self.assertNotEqual(fmt(value),'0')
        self.assertEqual(fmt(0),'0')
        self.assertEqual(fmt(32.5),'32.5')
        p=copy.deepcopy(product('acetaminophen'))
        p['ingredients'][0]['quantity']['numerator']['value']='0.000000001'
        self.assertIn('1e-09 mg',dose_visual_html(p))

    def test_combination_proportions_and_direct_labels(self):
        html=dose_visual_html(product('excedrin'))
        self.assertEqual(html.count('class="dose-bar"'),3)
        self.assertEqual(html.count('width:100.000000%'),2)
        self.assertIn('width:26.000000%',html)
        self.assertIn('65 mg per tablet',html)
        self.assertIn('250 mg per tablet',html)
        self.assertNotIn('ingredient-card',html)
    def test_single_no_invented_maximum_or_comparator(self):
        html=dose_visual_html(product('acetaminophen'))
        self.assertEqual(html.count('class="dose-bar"'),1)
        self.assertIn('500 mg per tablet',html)
        self.assertIn('not a maximum dose or total product mass',html)
        self.assertNotIn('100%',html)
    def test_liquid_original_and_normalized_denominator(self):
        html=dose_visual_html(product('liquid'))
        self.assertIn('32 mg per mL',html)
        self.assertIn('160 mg / 5 mL',html)
    def test_basis_preserved(self):
        html=dose_visual_html(product('metoprolol-er'))
        self.assertIn('METOPROLOL SUCCINATE',html)
        self.assertIn('Strength basis: METOPROLOL TARTRATE',html)
        self.assertIn('25 mg per tablet',html)
    def test_missing_excipients_not_quantified(self):
        html=excipient_visual_html(product('acetaminophen'))
        self.assertIn('quantities not disclosed',html)
        self.assertIn('not zero or a composition share',html)
        self.assertNotIn('dose-bar',html)
        self.assertNotIn('width:',html)
    def test_incompatible_denominators_separate_figures(self):
        p=product('excedrin');i=copy.deepcopy(next(i for i in p['ingredients'] if i['active']))
        i['quantity']['denominator']={'value':'5','unit':'mL'}
        p['ingredients'].append(i)
        html=dose_visual_html(p)
        self.assertEqual(html.count('<figure'),2)
        self.assertIn('per tablet',html);self.assertIn('per mL',html)
    def test_incompatible_units_unscaled(self):
        p=product('acetaminophen');p['ingredients'][0]['quantity']['numerator']['unit']='[iU]'
        html=dose_visual_html(p)
        self.assertNotIn('dose-bar',html)
        self.assertIn('500 [iU]',html)
        self.assertIn('No proportional bar',html)
    def test_korean(self):
        html=dose_visual_html(product('excedrin'),'ko')
        self.assertIn('1정당 250 mg',html)
        self.assertIn('강도 기준',html)
        self.assertIn('함량 미공개',excipient_visual_html(product('liquid'),'ko'))
if __name__=='__main__':unittest.main()
