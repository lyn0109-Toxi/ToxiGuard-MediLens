"""Composition workspace kept independent of existing safety heuristics."""
import json
import streamlit as st
from composition import SourceError, search_labels, load_label, strength
from composition_visuals import STYLE, dose_visual_html, excipient_visual_html
from molecular_assets import structure_evidence

@st.cache_data(ttl=3600, show_spinner=False)
def search(name, org, role, page):
    return search_labels(name, org, role, page)

@st.cache_data(ttl=3600, show_spinner=False)
def label(setid):
    return load_label(setid)

def render_composition(lang):
    ko = lang == 'ko'
    def tr(k, e): return k if ko else e
    st.markdown(STYLE, unsafe_allow_html=True)
    st.markdown('<div class="composition-hero"><small>MEDILENS / COMPOSITION</small><h1>' + tr('성분 함량을 한눈에', 'Ingredient amounts, visualized') + '</h1><p>' + tr('정확한 제품 선택 → 레이블 함량 시각화', 'Choose the exact product → see its declared amounts') + '</p></div>', unsafe_allow_html=True)
    country = st.radio(tr('국가', 'Country'), ['US', 'KR'], horizontal=True, format_func=lambda x: tr('미국', 'United States') if x == 'US' else tr('대한민국', 'South Korea'))
    if country == 'KR':
        st.info(tr('MFDS 제품정보 API가 연결되지 않았습니다. 한국 제품의 함량을 표시할 수 없습니다.', 'MFDS product API is not connected. Korean product composition is unavailable.'))
        st.link_button(tr('의약품안전나라 열기', 'Open MFDS product portal'), 'https://nedrug.mfds.go.kr/')
        return
    with st.form('composition-search'):
        a,b,c = st.columns([2,2,1])
        name = a.text_input(tr('제품명 또는 일반명', 'Product or generic name'), placeholder='acetaminophen')
        org = b.text_input(tr('회사명 (선택)', 'Organization (optional)'))
        role = c.selectbox(tr('회사 역할', 'Organization role'), ['manufacturer','labeler'], format_func=lambda x: tr('제조사','Manufacturer') if x == 'manufacturer' else tr('레이블러','Labeler'))
        page = st.number_input(tr('검색 결과 페이지', 'Results page'), min_value=1, max_value=999, value=1, step=1)
        submitted = st.form_submit_button(tr('공식 레이블 검색', 'Search official labels'), type='primary')
    if submitted:
        st.session_state.pop('composition_results', None)
        try:
            with st.spinner(tr('DailyMed 검색 중…','Searching DailyMed…')):
                result = search(name, org, role, page)
            st.session_state.composition_results = result
        except ValueError:
            st.warning(tr('두 글자 이상 입력하세요.', 'Enter at least two characters.'))
        except SourceError:
            st.error(tr('DailyMed에 연결할 수 없습니다. 잠시 후 다시 시도하세요.', 'DailyMed is unavailable. Please retry later.'))
    result = st.session_state.get('composition_results')
    if not result:
        st.info(tr('이름을 입력하고 공식 레이블을 선택하세요. 자동으로 제품을 추정하지 않습니다.', 'Search a name, then choose the exact label and product.'))
        return
    rows = result['data']
    if not rows:
        st.warning(tr('일치하는 레이블이 없습니다. 이름·회사 역할을 확인하세요.', 'No matching labels. Check the name and organization role.'))
        return
    st.caption(tr('전체 결과 수: ', 'Total matching labels: ') + str(result['metadata'].get('total_elements','?')) + tr(' · 다른 결과는 페이지를 변경하여 검색하세요.', ' · Change the results page to see more.'))
    selected = st.selectbox(tr('1 · 정확한 레이블 선택', '1 · Choose the exact label'), range(len(rows)), index=None, placeholder=tr('레이블 선택','Choose a label'), format_func=lambda j: rows[j]['title'] + ' · ' + rows[j]['setid'][:8], key='composition_label_' + result['url'])
    if selected is None: return
    try:
        with st.spinner(tr('SPL 원문 읽는 중…','Reading original SPL…')):
            record = label(rows[selected]['setid'])
    except (SourceError, ValueError):
        st.error(tr('이 레이블을 불러올 수 없습니다. 다른 제품을 추정하지 않습니다.', 'This label could not be loaded. No substitute composition is shown.'))
        return
    products = record['products']
    if not products:
        st.warning(tr('구조화된 함량 정보가 없습니다. 원문 레이블을 확인하세요.', 'No structured composition available. Review the original label.'))
    def summary(j):
        p = products[j]
        amounts = '; '.join(strength(i) or tr('미공개','Not disclosed') for i in p['ingredients'] if i['active'])
        return f"{p['name']} · {p['form']} · {amounts} · NDC {p['ndc'] or '—'}"
    idx = st.selectbox(tr('2 · 제품 · 함량 · 제형 선택', '2 · Choose product · strength · dosage form'), range(len(products)), index=None, placeholder=tr('정확한 제품 선택','Choose the exact product'), format_func=summary, key='composition_product_' + record['setid']) if products else None
    source = 'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=' + record['setid']
    if idx is None:
        st.link_button(tr('DailyMed 원문 레이블', 'Original DailyMed label'), source)
        return
    p = products[idx]
    releases = {'extended':tr('서방형','Extended release'), 'delayed':tr('지연방출형','Delayed release'), 'immediate':tr('속방형','Immediate release'), 'unspecified':tr('방출 유형 미명시','Release not specified')}
    st.subheader(p['name'])
    st.caption(p['form'] + ' · ' + releases[p['release']] + ' · NDC ' + (p['ndc'] or '—'))
    if not any(i['active'] for i in p['ingredients']):
        st.warning(tr('활성 성분 정보가 없습니다.', 'Active ingredient information unavailable.'))
    st.markdown(dose_visual_html(p, lang), unsafe_allow_html=True)
    st.markdown(excipient_visual_html(p, lang), unsafe_allow_html=True)
    st.caption(tr('성분 함량은 효능·안전성·치료적 동등성을 뜻하지 않습니다. DailyMed 등재가 FDA 승인을 뜻하지 않습니다.', 'Amounts do not indicate potency, safety or therapeutic equivalence. DailyMed listing does not imply FDA approval.'))
    with st.expander(tr('첨가제 및 원문 근거', 'Inactive ingredients & original evidence')):
        for i in p['ingredients']:
            st.write(i['name'] + ' — ' + (strength(i) or tr('함량 미공개','Amount not disclosed')))
            if i['active']:
                st.caption(tr('활성 부분: ','Active moiety: ') + ('; '.join(i['active_moieties']) or tr('미공개','Not disclosed')) + ' · SPL ' + i['class_code'])
            st.code(i['original_xml'], language='xml')
        st.caption(tr('미공개 함량은 0이 아닙니다. IID 최대 역가로 추정하지 않습니다. 총질량을 알 수 없어 원형 차트를 사용하지 않습니다.', 'Undisclosed amounts are not zero. IID maximum potency is not used to infer amounts. No total composition pie chart is shown.'))
        for section in record['sections']:
            if any(word in section['title'].lower() for word in ('ingredient','description','active')):
                st.write(section['title']); st.text(section['text'])
    with st.expander(tr('분자 구조 · 식별자 · 출처', 'Molecular structures · identity · sources')):
        st.caption(tr('검증된 구조 데이터로 직접 렌더링한 2D PNG입니다. 이름과 UNII가 모두 일치하는 성분만 표시합니다.','2D PNGs rendered deterministically from verified structure data. Both name and UNII must match.'))
        st.json(structure_evidence(p['ingredients']))
        st.markdown('[NCBI molecular-data policy](https://www.ncbi.nlm.nih.gov/home/about/policies/#data) · [RDKit BSD license](https://github.com/rdkit/rdkit/blob/master/license.txt)')
    with st.expander(tr('제품 정보 · 출처 · 다운로드', 'Product details · provenance · download')):
        st.write(p['generic'] + ' · ' + p['form'] + ' · ' + releases[p['release']])
        st.caption(tr('제조사: ', 'Manufacturer: ') + (p['manufacturer'] or tr('이 구조화된 제품 항목에 미공개','Not disclosed in this structured product entry')))
        st.caption(tr('레이블러: ', 'Labeler: ') + (p['labeler'] or tr('미공개','Not disclosed')))
        st.caption(tr('레이블러는 제조사와 다를 수 있습니다. 방출 유형은 구조화된 제형에서만 읽습니다.', 'Labeler may differ from manufacturer. Release classification uses the structured dosage form only.'))
        st.caption(tr('성분명·제형·원문은 원어로 표시합니다.', 'Ingredient names, dosage forms and source text remain in the source language.'))
        st.link_button(tr('DailyMed 원문 레이블', 'Original DailyMed label'), source)
        st.write({'SPL set ID':record['setid'], 'SPL version':record['version'], 'Label effective date':record['effective_date'], 'Retrieved (UTC)':record['retrieved_at']})
        st.link_button(tr('SPL XML 원문', 'Original SPL XML'), record['source_url'])
        st.download_button(tr('근거 JSON 다운로드','Download evidence JSON'), json.dumps({**record,'molecular_structure_evidence':structure_evidence(p['ingredients'])},ensure_ascii=False,indent=2), file_name='medilens-composition.json', mime='application/json')
