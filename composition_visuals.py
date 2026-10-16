"""Responsive, label-backed dose bars. No formulation totals or dosing limits."""
from html import escape
from composition import chart_groups, strength
from molecular_assets import structure_tile, accent
from ingredient_evidence import inactive_evidence

STYLE = '''<style>
.composition-hero{padding:14px 0 18px;border-bottom:1px solid #cbe2df;margin-bottom:18px;color:#153e44}.composition-hero h1{font-size:1.85rem;margin:4px 0}.composition-hero p{color:#526b70;margin:0;font-size:.95rem}
.dose-figure{background:#fbfcfe;border:1px solid #c9e2de;border-radius:20px;padding:28px 30px;margin:14px 0 18px;color:#133e43;box-sizing:border-box}.dose-figure *{box-sizing:border-box}.dose-kicker{font-size:.74rem;letter-spacing:.12em;color:#4c7476;text-transform:uppercase}.dose-title{font-size:1.35rem;font-weight:700;margin:5px 0 12px}.dose-axis{display:flex;justify-content:space-between;border-bottom:1px solid #a6c6c3;font-size:.8rem;color:#4c696e;padding-bottom:8px;margin-bottom:24px}.dose-row{margin:0 0 26px}.dose-row-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-end;margin-bottom:10px}.dose-name{font-size:1.05rem;font-weight:650;overflow-wrap:anywhere}.dose-value{font-weight:750;font-size:1.25rem;white-space:nowrap;color:#075d59}.dose-bar{height:40px;border-radius:0 8px 8px 0;background:var(--ingredient-accent,#147d85)}.dose-basis{font-size:.8rem;color:#46666b;margin-top:8px;overflow-wrap:anywhere}.dose-foot{font-size:.8rem;color:#48686d;margin-top:16px}.unknown-panel{border:1px dashed #9caeb3;background:repeating-linear-gradient(135deg,#f4f6f7,#f4f6f7 8px,#eef1f2 8px,#eef1f2 16px);border-radius:14px;padding:18px 20px;color:#41565d;margin:16px 0}.unknown-heading{font-weight:650;margin-bottom:10px}.unknown-chips{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0;margin:0}.unknown-chip{display:block;background:#fff;border:1px solid #c8d2d5;border-radius:6px;padding:5px 9px;margin:3px;font-size:.78rem;overflow-wrap:anywhere;max-width:100%}.unknown-note{font-size:.8rem;margin-top:10px}.unscaled-amount{border-left:3px solid #7c96a4;padding:8px 16px;margin:12px 0;color:#304e5a;overflow-wrap:anywhere}
.dose-axis{margin-left:164px;margin-bottom:10px}.dose-row{display:grid;grid-template-columns:144px minmax(0,1fr);gap:20px;align-items:center;padding:6px 0 10px;border-bottom:1px solid #e3e8ee;margin-bottom:4px}.dose-row:last-of-type{border-bottom:0}.dose-row-head{align-items:center}.dose-value{color:var(--ingredient-accent,#147d85);font-size:1.35rem}.dose-name{font-size:.98rem;letter-spacing:.02em}.dose-bar{height:26px;border-radius:0 6px 6px 0}.dose-basis{line-height:1.6;color:#647182}.molecule-tile{width:144px;text-align:center}.molecule-image,.molecule-placeholder{display:block!important;width:144px!important;height:101px!important;object-fit:contain!important;border:0!important;background:transparent!important;padding:0!important;box-shadow:none!important;border-radius:0!important}.molecule-placeholder{display:flex!important;align-items:center;justify-content:center;background:#f0f3f6!important;border:1px dashed #a6b0bd!important;border-radius:12px!important;color:#8a96a4;font-size:40px}.molecule-caption{font-size:.65rem;line-height:1.5;color:#697689;margin-top:6px;overflow-wrap:anywhere}.molecule-caption a{color:#526277;text-decoration:underline;text-underline-offset:2px}.molecule-caption span{font-size:.6rem}.dose-content{min-width:0}.dose-figure .dose-foot{color:#6b7583}.unknown-chip::before{content:"▧ ";color:#8995a4}
@media(max-width:600px){.dose-figure{padding:20px 14px}.dose-title{font-size:1.15rem;margin-bottom:16px}.dose-axis{font-size:.7rem;margin-left:112px;margin-bottom:12px}.dose-row{grid-template-columns:96px minmax(0,1fr);gap:16px;padding:12px 0 18px}.molecule-tile{width:96px}.molecule-image,.molecule-placeholder{width:96px!important;height:74px!important}.molecule-caption{font-size:.58rem}.dose-row-head{display:block}.dose-value{display:block;font-size:1.05rem;margin-top:6px;white-space:normal}.dose-name{font-size:.85rem}.dose-bar{height:24px}.dose-basis{font-size:.69rem;line-height:1.5}.composition-hero h1{font-size:1.5rem}.unknown-panel{padding:14px}}
</style>'''

