"""Offline public-fixture layout review; runs the production composition renderer."""
from pathlib import Path
import sys
from unittest.mock import patch
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from composition import parse_spl
from composition_ui import render_composition
st.set_page_config(page_title='MediLens · public-label layout QA',layout='wide',initial_sidebar_state='collapsed')
st.caption('PUBLIC LABEL FIXTURES · LAYOUT QA · downloaded 2026-10-16 · not a live source response')
a,b=st.columns([2,1])
example=a.selectbox('Public example',['excedrin','acetaminophen','liquid','metoprolol-er','mucinex-solution','fexofenadine','artificial-tears'],index={'excedrin':0,'acetaminophen':1,'liquid':2,'metoprolol-er':3,'mucinex-solution':4,'fexofenadine':5,'artificial-tears':6}.get(st.query_params.get('example'),0),format_func=lambda x:{'excedrin':'Combination tablet · 250 / 250 / 65 mg','acetaminophen':'Single tablet · 500 mg','liquid':'Liquid · 160 mg / 5 mL','metoprolol-er':'Salt identity · verified structure unavailable','mucinex-solution':'Mucinex solution · four actives per 20 mL','fexofenadine':'Fexofenadine · actual fruit-juice advice','artificial-tears':'Eye drops · no food advice in label'}[x])
lang=b.selectbox('Language',['en','ko'],index=1 if st.query_params.get('lang')=='ko' else 0)
raw=(ROOT/'tests'/'fixtures'/(example+'.xml')).read_bytes()
record=parse_spl(raw,retrieved_at='2026-10-16 · public fixture, not a live response')
record['source_url']='https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/'+record['setid']+'.xml'
url='fixture:'+example
st.session_state['composition_results']={'data':[{'setid':record['setid'],'title':record['title']}],'metadata':{'total_elements':1},'url':url}
st.session_state['composition_label_'+url]=0
product_key='composition_product_'+record['setid']
if product_key not in st.session_state:st.session_state[product_key]=0
with patch('composition_ui.label',return_value=record):
    render_composition(lang)
