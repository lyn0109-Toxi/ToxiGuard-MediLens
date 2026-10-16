"""Accessible ingredient explorer. Source strings are rendered as text, never HTML."""
from pathlib import Path
import streamlit as st
from composition import chart_groups, strength
from composition_visuals import fmt, per_unit
from ingredient_evidence import inactive_evidence
from molecular_assets import lookup_structure
ROOT=Path(__file__).parent/'ingredient_map_assets'
def component():
    # Registration is idempotent and must occur in each isolated Streamlit runtime.
    return st.components.v2.component('medilens_ingredient_map',html='<section id="ingredient-map"></section>',css=(ROOT/'map.css').read_text(),js=(ROOT/'map.js').read_text())

def map_data(product,record,lang='en',basis='label'):
    ko=lang=='ko'
    def tr(k,e):return k if ko else e
    amounts={}
    for group,rows in chart_groups(product['ingredients'],basis).items():
        for row in rows:
            amounts[(row['ingredient'],row['unii'],row['original_strength'])]=fmt(row['amount'])+' mg · '+per_unit(product,group,ko)
    ingredients=[{**i,'origin':'structured','presence':'listed','narrative':[]} for i in product['ingredients'] if i['active']]+inactive_evidence(product,record.get('inactive_narrative',[]))
    nodes=[]
    for j,i in enumerate(ingredients):
        entry=lookup_structure(i)
        amount=amounts.get((i['name'],i.get('unii'),strength(i))) if i['active'] else None
        status=tr('조건부 · 원문 확인','Conditional · see narrative') if i['presence']=='conditional' else tr('원문 구절 · 별도 성분 수 아님','Narrative phrase · may overlap structured items') if i['origin']=='narrative-only' else tr('구조화된 레이블 항목','Structured label entry')
        nodes.append({'id':str(j),'name':i['name'],'active':i['active'],'amount':amount or strength(i) or tr('함량 미공개','Amount not disclosed'),'original':strength(i) or tr('함량 미공개','Amount not disclosed'),'basis':i.get('basis') or tr('미공개','Not disclosed'),'moiety':'; '.join(i.get('active_moieties',[])) or tr('미공개','Not disclosed'),'unii':i.get('unii') or '—','status':status,'narrative':i.get('narrative',[]),'image':entry['data_uri'] if entry else None,'entity':entry['entity'] if entry else None,'cid':entry['CID'] if entry else None,'structure_url':entry['source_url'] if entry else None})
    return {'lang':lang,'name':product['name'],'form':product['form'],'nodes':nodes,'source':'https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid='+record['setid'],'retrieved':record['retrieved_at'],'version':record['version'],'ndc':product.get('ndc') or '—'}

def render_map(product,record,lang='en',basis='label'):
    component()(data=map_data(product,record,lang,basis),key='ingredient-map-'+record['setid']+'-'+str(product.get('ndc')),height='content')