def per_unit(product, group, ko=False):
    if group == 'mg / mL':
        return '1 mL당' if ko else 'per mL'
    denominator = group.split(' / ',1)[-1]
    if denominator != 'unit' and not denominator.endswith(' unit'):
        return denominator+'당' if ko else 'per '+denominator
    count = denominator[:-5] if denominator.endswith(' unit') else '1'
    if count != '1':
        return count+'투여 단위당' if ko else 'per '+count+' dosage units'
    form = product['form'].upper()
    if 'TABLET' in form:
        return '1정당' if ko else 'per tablet'
    if 'CAPSULE' in form:
        return '1캡슐당' if ko else 'per capsule'
    return '1투여 단위당' if ko else 'per dosage unit'

def fmt(value):
    if value != 0 and abs(value) < 0.000001:
        return f'{value:.6g}'  # Preserve small nonzero strengths instead of rounding to zero.
    return f'{value:,.6f}'.rstrip('0').rstrip('.')

def dose_visual_html(product, lang='en', basis='normalized'):
    ko = lang == 'ko'
    def tr(k,e): return k if ko else e
    active=[i for i in product['ingredients'] if i['active']]
    groups=chart_groups(active, basis)
    output=[]
    plotted=[]
    for unit, values in groups.items():
        denominator=per_unit(product,unit,ko)
        maximum=max(x['amount'] for x in values)
        title=tr('활성 성분 함량 · ','Active ingredient amounts · ')+denominator
        html='<figure class="dose-figure" aria-label="'+escape(title,quote=True)+'"><div class="dose-kicker">'+tr('레이블 기반 정량 시각화','LABEL-BACKED DOSE VISUALIZATION')+'</div><div class="dose-title">'+escape(title)+'</div>'
        html+='<div class="dose-axis" aria-hidden="true"><span>0 mg</span><span>'+fmt(maximum/2)+' mg</span><span>'+fmt(maximum)+' mg</span></div>'
        for row in values:
            plotted.append((row['ingredient'],row['basis']))
            amount=(denominator+' '+fmt(row['amount'])+' mg') if ko else (fmt(row['amount'])+' mg '+denominator)
            width=row['amount']/maximum*100
            html+='<div class="dose-row" style="--ingredient-accent:'+accent(row)+'">'+structure_tile(row,lang)+'<div class="dose-content"><div class="dose-row-head"><span class="dose-name">'+escape(row['ingredient'])+'</span><span class="dose-value">'+escape(amount)+'</span></div><div class="dose-bar" style="width:'+f'{width:.6f}'+'%" aria-hidden="true"></div><div class="dose-basis">'+tr('강도 기준: ','Strength basis: ')+escape(row['basis'])+' · '+tr('원문: ','Label: ')+escape(row['original_strength'] or '')+'</div></div></div>'
        if len(values)==1:
            note=tr('축의 끝은 이 레이블 함량입니다. 최대 복용량이나 제품 총질량을 뜻하지 않습니다.','Axis ends at this declared amount. It is not a maximum dose or total product mass.')
        else:
            note=tr('막대 길이는 표시된 질량에 비례합니다. 축은 가장 큰 표시 함량에서 끝납니다.','Bar lengths are proportional to declared mass. Axis ends at the largest displayed amount.')
        html+='<figcaption class="dose-foot">'+note+'<br>'+tr('구조 이미지는 같은 크기로 표시합니다. 색은 성분 구분용이며 효능·위험도를 뜻하지 않습니다.','Structure images use equal display boxes. Accent colors identify ingredients, not potency or risk.')+'</figcaption></figure>'
        output.append(html)
    for i in active:
        if (i['name'],i['basis']) not in plotted:
            output.append('<div class="unscaled-amount">'+structure_tile(i,lang)+'<b>'+escape(i['name'])+'</b> · '+escape(strength(i) or tr('함량 미공개','Amount not disclosed'))+'<br><small>'+tr('호환되는 단위 또는 강도 기준이 없어 비례 그래프를 표시하지 않습니다.','No proportional bar: compatible units or strength basis unavailable.')+'</small></div>')
    return ''.join(output)

