"""Static, immediately visible safety context with expandable exact SPL evidence."""
import base64
import re
from html import escape as h
from pathlib import Path
from label_safety import safety_model,summary
ASSETS=Path(__file__).parent/'assets'/'safety'
LABELS={'adverse':('이상반응','Reported adverse reactions','allergy.svg'),'food':('음식 · 음료','Food & drink','fruit_juice.svg'),'do_not_use':('사용 금기 · 중복 성분','Contraindications · duplicate actives','med_interaction.svg'),'interactions':('약물 상호작용 · 사전 상담','Drug interactions · consultation','med_interaction.svg'),'precautions':('중요 주의사항','Important precautions','review.svg'),'stop_use':('중단 · 상담 조건','Stop-use conditions','review.svg'),'directions':('연령 · 제형 · 복용 문맥','Age · formulation · directions','dose.svg'),'alcohol_caution':('알코올 주의','Alcohol caution','alcohol.svg'),'food_avoidance':('음식 관련 제한 문구','Food avoidance wording','fruit_juice.svg'),'food_administration':('음식과 관련된 복용 지침','Food administration instructions','dose.svg'),'food_wording':('음식·음료 관련 원문','Food/drink wording','review.svg')}
STYLE='<style>'+ (Path(__file__).parent/'safety_graphics.css').read_text() +'</style>'
def tr(lang,k,e):return k if lang=='ko' else e

def evidence(entry,lang):
    title=entry.get('title') or entry.get('display_name') or entry['kind']
    meta=' · '.join(filter(None,[title,'LOINC '+entry.get('code',''),'Section date '+(entry.get('effective_date') or 'not disclosed'),'SPL v'+entry.get('version',''),'Label '+entry.get('label_date',''),'Retrieved '+entry.get('retrieved','')]))
    return '<div class="safety-evidence"><p class="safety-meta">'+h(meta)+'</p><p lang="en">'+h(entry['text'])+'</p><a target="_blank" rel="noopener noreferrer" href="'+h(entry['source'],quote=True)+'">'+tr(lang,'DailyMed 원문 · 해당 섹션 확인','DailyMed original · review this section')+'</a></div>'

def urgent_html(record,product,lang='en'):
    model=safety_model(record,product)
    if not model['available'] or model.get('multiple_products'):return ''
    result=''
    for u in model['urgent']:
        result+='<aside class="safety-urgent" aria-label="'+tr(lang,'레이블의 즉시 행동 문구','Immediate action wording in label')+'"><span class="safety-tag">'+tr(lang,'⚠ 조건에 해당할 때 · 원문 경고','⚠ If the condition applies · label warning')+'</span><br><strong>'+h(u['summary'][lang])+'</strong><details open><summary>'+tr(lang,'조건·증상·원문 근거','Condition · symptoms · original evidence')+'</summary>'+evidence(u,lang)+'</details></aside>'
    return result

