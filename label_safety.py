"""Conservative section navigation, not a clinical assessment or generic drug matcher.

All content is scoped to the selected SPL. Source section types stay separate. Only a
small set of explicit label phrases receives reviewed bilingual action summaries.
Unknown wording remains original English, never guessed or labelled safe.
"""
import re
from label_sources import daily_med_url
CODES={'34084-4':'adverse','34070-3':'do_not_use','50570-1':'do_not_use','34073-7':'interactions','34071-1':'precautions','43685-7':'precautions','50569-3':'precautions','50568-5':'interactions','50567-7':'precautions','50566-9':'stop_use','53414-9':'precautions','34068-7':'directions','34076-0':'precautions','50565-1':'precautions'}
FOOD=re.compile(r'\b(food|meals?|fruit juices?|grapefruit|alcohol(?:ic)?(?: drinks?)?|dairy|milk|caffeine)\b',re.I)
URGENT=[('skin reaction occurs, stop use and seek medical help right away','피부 반응 시 사용 중단·즉시 의료 도움','Skin reaction: stop use and seek help right away'),('in case of overdose, get medical help or contact a poison control center right away','과량 복용 시 즉시 도움·중독관리센터 연락','Overdose: get help or contact Poison Control right away'),('an allergic reaction to this product occurs. seek medical help right away','이 제품에 알레르기 반응 시 즉시 의료 도움','Allergic reaction: seek medical help right away'),('if accidentally swallowed, get medical help or contact poison control center','잘못 삼켰다면 즉시 의료 도움·중독관리센터 연락','If accidentally swallowed: get help or contact Poison Control immediately')]

def category(s):
    code=s.get('code','')
    if code in CODES:return CODES[code]
    for c in s.get('parent_codes',[]):
        if c in CODES:return CODES[c]
    if code=='42229-5' and re.search(r'warning|allergy alert',s.get('title',''),re.I):return 'precautions'
    return None

def food_kind(text,kind):
    if not FOOD.search(text):return None
    low=text.lower()
    if re.search(r'\balcohol(?:ic)?\b',low):return 'alcohol_caution'
    if re.search(r'no need to|not necessary to|do not avoid|not required to',low):return 'food_wording'
    if re.search(r'\bavoid (?:eating |drinking |consuming )?(?:grapefruit|fruit juices?|milk|dairy|caffeine)\b|\bdo not (?:take (?:it )?with|drink|eat|consume) (?:any |these |the )?(?:fruit juices?|grapefruit|milk|dairy|food|caffeine)\b',low):return 'food_avoidance'
    if re.search(r'(?:with|following|after|before)\b[^.]{0,65}\b(?:food|meals?)\b',low) and kind in ('directions','precautions'):return 'food_administration'
    return 'food_wording'

