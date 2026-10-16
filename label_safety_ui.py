"""Static, immediately visible safety context with expandable exact SPL evidence."""
import base64
import re
from html import escape as h
from pathlib import Path
from label_safety import safety_model,summary
ASSETS=Path(__file__).parent/'assets'
LABELS={'adverse':('이상반응','Reported adverse reactions','allergy.svg'),'food':('음식 · 음료','Food & drink','fruit_juice.svg'),'do_not_use':('사용 금기 · 중복 성분','Contraindications · duplicate actives','med_interaction.svg'),'interactions':('약물 상호작용 · 사전 상담','Drug interactions · consultation','med_interaction.svg'),'precautions':('중요 주의사항','Important precautions','review.svg'),'stop_use':('중단 · 상담 조건','Stop-use conditions','review.svg'),'directions':('연령 · 제형 · 복용 문맥','Age · formulation · directions','dose.svg'),'alcohol_caution':('알코올 주의','Alcohol caution','alcohol.svg'),'food_avoidance':('음식 관련 제한 문구','Food avoidance wording','fruit_juice.svg'),'food_administration':('음식과 관련된 복용 지침','Food administration instructions','dose.svg'),'food_wording':('음식·음료 관련 원문','Food/drink wording','review.svg')}
STYLE='''<style>
.label-safety{margin:24px 0;color:#19384a}.safety-head{display:flex;align-items:center;justify-content:space-between;gap:16px}.safety-head h2{font-size:1.4rem;letter-spacing:-.035em;margin:0 0 6px}.safety-sub{font-size:.8rem;color:#526574;line-height:1.7}.safety-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:18px 0}.safety-card{background:#fff;border:1px solid #cbdce4;border-radius:18px;padding:20px;min-width:0;overflow-wrap:anywhere}.safety-card h3{font-size:.96rem;margin:12px 0;line-height:1.4}.safety-icon{width:42px!important;height:42px!important;object-fit:contain!important;border-radius:0!important;box-shadow:none!important;display:block}.safety-card p{font-size:.82rem;line-height:1.7;color:#365262;margin:10px 0}.safety-tag{font-size:.67rem;font-weight:650;display:inline-block;border:1px solid #bdced8;border-radius:6px;padding:3px 6px;margin:5px 0;color:#355466}.label-safety details{border-top:1px solid #d8e4ea;margin-top:14px;padding-top:4px}.label-safety summary{min-height:44px;padding:12px 0;font-size:.76rem;font-weight:650;cursor:pointer;color:#174e65}.label-safety summary:focus-visible,.label-safety a:focus-visible{outline:3px solid #245dc1;outline-offset:3px}.safety-evidence{padding:12px;background:#f3f7f9;border-radius:10px;margin-bottom:12px}.safety-evidence p{white-space:pre-wrap;font-size:.76rem;line-height:1.8;overflow-wrap:anywhere}.safety-meta{font-size:.65rem!important;color:#4d6573!important;line-height:1.6}.label-safety a{color:#126b70;text-underline-offset:3px}.safety-urgent{border:1px solid #d7b7ac;border-left:4px solid #93452e;background:#fff7f2;border-radius:14px;padding:16px 20px;margin:12px 0;color:#593725;animation:none!important;transition:none!important;opacity:1!important}.safety-urgent strong{font-size:.92rem;line-height:1.6}.safety-urgent .safety-tag{color:#743f29;border-color:#c8a591}.safety-boundary{font-size:.74rem;color:#526574;line-height:1.75;margin:12px 0}.safety-unavailable{border:1px dashed #a6bbc7;border-radius:16px;padding:20px;color:#526574}@media(max-width:900px){.safety-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:600px){.safety-grid{grid-template-columns:1fr}.safety-card{padding:18px}.safety-head{display:block}.safety-urgent{padding:14px}.safety-head h2{font-size:1.25rem}}
</style>'''
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
        result+='<aside class="safety-urgent" aria-label="'+tr(lang,'레이블의 즉시 행동 문구','Immediate action wording in label')+'"><span class="safety-tag">'+tr(lang,'⚠ 조건에 해당할 때 · 원문 경고','⚠ If the condition applies · label warning')+'</span><br><strong>'+h(u['summary'][lang])+'</strong><details><summary>'+tr(lang,'조건·증상·원문 근거','Condition · symptoms · original evidence')+'</summary>'+evidence(u,lang)+'</details></aside>'
    return result

