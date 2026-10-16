import copy,unittest
from pathlib import Path
from composition import parse_spl
from label_safety import safety_model,summary,food_kind
from label_safety_ui import safety_html,urgent_html
from label_sources import daily_med_url
F=Path(__file__).parent/'fixtures'
def fixture(n):return parse_spl((F/(n+'.xml')).read_bytes(),retrieved_at='2026-10-16T18:00:00Z')
class SafetyTests(unittest.TestCase):
    def test_mucinex_OTC_not_common_effects(self):
        r=fixture('mucinex-solution');m=safety_model(r,r['products'][0])
        self.assertFalse(m['groups']['adverse']);self.assertEqual(len(m['urgent']),2)
        stop=m['groups']['stop_use'][0]
        self.assertIn('nervousness, dizziness, or sleeplessness',stop['text'])
        self.assertIn('does not establish commonness',summary(stop,'en'))
    def test_mucinex_alcohol_threshold_not_blanket_food_ban(self):
        r=fixture('mucinex-solution');m=safety_model(r,r['products'][0]);food=m['groups']['food']
        self.assertEqual(len(food),1);self.assertEqual(food[0]['kind'],'alcohol_caution')
        for lang,token in [('en','3 or more'),('ko','3잔 이상')]:self.assertIn(token,summary(food[0],lang))
        html=safety_html(r,r['products'][0]);self.assertNotIn('grapefruit',html);self.assertNotIn('dairy',html)
    def test_adult_threshold_retains_population(self):
        e={'kind':'alcohol_caution','text':'Severe liver damage may occur if adult has 3 or more alcoholic drinks every day.'}
        self.assertIn('Adult-specific',summary(e,'en'))
        self.assertIn('성인',summary(e,'ko'))

    def test_duplicate_MAOI_warfarin_conditions(self):
        r=fixture('mucinex-solution');g=safety_model(r,r['products'][0])['groups']
        self.assertIn('2-week',summary(g['do_not_use'][0],'en'))
        self.assertIn('warfarin',summary(g['interactions'][0],'en'))
        self.assertIn('2 weeks',g['do_not_use'][0]['text'])
    def test_no_MAOI_invention_for_other_labels(self):
        r=fixture('acetaminophen');m=safety_model(r,r['products'][0])
        for e in m['groups']['do_not_use']:
            if 'MAOI' not in e['text']:self.assertNotIn('MAOI',summary(e,'en'))
    def test_actual_food_avoidance_and_antacid_distinct(self):
        r=fixture('fexofenadine');g=safety_model(r,r['products'][0])['groups']
        self.assertEqual(g['food'][0]['kind'],'food_avoidance')
        self.assertIn('fruit juices',summary(g['food'][0],'en'))
        self.assertTrue(g['interactions']);self.assertIn('aluminum or magnesium antacids',g['interactions'][0]['text'])
        self.assertIn('12 years',g['directions'][0]['text'])
        self.assertIn('65 years',g['directions'][0]['text'])
    def test_actual_food_administration_not_avoidance(self):
        r=fixture('metoprolol-er');g=safety_model(r,r['products'][0])['groups']
        self.assertEqual(g['food'][0]['kind'],'food_administration')
        self.assertIn('as directed',summary(g['food'][0],'en'))
        self.assertIn('preferably',summary(g['food'][0],'en'))
    def test_common_frequency_and_population_are_source_backed(self):
        r=fixture('metoprolol-er');g=safety_model(r,r['products'][0])['groups']
        e=next(e for e in g['adverse'] if 'the most common (>2%)' in e['text'].lower())
        s=summary(e,'en');self.assertIn('hypertension/angina',s);self.assertIn('>2%',s);self.assertIn('Do not generalize',s)
        self.assertIn('MERIT-HF',e['text'])
    def test_multiple_strengths_scope_is_explicit(self):
        r=fixture('metoprolol-er');p=r['products'][0]
        self.assertTrue(safety_model(r,p)['multiple_products']);self.assertIn('multiple products/strengths',safety_html(r,p));self.assertEqual(urgent_html(r,p),'')
    def test_real_no_food_advice_and_external_only(self):
        r=fixture('artificial-tears');p=r['products'][0];g=safety_model(r,p)['groups']
        self.assertEqual(g['food'],[]);html=safety_html(r,p)
        self.assertIn('Information not found',html);self.assertIn('does not mean safe',html)
        self.assertIn('not an oral product',html);self.assertNotIn('grapefruit',html)
    def test_missing_source_has_no_fallback_or_old_items(self):
        r=fixture('mucinex-solution');p=r['products'][0]
        for source in [None,{},dict(r,sections=[])]:
            self.assertFalse(safety_model(source,p)['available']);self.assertIn('unavailable',safety_html(source,p));self.assertEqual(urgent_html(source,p),'')
    def test_wrong_product_and_stale_strength_rejected(self):
        r=fixture('mucinex-solution');other=fixture('fexofenadine')['products'][0]
        self.assertFalse(safety_model(r,other)['available'])
        p=copy.deepcopy(r['products'][0]);p['ingredients'][0]['quantity']['numerator']['value']='5'
        self.assertFalse(safety_model(r,p)['available'])
    def test_provenance_each_entry(self):
        r=fixture('mucinex-solution');m=safety_model(r,r['products'][0])
        for entries in m['groups'].values():
            for e in entries:
                self.assertEqual(e['setid'],r['setid']);self.assertEqual(e['retrieved'],'2026-10-16T18:00:00Z');self.assertTrue(e['code']);self.assertTrue(e['effective_date']);self.assertIn(r['setid'],e['source'])
        self.assertIn('LOINC 50566-9',safety_html(r,r['products'][0]))
    def test_no_false_avoidance_from_negation_or_driving(self):
        self.assertEqual(food_kind('There is no need to avoid grapefruit.','precautions'),'food_wording')
        self.assertEqual(food_kind('Take with meals. Avoid operating machinery.','precautions'),'food_administration')
        self.assertIsNone(food_kind('Remove contact lens before using.','precautions'))
    def test_urgent_not_from_symptom_mention_or_frequency(self):
        r=fixture('mucinex-solution');r['sections']=[{'code':'34084-4','text':'rash, nervousness, dizziness','title':'Adverse reactions'}]
        self.assertEqual(safety_model(r,r['products'][0])['urgent'],[])
    def test_HTML_escapes_source_and_urgent_is_not_animated(self):
        r=fixture('mucinex-solution');r['sections'][0]['text']='<script>bad()</script>';r['sections'][0]['code']='34071-1'
        html=safety_html(r,r['products'][0]);self.assertNotIn('<script>',html);self.assertIn('&lt;script&gt;',html)
        self.assertIn('safety-urgent',urgent_html(r,r['products'][0]));self.assertNotIn('node-arrive',urgent_html(r,r['products'][0]))
    def test_retained_safety_fixtures_match_provenance(self):
        import json, hashlib
        from pathlib import Path
        base=Path(__file__).parent/'fixtures'
        for row in json.loads((base/'SAFETY_SOURCES.json').read_text()):
            self.assertEqual(hashlib.sha256((base/row['fixture']).read_bytes()).hexdigest(),row['sha256'])
            self.assertTrue(row['source_url'].startswith('https://dailymed.nlm.nih.gov/'))

    def test_shared_source_resolver(self):
        self.assertIn('setid=abc',daily_med_url({'set_id':'abc'},{}));self.assertIn('setid=def',daily_med_url({}, {'spl_set_id':['def']}));self.assertIn('spls_api',daily_med_url({},{}))
if __name__=='__main__':unittest.main()
