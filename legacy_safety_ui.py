"""Presentation-only adapter for the legacy safety overview; no clinical inference."""
import base64
from pathlib import Path
import streamlit as st

ROOT=Path(__file__).resolve().parent
# These are decorative asset substitutions, never evidence classifications.
ICON_GROUPS={
    'food':{'alcohol','cheese','coffee','fruit_juice','grapefruit','leafy_greens','milk'},
    'interactions':{'med_interaction','antacid','prescription'},
    'adverse':{'allergy','bleeding','blood_pressure','digestive','headache','liver','muscle','stomach_bleeding'},
    'directions':{'age','dose','duration'},
    'precautions':{'driving','pregnancy','review','sun'},
}

def render_legacy_icon(original_path):
    name=Path(original_path).stem
    category=next((key for key,names in ICON_GROUPS.items() if name in names),'precautions')
    svg=base64.b64encode((ROOT/'assets/safety'/(category+'.svg')).read_bytes()).decode()
    st.markdown('<div class="legacy-safety-icon legacy-icon-'+category+'" aria-hidden="true"><img alt="" src="data:image/svg+xml;base64,'+svg+'"></div>',unsafe_allow_html=True)

def install_legacy_style():
    st.markdown('<style>'+(ROOT/'legacy_safety.css').read_text()+'</style>',unsafe_allow_html=True)