def safety_html(record,product,lang='en'):
    model=safety_model(record,product)
    if not model['available']:return '<section class="label-safety safety-unavailable">'+tr(lang,'선택 제품의 레이블 안전성 근거를 불러올 수 없습니다. 안전 여부를 판단할 수 없습니다.','Safety source unavailable for the selected product. Safety cannot be assessed.')+'</section>'
    out='<section class="label-safety"><div class="safety-head"><div><h2>'+tr(lang,'사용 전, 레이블에서 확인할 것','Before use, check the label')+'</h2><div class="safety-sub">'+h(product['name'])+' · NDC '+h(product.get('ndc') or '—')+'</div></div><span class="safety-tag">ADVICE → EVIDENCE → SOURCE</span></div>'
    out+='<p class="safety-boundary">'+tr(lang,'선택한 미국 레이블의 정보 탐색입니다. 모든 경고가 모든 사람에게 해당하지 않습니다. 개인별 복용 허가·진단이나 약사의 검토를 대신하지 않습니다. 원문은 영어로 보존하며, 아래 요약은 제한된 명시 문구만 안내합니다.','Navigation of the selected US label. Not every warning applies to every person. This is not personal medication clearance, diagnosis or a substitute for pharmacist review. Original English is preserved; summaries cover a limited set of explicit phrases.')+'</p>'
    if model['multiple_products']:out+='<p class="safety-boundary">'+tr(lang,'여러 제품·함량을 포함한 레이블입니다. 아래 문구가 선택한 함량·제형에 적용되는지 원문에서 확인하세요. 즉시 행동 요약은 제품별 적용을 확정할 수 없어 생략합니다.','This label covers multiple products/strengths. Check applicability to the selected strength/formulation. Immediate-action summaries are withheld where product applicability is uncertain.')+'</p>'
    groups=model['groups'];out+='<div class="safety-grid">'
    for key in ['adverse','food','stop_use','do_not_use','interactions','precautions','directions']:
        entries=groups[key]
        if not entries and key not in ('adverse','food','precautions'):continue
        k,e,img=LABELS[key];src='data:image/svg+xml;base64,'+base64.b64encode((ASSETS/img).read_bytes()).decode()
        out+='<article class="safety-card"><img class="safety-icon" src="'+src+'" alt=""><h3>'+h(k if lang=='ko' else e)+'</h3>'
        if not entries:
            missing=tr(lang,'이 레이블의 검토한 섹션에서 해당 정보를 찾지 못했습니다. 안전하거나 상호작용이 없다는 뜻은 아닙니다.','Information not found in the reviewed sections of this label. This does not mean safe or no interaction.')
            if key=='adverse':missing=tr(lang,'전용 이상반응 항목을 찾지 못했습니다. 아래의 중단·경고 문구와 구분해야 하며, 흔함·빈도는 추정하지 않습니다.','No dedicated adverse-reactions section found. Stop-use/warning wording is separate; commonness and frequency are not inferred.')
            out+='<p>'+missing+'</p>'
        else:
            # Distinguish each evidence category; never label all effects "common".
            primary=next((x for x in entries if key=='adverse' and 'the most common (>2%)' in x['text'].lower()),entries[0])
            shown=[primary]
            for item in shown:
                k2,e2,_=LABELS[item['kind']]
                if item['kind']!=key:out+='<span class="safety-tag">'+h(k2 if lang=='ko' else e2)+'</span>'
                out+='<p>'+h(summary(item,lang))+'</p>'
            if key=='food' and all(x['kind']=='alcohol_caution' for x in entries) and not any(re.search(r'\b(?:foods?|meals?|fruit juices?|grapefruit|dairy|milk|caffeine)\b',x['text'],re.I) for x in entries):out+='<p>'+tr(lang,'특정 음식의 금지·복용 지침은 검토한 섹션에서 찾지 못했습니다. 알코올 주의와 구분하세요.','Specific food avoidance/administration advice was not located in reviewed sections. Alcohol caution is separate.')+'</p>'
            out+='<details><summary>'+tr(lang,'공식 근거 · ','Official evidence · ')+str(len(entries))+tr(lang,'개 섹션',' section' if len(entries)==1 else ' sections')+'</summary>'+''.join(evidence(x,lang) for x in entries)+'</details>'
        out+='</article>'
    out+='</div><p class="safety-meta">SPL '+h(record['setid'])+' · v'+h(record.get('version',''))+' · Label '+h(record.get('effective_date',''))+' · Retrieved '+h(record.get('retrieved_at',''))+'</p></section>'
    return out