def summary(entry,lang):
    ko=lang=='ko';text=entry['text'];low=text.lower();kind=entry['kind']
    if kind=='alcohol_caution' and re.search(r'3 or more alcoholic drinks (?:daily|every day)',low) and 'severe liver damage' in low:
        adult=bool(re.search(r'adult (?:has|takes) 3 or more',low))
        prefix=('성인에 대한 문구입니다. ' if ko else 'Adult-specific wording. ') if adult else ''
        return prefix+('복용 중 매일 알코올 음료 3잔 이상일 때 심각한 간 손상 위험을 경고합니다. 이 기준 미만이 안전하다는 뜻은 아닙니다.' if ko else 'The label warns of severe liver damage with 3 or more alcoholic drinks daily during use. This is not clearance for lower intake.')
    if kind=='food_avoidance' and 'do not take with fruit juices' in low:
        return ('이 제품은 과일 주스와 함께 복용하지 말라고 명시합니다.' if ko else 'This product says not to take it with fruit juices.')+ ((' 제산제 관련 별도 문구도 원문에서 확인하세요.' if ko else ' Review the separate antacid wording in the original section.') if 'antacids' in low else '')
    if kind=='food_administration' and 'regularly and continuously' in low and 'as directed' in low and re.search(r'preferably with or immediately following meals',low):
        return '처방 지시에 따라 규칙적으로 지속 복용하되, 가능하면 식사와 함께 또는 직후 복용하도록 안내합니다.' if ko else 'The label advises regular use as directed, preferably with or immediately following meals.'
    if kind=='adverse' and 'hypertension and angina' in low and 'the most common (>2%) adverse reactions are tiredness, dizziness, depression, diarrhea, shortness of breath, bradycardia, and rash.' in low:
        return '고혈압·협심증 문맥에서 피로·어지러움·우울·설사·호흡곤란·서맥·발진을 가장 흔한(>2%) 이상반응으로 기재합니다. 다른 환자군 빈도로 일반화하지 마세요.' if ko else 'For hypertension/angina, the label lists tiredness, dizziness, depression, diarrhea, shortness of breath, bradycardia and rash as most common (>2%). Do not generalize this rate to other populations.'
    if kind=='interactions' and 'ask a doctor or pharmacist' in low and 'before use' in low and 'blood thinning drug warfarin' in low:
        return '혈액희석제 와파린 복용 중에는 사용 전 의사·약사에게 문의하라고 명시합니다.' if ko else 'The label says to ask a doctor or pharmacist before use when taking the blood-thinning drug warfarin.'
    if kind=='precautions' and 'following abrupt cessation' in low and 'myocardial infarction have occurred' in low and 'without their physician' in low:
        return '일부 베타차단제의 갑작스러운 중단 후 협심증 악화·심근경색이 보고됐습니다. 이 제품도 의사의 조언 없이 중단하지 말라는 문구를 확인하세요.' if ko else 'Angina exacerbation and myocardial infarction have occurred after abrupt cessation of certain beta-blockers. This product warns against interruption without physician advice.'
    if kind=='do_not_use' and 'with any other drug containing acetaminophen' in low:
        return ('다른 아세트아미노펜 함유 약과 함께 사용하지 말라는 지침입니다.' if ko else 'Do not combine with another acetaminophen-containing drug.')+((' MAOI 복용·중단 후 2주 조건도 원문에서 확인하세요.' if ko else ' Review the MAOI and 2-week stopping condition in the source.') if 'monoamine oxidase inhibitor' in low and '2 weeks' in low else '')
    if kind=='precautions' and low=='for external use only':
        return '외용 전용 제품이라는 경고입니다. 복용 제품이 아닙니다.' if ko else 'For external use only; this is not an oral product.'
    if kind=='stop_use' and 'nervousness, dizziness, or sleeplessness occur' in low:
        return '신경과민·어지러움·불면이 생기면 중단하고 의사에게 문의하라는 문구입니다. 흔한 부작용이나 발생률을 뜻하지 않습니다.' if ko else 'Stop-use wording includes nervousness, dizziness or sleeplessness. This does not establish commonness or frequency.'
    return {'adverse':('이상반응 항목입니다. 빈도·비교군·환자군은 원문을 확인하세요.','Reported adverse reactions. Review frequency, comparison group and population in the original.'),'do_not_use':('사용 금기·사용하지 말아야 할 조건을 확인하세요. 모든 환자에게 해당한다는 뜻은 아닙니다.','Review contraindications or do-not-use conditions; they do not necessarily apply to every patient.'),'interactions':('약물 상호작용·사전 상담 조건입니다. 음식 금지와 구분해 확인하세요.','Drug interaction or pre-use consultation wording; separate from food restrictions.'),'directions':('이 제품의 연령·제형·용량 조건을 원문에서 확인하세요. 개인별 용량 권장이 아닙니다.','Review this product’s age, formulation and dose context. This is not personal dosing advice.'),'food_wording':('음식·음료 관련 문구가 있습니다. 실제 금지·복용 지침인지는 원문을 확인하세요.','Food or drink wording found. Check whether it is avoidance, administration guidance or another context.'),'food_administration':('음식과 관련된 복용 지침입니다. 음식 금지와 구분하세요.','Food-related administration instructions, separate from avoidance.'),'food_avoidance':('음식·음료 관련 사용 제한 문구입니다. 적용 조건과 범위는 원문을 확인하세요.','Food/drink avoidance wording. Check the exact conditions and scope in the source.'),'alcohol_caution':('알코올 관련 주의 문구입니다. 대상·양·기간 조건을 원문 그대로 확인하세요.','Alcohol caution. Review the exact population, amount and duration conditions.'),'stop_use':('사용 중단·상담 조건입니다. 일반적인 이상반응 목록과 구분하세요.','Stop-use and consultation conditions, separate from an adverse-reaction list.'),'precautions':('경고·사전 상담 조건입니다. 해당되는 조건을 원문에서 확인하세요.','Warnings and consultation conditions. Check applicability in the original section.')}[kind][0 if ko else 1]

def safety_model(record,product):
    groups={k:[] for k in ['adverse','food','do_not_use','interactions','precautions','stop_use','directions']}
    # No fallback to another label, sample medication or ingredient class.
    identity=bool(record and record.get('setid') and any(p==product for p in record.get('products',[])))
    if not identity or not record.get('sections'):
        return {'available':False,'groups':groups,'urgent':[],'reason':'source unavailable or selected product does not belong to label'}
    urgent=[];source=daily_med_url({'set_id':record['setid']},{})
    for s in record['sections']:
        kind=category(s);text=s.get('text','').strip()
        if not kind or not text:continue
        entry={**s,'kind':kind,'source':source,'setid':record['setid'],'version':record.get('version',''),'retrieved':record.get('retrieved_at',''),'label_date':record.get('effective_date','')}
        groups[kind].append(entry)
        if kind=='precautions' and 'do not take at the same time as aluminum or magnesium antacids' in text.lower():
            groups['interactions'].append({**entry,'kind':'interactions'})
        fk=food_kind(text,kind)
        if fk and kind!='adverse':groups['food'].append({**entry,'kind':fk})
        if kind in ['precautions','stop_use']:
            low=' '.join(text.lower().split())
            for phrase,k,e in URGENT:
                if phrase in low and not any(u['summary']['en']==e for u in urgent):urgent.append({**entry,'summary':{'ko':k,'en':e}})
    return {'available':True,'groups':groups,'urgent':urgent,'source':source,'setid':record['setid'],'ndc':product.get('ndc'),'multiple_products':len(record['products'])>1}