def safety_html(record,product,lang='en'):
    model=safety_model(record,product)
    if not model['available']:return '<section class="label-safety safety-unavailable">'+tr(lang,'선택 제품의 레이블 안전성 근거를 불러올 수 없습니다. 안전 여부를 판단할 수 없습니다.','Safety source unavailable for the selected product. Safety cannot be assessed.')+'</section>'
    out='<section class="label-safety"><div class="safety-head"><div><h2>'+tr(lang,'사용 전, 레이블에서 확인할 것','Before use, check the label')+'</h2><div class="safety-sub">'+h(product['name'])+' · NDC '+h(product.get('ndc') or '—')+'</div></div><span class="safety-tag">'+tr(lang,'제품별 레이블 근거','PRODUCT LABEL EVIDENCE')+'</span></div>'
    out+='<p class="safety-boundary">'+tr(lang,'선택한 미국 레이블의 정보 탐색입니다. 모든 경고가 모든 사람에게 해당하지 않습니다. 개인별 복용 허가·진단이나 약사의 검토를 대신하지 않습니다. 원문은 영어로 보존하며, 아래 요약은 제한된 명시 문구만 안내합니다.','Navigation of the selected US label. Not every warning applies to every person. This is not personal medication clearance, diagnosis or a substitute for pharmacist review. Original English is preserved; summaries cover a limited set of explicit phrases.')+'</p>'
    if model['multiple_products']:out+='<p class="safety-boundary">'+tr(lang,'여러 제품·함량을 포함한 레이블입니다. 아래 문구가 선택한 함량·제형에 적용되는지 원문에서 확인하세요. 즉시 행동 요약은 제품별 적용을 확정할 수 없어 생략합니다.','This label covers multiple products/strengths. Check applicability to the selected strength/formulation. Immediate-action summaries are withheld where product applicability is uncertain.')+'</p>'
    groups=model['groups'];out+='<div class="safety-grid">'
    for key in ['adverse','food','stop_use','do_not_use','interactions','precautions','directions']:
        entries=groups[key]
        # Keep every category visible; absence is never a safety verdict.
        k,e,img=LABELS[key];src='data:image/svg+xml;base64,'+base64.b64encode((ASSETS/(key+'.svg')).read_bytes()).decode()
        out+='<article class="safety-card safety-kind-'+key+'"><div class="safety-card-heading"><span class="safety-icon-frame" aria-hidden="true"><img class="safety-icon" src="'+src+'" alt=""></span><h3>'+h(k if lang=='ko' else e)+'</h3></div>'
        if not entries:
            missing=tr(lang,'이 레이블의 검토한 섹션에서 해당 정보를 찾지 못했습니다. 안전하거나 상호작용이 없다는 뜻은 아닙니다.','Information not found in the reviewed sections of this label. This does not mean safe or no interaction.')
            if key=='adverse':missing=tr(lang,'전용 이상반응 항목을 찾지 못했습니다. 아래의 중단·경고 문구와 구분해야 하며, 흔함·빈도는 추정하지 않습니다.','No dedicated adverse-reactions section found. Stop-use/warning wording is separate; commonness and frequency are not inferred.')
            out+='<p>'+missing+'</p>'
        else:
            # Distinguish each evidence category; never label all effects "common".
            primary=next((x for x in entries if key=='adverse' and 'the most common (>2%)' in x['text'].lower()),entries[0])
            shown=[]
            seen=set()
            for item in [primary] + [x for x in entries if x is not primary]:
                signature=(item['kind'],summary(item,lang))
                if signature not in seen:
                    shown.append(item);seen.add(signature)
            for item in shown:
                k2,e2,_=LABELS[item['kind']]
                if item['kind']!=key:out+='<span class="safety-tag">'+h(k2 if lang=='ko' else e2)+'</span>'
                out+='<p>'+h(summary(item,lang))+'</p>'
            if key=='food' and all(x['kind']=='alcohol_caution' for x in entries) and not any(re.search(r'\b(?:foods?|meals?|fruit juices?|grapefruit|dairy|milk|caffeine)\b',x['text'],re.I) for x in entries):out+='<p>'+tr(lang,'특정 음식의 금지·복용 지침은 검토한 섹션에서 찾지 못했습니다. 알코올 주의와 구분하세요.','Specific food avoidance/administration advice was not located in reviewed sections. Alcohol caution is separate.')+'</p>'
            out+='<details'+(' open' if key in ('stop_use','do_not_use','interactions','precautions','food','directions') else '')+'><summary>'+tr(lang,'적용 조건 · 원문 근거 · ','Conditions · original evidence · ')+str(len(entries))+tr(lang,'개 섹션',' section' if len(entries)==1 else ' sections')+'</summary>'+''.join(evidence(x,lang) for x in entries)+'</details>'
        out+='</article>'
    out+='</div><p class="safety-meta">SPL '+h(record['setid'])+' · v'+h(record.get('version',''))+' · Label '+h(record.get('effective_date',''))+' · Retrieved '+h(record.get('retrieved_at',''))+'</p></section>'
    return out