def excipient_visual_html(product,lang='en',narrative=None):
    ko=lang=='ko'
    def tr(k,e):return k if ko else e
    inactive=inactive_evidence(product,narrative or [])
    unknown=[i for i in inactive if strength(i) is None]
    disclosed=[i for i in inactive if strength(i) is not None]
    html=''
    if unknown:
        html='<aside class="unknown-panel"><div class="unknown-heading">'+tr('첨가제 · 함량 미공개','Excipients · quantities not disclosed')+'</div>'
        html+='<ul class="unknown-chips">'+''.join('<li class="unknown-chip">'+escape(i['name']+(' · '+tr('조건부','conditional') if i.get('presence')=='conditional' else '')+(' · '+tr('원문 구절','narrative phrase') if i.get('origin')=='narrative-only' else ''))+'</li>' for i in unknown)+'</ul>'
        html+='<div class="unknown-note">'+tr('빗금은 미공개 데이터입니다. 0 또는 함량 비율을 뜻하지 않습니다. 원문 구절은 구조화된 항목과 겹칠 수 있습니다.','Hatching indicates missing quantity data, not zero or a composition share. Narrative phrases may overlap structured entries.')+'</div></aside>'
    if disclosed:
        html+='<div class="unscaled-amount">'+tr('공개된 첨가제 함량: ','Disclosed excipient amounts: ')+escape('; '.join(i['name']+' '+strength(i) for i in disclosed))+'</div>'
    if not inactive:
        html='<div class="unknown-panel">'+tr('이 구조화된 항목에는 첨가제 목록이 없습니다.','No inactive ingredient list in this structured entry.')+'</div>'
    return html

# Only composition-specific classes are styled; the legacy safety workspace is untouched.
STYLE += """<style>
.composition-hero{padding:22px 0 24px;border-bottom:1px solid #d4e0e7;color:#152f40}.composition-hero small{font-size:.65rem;letter-spacing:.16em;font-weight:700;color:#526574}.composition-hero h1{font-size:2.2rem;letter-spacing:-.055em;line-height:1.15;margin:10px 0}.composition-hero p{font-size:.88rem;color:#526574}.dose-figure{background:#fff;border-color:#d4e0e7;border-radius:24px;box-shadow:0 9px 28px #153e4406}.dose-title{color:#17384a;letter-spacing:-.03em}.dose-bar{border-radius:0 8px 8px 0}.dose-value{font-variant-numeric:tabular-nums}.unknown-panel{border-color:#b6c9d2;border-radius:18px}.unknown-chip{border-color:#cfdae1;border-radius:8px}.unknown-heading{letter-spacing:-.02em}@media(max-width:600px){.composition-hero h1{font-size:1.7rem}.composition-hero{padding:14px 0 20px}}
</style>"""
