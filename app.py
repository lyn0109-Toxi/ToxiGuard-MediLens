from __future__ import annotations

import json
import ssl
import urllib.parse
import urllib.request
from typing import Any

import certifi
import streamlit as st


st.set_page_config(
    page_title="ToxiGuard-MediLens",
    page_icon="TG",
    layout="wide",
    initial_sidebar_state="expanded",
)


UI = {
    "ko": {
        "language": "언어",
        "search": "약 이름",
        "search_help": "브랜드명, 성분명, 한국어 별칭으로 검색할 수 있습니다.",
        "context": "내 상황",
        "sources": "공식 데이터 기준",
        "source_note": "모든 조언은 Advice -> Evidence -> Source 흐름으로 추적됩니다.",
        "top_eyebrow": "Medication safety snapshot",
        "top_title": "복용 전 10초 체크",
        "top_copy": "긴 레이블을 음식, 환경, 부작용, 근거 중심으로 다시 정리합니다.",
        "active_ingredient": "활성 성분",
        "concept": "표준 개념",
        "product": "제품",
        "precheck": "복용 전 확인",
        "evidence_flow": "근거 흐름",
        "side_effects": "부작용 비주얼",
        "avoid": "피하거나 확인할 음식/조건",
        "evidence": "근거",
        "advice": "조언",
        "source": "출처",
        "common": "흔함",
        "caution_tab": "주의",
        "urgent_tab": "위험 신호",
        "view_source": "원문 보기",
        "based_on": "기준",
        "label_verified": "레이블 확인됨",
        "search_results": "검색 결과",
        "sample_result": "샘플 데이터",
        "official_result": "공식 소스 조회 결과",
        "try_openfda": "공식 레이블 조회",
        "openfda_button": "공식 소스 조회",
        "openfda_hint": "브랜드명/성분명/활성성분을 openFDA Drug Label에서 순차 검색합니다.",
        "official_searching": "공식 소스에서 약 정보를 찾는 중입니다.",
        "refresh_official": "공식 소스 다시 조회",
        "no_query": "검색어를 입력하세요.",
        "lookup_failed": "openFDA 조회에 실패했습니다. 샘플 약으로 먼저 확인해 주세요.",
        "lookup_empty": "공식 레이블 결과를 찾지 못했습니다.",
        "external_loaded": "공식 레이블 결과를 사용 중입니다.",
        "search_not_found": "샘플과 공식 소스에서 결과를 찾지 못했습니다. 영문 성분명 또는 브랜드명으로 다시 검색해 주세요.",
        "source_lookup_caption": "샘플에 없는 약은 FDA 레이블 기반 결과를 자동으로 시도합니다.",
        "disclaimer": "이 앱은 공식 레이블을 쉽게 읽도록 돕는 프로토타입이며, 진단/처방/응급 판단을 대신하지 않습니다.",
        "risk_low": "낮은 주의",
        "risk_mid": "주의 필요",
        "risk_high": "피해야 할 항목 있음",
        "risk_urgent": "위험 신호 포함",
        "overview_title": "한눈에 보는 안전 결과",
        "overview_copy": "복용 전 체크, 피하거나 확인할 항목, 근거 연결 상태를 시각적으로 요약합니다.",
        "risk_meter": "위험도 미터",
        "precheck_count": "복용 전 체크",
        "avoid_count": "피하기/확인",
        "evidence_count": "근거 링크",
        "context_match": "내 상황 관련",
        "severity_distribution": "위험 신호 분포",
        "source_coverage": "조언-근거 연결",
        "context_none": "상황을 선택하면 관련 경고가 더 강하게 표시됩니다.",
        "context_selected": "선택한 상황",
        "items": "개",
    },
    "en": {
        "language": "Language",
        "search": "Medication name",
        "search_help": "Search by brand, generic name, or Korean alias.",
        "context": "My context",
        "sources": "Official data basis",
        "source_note": "Every recommendation is traceable through Advice -> Evidence -> Source.",
        "top_eyebrow": "Medication safety snapshot",
        "top_title": "10-second pre-dose check",
        "top_copy": "Long labels are reorganized around food, environment, side effects, and evidence.",
        "active_ingredient": "Active ingredient",
        "concept": "Standard concept",
        "product": "Product",
        "precheck": "Before you take it",
        "evidence_flow": "Evidence flow",
        "side_effects": "Side-effect view",
        "avoid": "Foods / conditions to avoid or check",
        "evidence": "Evidence",
        "advice": "Advice",
        "source": "Source",
        "common": "Common",
        "caution_tab": "Caution",
        "urgent_tab": "Red flags",
        "view_source": "View source",
        "based_on": "based on",
        "label_verified": "Label verified",
        "search_results": "Search results",
        "sample_result": "Sample data",
        "official_result": "Official source result",
        "try_openfda": "Official label lookup",
        "openfda_button": "Search official sources",
        "openfda_hint": "Searches openFDA Drug Label by brand, generic, active ingredient, and product text.",
        "official_searching": "Searching official sources for this medication.",
        "refresh_official": "Refresh official source",
        "no_query": "Enter a search term.",
        "lookup_failed": "openFDA lookup failed. Try a sample medication first.",
        "lookup_empty": "No official label result found.",
        "external_loaded": "Using the official label result.",
        "search_not_found": "No result found in samples or official sources. Try an English generic or brand name.",
        "source_lookup_caption": "Medications outside the samples are automatically checked against FDA label data.",
        "disclaimer": "This prototype helps make official labels easier to read. It does not replace diagnosis, prescribing, or emergency judgment.",
        "risk_low": "Low attention",
        "risk_mid": "Caution needed",
        "risk_high": "Avoidance item found",
        "risk_urgent": "Red flag included",
        "overview_title": "Visual safety overview",
        "overview_copy": "A quick visual summary of pre-dose checks, avoid/check items, and evidence coverage.",
        "risk_meter": "Risk meter",
        "precheck_count": "Pre-dose checks",
        "avoid_count": "Avoid/check",
        "evidence_count": "Evidence links",
        "context_match": "Context-related",
        "severity_distribution": "Signal distribution",
        "source_coverage": "Advice-evidence links",
        "context_none": "Choose your context to highlight relevant warnings.",
        "context_selected": "Selected context",
        "items": "items",
    },
}


CONTEXTS = [
    {
        "id": "alcohol",
        "label": {"ko": "술/음주 예정", "en": "Alcohol planned"},
        "note": {"ko": "알코올 관련 경고 우선 표시", "en": "Prioritize alcohol-related warnings"},
    },
    {
        "id": "driving",
        "label": {"ko": "운전/기계 조작", "en": "Driving / machinery"},
        "note": {"ko": "졸림, 어지러움 조언 강조", "en": "Highlight drowsiness and dizziness advice"},
    },
    {
        "id": "pregnancy",
        "label": {"ko": "임신/수유", "en": "Pregnancy / breastfeeding"},
        "note": {"ko": "전문가 확인 필요 항목 표시", "en": "Show items needing professional review"},
    },
    {
        "id": "sun",
        "label": {"ko": "햇빛 노출 많음", "en": "High sun exposure"},
        "note": {"ko": "광과민성 관련 조건 확인", "en": "Check photosensitivity-related conditions"},
    },
    {
        "id": "supplements",
        "label": {"ko": "영양제/제산제 복용", "en": "Supplements / antacids"},
        "note": {"ko": "칼슘, 철분, 마그네슘 간격 확인", "en": "Check calcium, iron, and magnesium spacing"},
    },
    {
        "id": "other_meds",
        "label": {"ko": "다른 약 함께 복용", "en": "Taking other medicines"},
        "note": {"ko": "상호작용 가능성 우선 확인", "en": "Prioritize possible interactions"},
    },
]


SEVERITY = {
    "info": {"ko": "정보", "en": "Info", "score": 1, "class": "info"},
    "caution": {"ko": "주의", "en": "Caution", "score": 2, "class": "caution"},
    "avoid": {"ko": "피하기", "en": "Avoid", "score": 3, "class": "avoid"},
    "urgent": {"ko": "위험 신호", "en": "Red flag", "score": 4, "class": "urgent"},
}

SEVERITY_ICONS = {
    "info": ":material/info:",
    "caution": ":material/report:",
    "avoid": ":material/block:",
    "urgent": ":material/emergency_home:",
}

SEVERITY_COLORS = {
    "info": "blue",
    "caution": "orange",
    "avoid": "red",
    "urgent": "red",
}


SOURCE_LINKS = {
    "rxnorm": "https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html",
    "openfda": "https://open.fda.gov/apis/drug/label/",
    "dailymed": "https://dailymed.nlm.nih.gov/dailymed/webservices-help/v2/spls_api.cfm",
    "grapefruit": "https://www.fda.gov/consumers/consumer-updates/grapefruit-juice-and-some-drugs-dont-mix",
    "nsaid_pregnancy": "https://www.fda.gov/drugs/drug-safety-and-availability/fda-recommends-avoiding-use-nsaids-pregnancy-20-weeks-or-later-because-they-can-result-low-amniotic",
}

OPENFDA_SEARCH_FIELDS = [
    "openfda.brand_name",
    "openfda.generic_name",
    "openfda.substance_name",
    "active_ingredient",
    "spl_product_data_elements",
]

HTTPS_CONTEXT = ssl.create_default_context(cafile=certifi.where())

QUERY_ALIASES = {
    "아스피린": "aspirin",
    "타이레놀": "tylenol",
    "아세트아미노펜": "acetaminophen",
    "메트포르민": "metformin",
    "메트포민": "metformin",
    "심바스타틴": "simvastatin",
    "와파린": "warfarin",
    "알레그라": "allegra",
    "펙소페나딘": "fexofenadine",
    "이부프로펜": "ibuprofen",
}


def official_query(query: str) -> str:
    cleaned = query.strip()
    return QUERY_ALIASES.get(normalize(cleaned), cleaned)


SAMPLE_DRUGS = [
    {
        "id": "simvastatin",
        "name": "Simvastatin",
        "aliases": ["zocor", "simvastatin", "심바스타틴", "스타틴"],
        "active": "simvastatin",
        "concept": {"ko": "RxCUI 후보: 36567", "en": "RxCUI candidate: 36567"},
        "product": "Tablet, oral",
        "status": {"ko": "샘플 레이블", "en": "Sample label"},
        "label_date": {"ko": "DailyMed/openFDA 레이블 기반", "en": "Based on DailyMed/openFDA labels"},
        "summary": {
            "ko": "콜레스테롤을 낮추는 스타틴 계열 약물입니다. 자몽, 알코올, 근육 증상, 병용 약물 확인이 핵심입니다.",
            "en": "A statin used to lower cholesterol. Key checks include grapefruit, alcohol, muscle symptoms, and interacting medicines.",
        },
        "prechecks": [
            {
                "title": {"ko": "자몽과 자몽주스 피하기", "en": "Avoid grapefruit and grapefruit juice"},
                "body": {
                    "ko": "자몽은 일부 스타틴의 체내 농도를 높여 근육 및 간 관련 부작용 위험을 키울 수 있습니다.",
                    "en": "Grapefruit can increase exposure to some statins and may raise muscle- and liver-related side-effect risk.",
                },
                "severity": "avoid",
                "context": [],
                "source": "simvastatin-grapefruit",
            },
            {
                "title": {"ko": "설명되지 않는 근육 통증은 즉시 확인", "en": "Check unexplained muscle pain promptly"},
                "body": {
                    "ko": "근육 통증, 힘 빠짐, 발열, 어두운 소변이 함께 나타나면 빠르게 의료진에게 연락하세요.",
                    "en": "Contact a clinician promptly if muscle pain or weakness occurs with fever or dark urine.",
                },
                "severity": "urgent",
                "context": [],
                "source": "simvastatin-muscle",
            },
            {
                "title": {"ko": "다른 항생제/항진균제 병용 확인", "en": "Check antibiotics and antifungals"},
                "body": {
                    "ko": "상호작용 약물이 있으면 혈중 농도가 올라갈 수 있어 약사 확인이 필요합니다.",
                    "en": "Interacting medicines may increase blood levels, so pharmacist review is important.",
                },
                "severity": "caution",
                "context": ["other_meds"],
                "source": "simvastatin-interactions",
            },
        ],
        "avoid": [
            {
                "title": {"ko": "자몽/자몽주스", "en": "Grapefruit / grapefruit juice"},
                "body": {"ko": "복용 기간 중 피해야 할 항목으로 우선 표시합니다.", "en": "Flagged as an item to avoid during treatment."},
                "severity": "avoid",
                "tags": ["food", "CYP3A4"],
            },
            {
                "title": {"ko": "과도한 음주", "en": "Heavy alcohol use"},
                "body": {"ko": "간 관련 위험을 키울 수 있어 음주 습관이 있으면 상담이 필요합니다.", "en": "Alcohol habits may increase liver-related risk and should be discussed."},
                "severity": "caution",
                "tags": ["condition", "liver"],
            },
        ],
        "side_effects": {
            "common": [
                ({"ko": "두통, 복부 불편감", "en": "Headache, abdominal discomfort"}, {"ko": "지속되면 상담", "en": "Discuss if persistent"}),
                ({"ko": "메스꺼움, 변비", "en": "Nausea, constipation"}, {"ko": "반복되면 약사에게 확인", "en": "Ask a pharmacist if repeated"}),
            ],
            "caution": [
                ({"ko": "간 관련 이상 신호", "en": "Possible liver-related warning signs"}, {"ko": "피로, 진한 소변, 황달 등", "en": "Fatigue, dark urine, jaundice, and similar signs"}),
            ],
            "urgent": [
                ({"ko": "심한 근육 통증/힘 빠짐", "en": "Severe muscle pain / weakness"}, {"ko": "발열 또는 어두운 소변과 함께 나타나면 즉시 도움", "en": "Seek help promptly if it occurs with fever or dark urine"}),
            ],
        },
        "evidence": [
            {
                "id": "simvastatin-grapefruit",
                "title": {"ko": "자몽 상호작용", "en": "Grapefruit interaction"},
                "quote": {"ko": "FDA는 일부 경구 약물에서 자몽 관련 경고가 필요하다고 설명합니다.", "en": "FDA notes that some oral medicines need grapefruit-related warnings."},
                "source": "FDA Consumer Update + Drug Interactions label section",
                "url": SOURCE_LINKS["grapefruit"],
            },
            {
                "id": "simvastatin-muscle",
                "title": {"ko": "근육 관련 위험 신호", "en": "Muscle-related red flags"},
                "quote": {"ko": "근병증, 횡문근융해증 경고는 스타틴 계열의 핵심 안전 정보입니다.", "en": "Warnings about myopathy and rhabdomyolysis are core statin safety information."},
                "source": "DailyMed/openFDA adverse reactions and warnings",
                "url": SOURCE_LINKS["openfda"],
            },
            {
                "id": "simvastatin-interactions",
                "title": {"ko": "약물 상호작용", "en": "Drug interactions"},
                "quote": {"ko": "일부 병용 약물은 농도 상승과 부작용 증가에 관여할 수 있습니다.", "en": "Some concomitant medicines may increase exposure and side effects."},
                "source": "Drug Interactions label section",
                "url": SOURCE_LINKS["openfda"],
            },
        ],
    },
    {
        "id": "warfarin",
        "name": "Warfarin",
        "aliases": ["coumadin", "jantoven", "warfarin", "와파린", "쿠마딘"],
        "active": "warfarin sodium",
        "concept": {"ko": "RxCUI 후보: 11289", "en": "RxCUI candidate: 11289"},
        "product": "Tablet, oral",
        "status": {"ko": "샘플 레이블", "en": "Sample label"},
        "label_date": {"ko": "DailyMed/openFDA 레이블 기반", "en": "Based on DailyMed/openFDA labels"},
        "summary": {
            "ko": "혈액 응고를 늦추는 항응고제입니다. 비타민 K 섭취 변화, 음주, 병용 약물, 출혈 신호가 핵심입니다.",
            "en": "An anticoagulant that slows blood clotting. Key checks include vitamin K diet changes, alcohol, other medicines, and bleeding signs.",
        },
        "prechecks": [
            {
                "title": {"ko": "비타민 K 많은 음식은 갑자기 바꾸지 않기", "en": "Do not suddenly change vitamin K-rich foods"},
                "body": {"ko": "케일, 시금치 같은 음식은 완전 금지보다 섭취 패턴을 일정하게 유지하는 것이 중요합니다.", "en": "For foods like kale and spinach, a consistent pattern matters more than complete avoidance."},
                "severity": "caution",
                "context": [],
                "source": "warfarin-vitamin-k",
            },
            {
                "title": {"ko": "술은 출혈 위험을 높일 수 있음", "en": "Alcohol may increase bleeding risk"},
                "body": {"ko": "음주량 변화는 INR과 출혈 위험에 영향을 줄 수 있어 의료진과 상의하세요.", "en": "Changes in alcohol intake may affect INR and bleeding risk, so discuss them with a clinician."},
                "severity": "avoid",
                "context": ["alcohol"],
                "source": "warfarin-alcohol",
            },
            {
                "title": {"ko": "멈추지 않는 출혈은 즉시 도움", "en": "Get immediate help for bleeding that does not stop"},
                "body": {"ko": "검은변, 피 섞인 소변, 심한 두통, 토혈, 멍 증가가 있으면 빠르게 도움을 받으세요.", "en": "Seek help quickly for black stools, blood in urine, severe headache, vomiting blood, or increasing bruising."},
                "severity": "urgent",
                "context": [],
                "source": "warfarin-bleeding",
            },
        ],
        "avoid": [
            {
                "title": {"ko": "비타민 K 섭취 급변", "en": "Sudden vitamin K intake change"},
                "body": {"ko": "녹색 잎채소를 갑자기 많이 늘리거나 줄이지 않는 방식으로 관리합니다.", "en": "Avoid sudden large increases or decreases in leafy green intake."},
                "severity": "caution",
                "tags": ["food", "vitamin K"],
            },
            {
                "title": {"ko": "이부프로펜/아스피린 등 임의 병용", "en": "Unreviewed ibuprofen/aspirin use"},
                "body": {"ko": "출혈 위험이 커질 수 있어 처방자 또는 약사 확인이 필요합니다.", "en": "Bleeding risk can increase, so prescriber or pharmacist review is needed."},
                "severity": "avoid",
                "tags": ["drug", "NSAID"],
            },
        ],
        "side_effects": {
            "common": [
                ({"ko": "쉽게 멍이 듦", "en": "Easy bruising"}, {"ko": "갑자기 심해지면 확인", "en": "Check if suddenly worsening"}),
                ({"ko": "가벼운 코피/잇몸 출혈", "en": "Mild nosebleeds / gum bleeding"}, {"ko": "반복되거나 오래가면 상담", "en": "Discuss if repeated or prolonged"}),
            ],
            "caution": [
                ({"ko": "INR 변동", "en": "INR fluctuation"}, {"ko": "음식, 술, 다른 약 변화와 함께 확인", "en": "Review along with food, alcohol, and medication changes"}),
            ],
            "urgent": [
                ({"ko": "멈추지 않는 출혈", "en": "Bleeding that does not stop"}, {"ko": "검은변, 토혈, 피 섞인 소변 포함", "en": "Includes black stools, vomiting blood, or blood in urine"}),
            ],
        },
        "evidence": [
            {
                "id": "warfarin-vitamin-k",
                "title": {"ko": "비타민 K와 식단 일관성", "en": "Vitamin K and diet consistency"},
                "quote": {"ko": "와파린 관리는 비타민 K 섭취량 변화와 INR 변동을 함께 봅니다.", "en": "Warfarin management considers vitamin K intake changes along with INR variation."},
                "source": "Warfarin label dietary guidance",
                "url": SOURCE_LINKS["dailymed"],
            },
            {
                "id": "warfarin-alcohol",
                "title": {"ko": "음주와 출혈 위험", "en": "Alcohol and bleeding risk"},
                "quote": {"ko": "알코올 섭취 변화는 항응고 효과와 출혈 위험에 영향을 줄 수 있습니다.", "en": "Changes in alcohol intake may affect anticoagulation and bleeding risk."},
                "source": "Warnings and precautions",
                "url": SOURCE_LINKS["openfda"],
            },
            {
                "id": "warfarin-bleeding",
                "title": {"ko": "출혈 위험 신호", "en": "Bleeding red flags"},
                "quote": {"ko": "출혈은 항응고제 레이블의 가장 우선순위 높은 안전 정보입니다.", "en": "Bleeding is among the highest-priority safety information in anticoagulant labels."},
                "source": "Boxed warning and adverse reactions",
                "url": SOURCE_LINKS["dailymed"],
            },
        ],
    },
    {
        "id": "fexofenadine",
        "name": "Fexofenadine",
        "aliases": ["allegra", "fexofenadine", "펙소페나딘", "알레그라"],
        "active": "fexofenadine hydrochloride",
        "concept": {"ko": "RxCUI 후보: 87636", "en": "RxCUI candidate: 87636"},
        "product": "Tablet or suspension, oral",
        "status": {"ko": "샘플 레이블", "en": "Sample label"},
        "label_date": {"ko": "FDA 소비자 안내/openFDA 레이블 기반", "en": "Based on FDA consumer guidance/openFDA labels"},
        "summary": {
            "ko": "알레르기 증상 완화에 쓰이는 항히스타민제입니다. 일부 과일주스와 제산제는 약효를 낮출 수 있습니다.",
            "en": "An antihistamine used for allergy relief. Some fruit juices and antacids can reduce effect.",
        },
        "prechecks": [
            {
                "title": {"ko": "자몽, 오렌지, 사과 주스와 함께 먹지 않기", "en": "Do not take with grapefruit, orange, or apple juice"},
                "body": {"ko": "일부 과일주스는 흡수를 낮춰 약이 덜 작동하게 만들 수 있습니다.", "en": "Some fruit juices can reduce absorption and make the medicine work less well."},
                "severity": "avoid",
                "context": [],
                "source": "fexofenadine-juice",
            },
            {
                "title": {"ko": "알루미늄/마그네슘 제산제와 간격 두기", "en": "Separate from aluminum/magnesium antacids"},
                "body": {"ko": "제산제는 흡수를 줄일 수 있어 복용 간격을 확인하세요.", "en": "Antacids can reduce absorption, so check dosing separation."},
                "severity": "caution",
                "context": ["supplements"],
                "source": "fexofenadine-antacid",
            },
        ],
        "avoid": [
            {
                "title": {"ko": "자몽/오렌지/사과 주스", "en": "Grapefruit / orange / apple juice"},
                "body": {"ko": "복용 전후 주스 섭취는 흡수 감소 가능성을 기준으로 표시합니다.", "en": "Juice around dosing is flagged because of possible reduced absorption."},
                "severity": "avoid",
                "tags": ["food", "transporters"],
            },
            {
                "title": {"ko": "알루미늄/마그네슘 제산제", "en": "Aluminum/magnesium antacids"},
                "body": {"ko": "동시 복용 대신 시간 간격을 둬야 할 수 있습니다.", "en": "You may need spacing instead of taking them together."},
                "severity": "caution",
                "tags": ["supplement", "antacid"],
            },
        ],
        "side_effects": {
            "common": [
                ({"ko": "두통", "en": "Headache"}, {"ko": "지속되면 상담", "en": "Discuss if persistent"}),
                ({"ko": "어지러움", "en": "Dizziness"}, {"ko": "운전 전 개인 반응 확인", "en": "Check your response before driving"}),
            ],
            "caution": [
                ({"ko": "약효 감소", "en": "Reduced effect"}, {"ko": "과일주스 또는 제산제와 함께 복용했는지 확인", "en": "Check whether it was taken with fruit juice or antacids"}),
            ],
            "urgent": [
                ({"ko": "심한 알레르기 반응", "en": "Severe allergic reaction"}, {"ko": "호흡곤란, 얼굴/입술 부종은 즉시 도움", "en": "Trouble breathing or face/lip swelling needs immediate help"}),
            ],
        },
        "evidence": [
            {
                "id": "fexofenadine-juice",
                "title": {"ko": "과일주스와 흡수 감소", "en": "Fruit juice and reduced absorption"},
                "quote": {"ko": "FDA는 fexofenadine이 자몽, 오렌지, 사과 주스와 함께 복용 시 효과가 낮아질 수 있다고 설명합니다.", "en": "FDA explains that fexofenadine may be less effective when taken with grapefruit, orange, or apple juice."},
                "source": "FDA Consumer Update",
                "url": SOURCE_LINKS["grapefruit"],
            },
            {
                "id": "fexofenadine-antacid",
                "title": {"ko": "제산제 간격", "en": "Antacid spacing"},
                "quote": {"ko": "알루미늄/마그네슘 제산제는 fexofenadine 흡수에 영향을 줄 수 있습니다.", "en": "Aluminum/magnesium antacids can affect fexofenadine absorption."},
                "source": "Drug interactions label section",
                "url": SOURCE_LINKS["openfda"],
            },
        ],
    },
    {
        "id": "ibuprofen",
        "name": "Ibuprofen",
        "aliases": ["advil", "motrin", "ibuprofen", "이부프로펜"],
        "active": "ibuprofen",
        "concept": {"ko": "RxCUI 후보: 5640", "en": "RxCUI candidate: 5640"},
        "product": "Tablet/capsule/suspension, oral",
        "status": {"ko": "샘플 레이블", "en": "Sample label"},
        "label_date": {"ko": "FDA/openFDA 레이블 기반", "en": "Based on FDA/openFDA labels"},
        "summary": {
            "ko": "통증, 염증, 발열에 쓰이는 NSAID입니다. 음주, 위장 출혈, NSAID 중복, 임신 20주 이후 사용 확인이 중요합니다.",
            "en": "An NSAID used for pain, inflammation, and fever. Key checks include alcohol, stomach bleeding, duplicate NSAIDs, and use after 20 weeks of pregnancy.",
        },
        "prechecks": [
            {
                "title": {"ko": "술과 함께 복용하지 않기", "en": "Do not take with alcohol"},
                "body": {"ko": "알코올은 위장 출혈 위험을 높일 수 있어 복용 기간 중 피하는 쪽이 안전합니다.", "en": "Alcohol can increase stomach bleeding risk, so avoiding it during use is safer."},
                "severity": "avoid",
                "context": ["alcohol"],
                "source": "ibuprofen-alcohol",
            },
            {
                "title": {"ko": "임신 20주 이후는 처방자 확인", "en": "After 20 weeks of pregnancy, check with the prescriber"},
                "body": {"ko": "FDA는 임신 20주 이후 NSAID 사용을 의료진 지시 없이 피하도록 권고합니다.", "en": "FDA recommends avoiding NSAID use after 20 weeks of pregnancy unless directed by a clinician."},
                "severity": "avoid",
                "context": ["pregnancy"],
                "source": "ibuprofen-pregnancy",
            },
            {
                "title": {"ko": "검은변, 토혈, 심한 복통은 즉시 도움", "en": "Black stools, vomiting blood, or severe abdominal pain need immediate help"},
                "body": {"ko": "위장 출혈 신호일 수 있어 빠르게 의료진의 도움을 받으세요.", "en": "These may signal stomach bleeding and require prompt medical help."},
                "severity": "urgent",
                "context": [],
                "source": "ibuprofen-bleeding",
            },
        ],
        "avoid": [
            {
                "title": {"ko": "알코올", "en": "Alcohol"},
                "body": {"ko": "위장 출혈 위험 증가 가능성을 기준으로 피해야 할 조건에 표시합니다.", "en": "Flagged because it may increase stomach bleeding risk."},
                "severity": "avoid",
                "tags": ["condition", "GI bleeding"],
            },
            {
                "title": {"ko": "NSAID 중복 복용", "en": "Duplicate NSAID use"},
                "body": {"ko": "약 이름이 달라도 같은 계열이면 위험이 누적될 수 있습니다.", "en": "Even with different names, risk can add up if the medicines are in the same class."},
                "severity": "avoid",
                "tags": ["drug", "duplicate therapy"],
            },
        ],
        "side_effects": {
            "common": [
                ({"ko": "속쓰림, 위 불편감", "en": "Heartburn, stomach discomfort"}, {"ko": "식사와 함께 복용 가능 여부 확인", "en": "Check whether taking with food is appropriate"}),
                ({"ko": "어지러움", "en": "Dizziness"}, {"ko": "운전 전 개인 반응 확인", "en": "Check your response before driving"}),
            ],
            "caution": [
                ({"ko": "혈압 상승 또는 부종", "en": "Blood pressure increase or swelling"}, {"ko": "기저질환이 있으면 확인", "en": "Review if underlying conditions are present"}),
            ],
            "urgent": [
                ({"ko": "검은변/토혈/심한 복통", "en": "Black stools / vomiting blood / severe abdominal pain"}, {"ko": "위장 출혈 가능성", "en": "Possible stomach bleeding"}),
            ],
        },
        "evidence": [
            {
                "id": "ibuprofen-alcohol",
                "title": {"ko": "알코올과 위장 출혈", "en": "Alcohol and stomach bleeding"},
                "quote": {"ko": "NSAID 레이블은 알코올, 위장 출혈, 궤양 위험을 주요 경고로 다룹니다.", "en": "NSAID labels treat alcohol, stomach bleeding, and ulcer risk as major warnings."},
                "source": "NSAID warnings",
                "url": SOURCE_LINKS["openfda"],
            },
            {
                "id": "ibuprofen-pregnancy",
                "title": {"ko": "임신 20주 이후 NSAID", "en": "NSAIDs after 20 weeks of pregnancy"},
                "quote": {"ko": "FDA는 임신 20주 이후 NSAID 사용을 의료진 지시 없이 피하도록 권고합니다.", "en": "FDA recommends avoiding NSAID use after 20 weeks of pregnancy unless directed by a clinician."},
                "source": "FDA Drug Safety Communication",
                "url": SOURCE_LINKS["nsaid_pregnancy"],
            },
            {
                "id": "ibuprofen-bleeding",
                "title": {"ko": "위장 출혈 위험 신호", "en": "Stomach bleeding red flags"},
                "quote": {"ko": "검은변, 토혈, 심한 복통은 즉시 확인해야 하는 신호입니다.", "en": "Black stools, vomiting blood, and severe abdominal pain need immediate review."},
                "source": "Warnings and adverse reactions",
                "url": SOURCE_LINKS["openfda"],
            },
        ],
    },
]


def css() -> None:
    st.html(
        """
        <style>
          :root {
            --ink: #172126;
            --muted: #61707c;
            --line: #dce4e9;
            --green: #12745f;
            --green-soft: #dff4ed;
            --blue: #2c67b0;
            --blue-soft: #e3eef9;
            --amber: #b96712;
            --amber-soft: #faebd8;
            --red: #c84c3e;
            --red-soft: #f9e1dd;
          }
          .stApp {
            background:
              linear-gradient(180deg, rgba(255,255,255,.74), rgba(245,248,247,.96)),
              linear-gradient(135deg, rgba(237,246,243,.74), rgba(244,248,250,.72));
            color: var(--ink);
          }
          section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(247,251,249,.94));
            border-right: 1px solid var(--line);
          }
          div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: var(--line);
            box-shadow: 0 10px 26px rgba(22,38,46,.05);
          }
          div[data-testid="stMetricValue"] {
            font-size: 18px;
          }
        </style>
        """
    )


def t(lang: str, key: str) -> str:
    return UI[lang][key]


def l(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("en") or value.get("ko") or "")
    return str(value)


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def match_drugs(query: str) -> list[dict[str, Any]]:
    q = normalize(query)
    if not q:
        return SAMPLE_DRUGS
    matches = []
    for drug in SAMPLE_DRUGS:
        haystack = " ".join([drug["name"], drug["active"], *drug["aliases"]]).lower()
        if q in haystack:
            matches.append(drug)
    return matches


def evidence_by_id(drug: dict[str, Any], evidence_id: str | None) -> dict[str, Any]:
    for item in drug.get("evidence", []):
        if item["id"] == evidence_id:
            return item
    return drug.get("evidence", [{}])[0]


def ranked_prechecks(drug: dict[str, Any], contexts: set[str]) -> list[dict[str, Any]]:
    cards = list(drug.get("prechecks", []))
    if "pregnancy" in contexts and not any("pregnancy" in item.get("context", []) for item in cards):
        cards.append(
            {
                "title": {"ko": "임신/수유 상황은 약사 또는 처방자 확인", "en": "Pregnancy / breastfeeding: check with pharmacist or prescriber"},
                "body": {
                    "ko": "공식 레이블에 명확한 음식 제한이 없어도 개인별 판단이 필요합니다.",
                    "en": "Even if the official label has no clear food restriction, individual review is needed.",
                },
                "severity": "caution",
                "context": ["pregnancy"],
                "source": drug.get("evidence", [{}])[0].get("id"),
            }
        )
    return sorted(
        cards,
        key=lambda item: SEVERITY[item["severity"]]["score"] * 10
        + (6 if set(item.get("context", [])) & contexts else 0),
        reverse=True,
    )


def risk_label(lang: str, cards: list[dict[str, Any]]) -> tuple[str, str]:
    top_score = max([SEVERITY[item["severity"]]["score"] for item in cards] or [1])
    if top_score >= 4:
        return "urgent", t(lang, "risk_urgent")
    if top_score >= 3:
        return "avoid", t(lang, "risk_high")
    if top_score >= 2:
        return "caution", t(lang, "risk_mid")
    return "info", t(lang, "risk_low")


def severity_counts(items: list[dict[str, Any]]) -> dict[str, int]:
    counts = {key: 0 for key in ["urgent", "avoid", "caution", "info"]}
    for item in items:
        severity = item.get("severity", "info")
        counts[severity if severity in counts else "info"] += 1
    return counts


def context_match_count(items: list[dict[str, Any]], contexts: set[str]) -> int:
    if not contexts:
        return 0
    return sum(1 for item in items if set(item.get("context", [])) & contexts)


def card(title: str, body: str, severity: str, lang: str, source: str | None = None, tags: list[str] | None = None) -> None:
    sev = SEVERITY[severity]
    badge_color = SEVERITY_COLORS.get(severity, "gray")

    with st.container(border=True):
        text_col, badge_col = st.columns([0.78, 0.22], vertical_alignment="top")
        with text_col:
            st.markdown(f"**{title}**")
            st.write(body)
            if source:
                st.caption(f"{t(lang, 'source')}: {source}")
            if tags:
                st.caption(" · ".join(tags))
        with badge_col:
            st.badge(l(sev, lang), icon=SEVERITY_ICONS.get(severity), color=badge_color)


def render_visual_overview(
    drug: dict[str, Any],
    cards: list[dict[str, Any]],
    risk_class: str,
    risk_text: str,
    contexts: set[str],
    lang: str,
) -> None:
    avoid_items = list(drug.get("avoid", []))
    evidence_items = list(drug.get("evidence", []))
    counts = severity_counts(cards + avoid_items)
    risk_ratio = SEVERITY[risk_class]["score"] / 4
    context_hits = context_match_count(cards, contexts)
    source_ratio = min(len(evidence_items) / max(len(cards), 1), 1.0)

    with st.container(border=True):
        head_col, badge_col = st.columns([0.72, 0.28], vertical_alignment="center")
        with head_col:
            st.badge(t(lang, "overview_title"), icon=":material/dashboard:", color="primary")
            st.caption(t(lang, "overview_copy"))
        with badge_col:
            st.badge(risk_text, icon=SEVERITY_ICONS.get(risk_class), color=SEVERITY_COLORS.get(risk_class, "gray"))

        meter_col, stats_col = st.columns([0.48, 0.52], gap="large", vertical_alignment="top")
        with meter_col:
            st.markdown(f"**{t(lang, 'risk_meter')}**")
            st.progress(risk_ratio, text=risk_text)
            st.caption(f"{t(lang, 'source_coverage')}: {len(evidence_items)} / {max(len(cards), 1)}")
            st.progress(source_ratio)

        with stats_col:
            metric_cols = st.columns(4)
            metric_data = [
                (t(lang, "precheck_count"), len(cards), ":material/fact_check:", "blue"),
                (t(lang, "avoid_count"), len(avoid_items), ":material/no_food:", "red"),
                (t(lang, "evidence_count"), len(evidence_items), ":material/source:", "green"),
                (t(lang, "context_match"), context_hits, ":material/person_check:", "orange" if context_hits else "gray"),
            ]
            for col, (label, value, icon, color) in zip(metric_cols, metric_data):
                with col.container(border=True):
                    st.badge(label, icon=icon, color=color)
                    st.markdown(f"### {value}")

        st.markdown(f"**{t(lang, 'severity_distribution')}**")
        dist_cols = st.columns(4)
        max_count = max(counts.values()) or 1
        for col, severity in zip(dist_cols, ["urgent", "avoid", "caution", "info"]):
            with col.container(border=True):
                st.badge(
                    l(SEVERITY[severity], lang),
                    icon=SEVERITY_ICONS[severity],
                    color=SEVERITY_COLORS.get(severity, "gray"),
                )
                st.progress(counts[severity] / max_count, text=f"{counts[severity]} {t(lang, 'items')}")

        if contexts:
            selected_labels = [l(context["label"], lang) for context in CONTEXTS if context["id"] in contexts]
            st.caption(f"{t(lang, 'context_selected')}: " + " · ".join(selected_labels))
        else:
            st.caption(t(lang, "context_none"))


def render_brand(lang: str) -> None:
    with st.sidebar.container(border=True):
        st.markdown("## ToxiGuard\n## MediLens")
        st.caption(t(lang, "top_copy"))
        st.badge("FDA label", icon=":material/verified:", color="green")
        st.badge("RxNorm concept", icon=":material/hub:", color="blue")
        st.badge("SPL source", icon=":material/source:", color="gray")


def render_drug_header(drug: dict[str, Any], lang: str) -> None:
    with st.container(border=True):
        status_col, date_col = st.columns([0.32, 0.68], vertical_alignment="center")
        status_col.badge(l(drug.get("status"), lang), icon=":material/verified_user:", color="green")
        date_col.caption(l(drug.get("label_date"), lang))
        st.markdown(f"# {drug['name']}")
        st.write(l(drug["summary"], lang))

    c1, c2, c3 = st.columns(3)
    metrics = [
        (c1, t(lang, "active_ingredient"), drug["active"]),
        (c2, t(lang, "concept"), l(drug["concept"], lang)),
        (c3, t(lang, "product"), drug["product"]),
    ]
    for col, label, value in metrics:
        with col.container(border=True):
            st.caption(label)
            st.markdown(f"**{value}**")


def render_evidence_flow(drug: dict[str, Any], cards: list[dict[str, Any]], lang: str) -> None:
    first = cards[0] if cards else {}
    evidence = evidence_by_id(drug, first.get("source"))
    with st.container(border=True):
        st.markdown(f"### {t(lang, 'evidence_flow')}")
        for label, value in [
            (t(lang, "advice"), l(first.get("title", ""), lang)),
            (t(lang, "evidence"), l(evidence.get("quote", ""), lang)),
            (t(lang, "source"), evidence.get("source", "openFDA / DailyMed / RxNorm")),
        ]:
            with st.container(border=True):
                st.markdown(f"**{label}**")
                st.caption(value)


@st.cache_data(ttl=60 * 60 * 12, show_spinner=False)
def fetch_openfda(query: str) -> dict[str, Any] | None:
    cleaned = query.strip().replace('"', "")
    if not cleaned:
        return None

    for field in OPENFDA_SEARCH_FIELDS:
        search = f'{field}:"{cleaned}"'
        url = f"https://api.fda.gov/drug/label.json?search={urllib.parse.quote(search)}&limit=1"
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "ToxiGuard-MediLens/0.1"})
            with urllib.request.urlopen(request, timeout=10, context=HTTPS_CONTEXT) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            continue
        results = payload.get("results") or []
        if results:
            return build_external_drug(results[0], query, source_url=url)
    return None


def first(value: Any) -> str:
    if isinstance(value, list) and value:
        return str(value[0])
    return str(value or "")


def text_from_fields(label: dict[str, Any], fields: list[str]) -> str:
    chunks = []
    for field in fields:
        value = label.get(field)
        if isinstance(value, list):
            chunks.extend(str(item) for item in value if item)
        elif value:
            chunks.append(str(value))
    return " ".join(" ".join(chunk.split()) for chunk in chunks)


def sentences(value: str, limit: int = 3) -> list[str]:
    clean = " ".join(value.split())
    if not clean:
        return []
    pieces = []
    for chunk in clean.replace("? ", ". ").replace("! ", ". ").split(". "):
        item = chunk.strip(" .")
        if 28 <= len(item) <= 220:
            pieces.append(item + ".")
        if len(pieces) >= limit:
            break
    return pieces


def daily_med_url(label: dict[str, Any], openfda: dict[str, Any]) -> str:
    set_id = first(openfda.get("spl_set_id")) or str(label.get("set_id") or "")
    if set_id:
        return f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={urllib.parse.quote(set_id)}"
    return SOURCE_LINKS["dailymed"]


def rxnorm_url(openfda: dict[str, Any]) -> str:
    rxcui = first(openfda.get("rxcui"))
    if rxcui:
        return f"https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm={urllib.parse.quote(rxcui)}"
    return SOURCE_LINKS["rxnorm"]


def build_external_drug(label: dict[str, Any], query: str, source_url: str) -> dict[str, Any]:
    openfda = label.get("openfda", {})
    name = first(openfda.get("brand_name")) or first(openfda.get("generic_name")) or query
    active = first(openfda.get("substance_name")) or first(openfda.get("generic_name")) or first(label.get("active_ingredient")) or "Needs review"
    product = ", ".join(part for part in [first(openfda.get("dosage_form")), first(openfda.get("route"))] if part) or "Needs review"
    indication_text = text_from_fields(label, ["indications_and_usage", "purpose"])
    warning_text_source = text_from_fields(
        label,
        [
            "warnings",
            "warnings_and_cautions",
            "drug_interactions",
            "adverse_reactions",
            "contraindications",
            "stop_use",
            "do_not_use",
            "when_using",
            "ask_doctor_or_pharmacist",
        ],
    )
    adverse_text_source = text_from_fields(label, ["adverse_reactions"])
    urgent_text_source = text_from_fields(label, ["stop_use", "do_not_use", "contraindications"])
    warning_text = warning_text_source.lower()
    official_summary = " ".join(sentences(indication_text, 2))
    if not official_summary:
        official_summary = " ".join(sentences(warning_text_source, 1))
    dailymed = daily_med_url(label, openfda)
    rxnav = rxnorm_url(openfda)

    evidence = [
        {
            "id": "external-label",
            "title": {"ko": "openFDA 레이블 원문", "en": "Original openFDA label"},
            "quote": {
                "ko": f"검색어 '{query}'로 openFDA Drug Label API에서 FDA 제출 레이블을 가져왔습니다.",
                "en": f"The FDA-submitted label was retrieved from openFDA Drug Label API for '{query}'.",
            },
            "source": "openFDA Drug Label API",
            "url": source_url,
        },
        {
            "id": "external-dailymed",
            "title": {"ko": "DailyMed SPL 레이블", "en": "DailyMed SPL label"},
            "quote": {
                "ko": "openFDA 레코드의 SPL set_id를 기반으로 DailyMed 원문 레이블 링크를 연결했습니다.",
                "en": "The DailyMed source-label link is derived from the SPL set_id in the openFDA record.",
            },
            "source": "DailyMed Structured Product Labeling",
            "url": dailymed,
        },
        {
            "id": "external-rxnorm",
            "title": {"ko": "RxNorm 표준 개념", "en": "RxNorm standard concept"},
            "quote": {
                "ko": "가능한 경우 openFDA 레코드의 RxCUI를 이용해 표준 약물 개념으로 연결합니다.",
                "en": "When available, the RxCUI in the openFDA record links this result to a standard medication concept.",
            },
            "source": "RxNorm / RxNav",
            "url": rxnav,
        },
    ]
    prechecks: list[dict[str, Any]] = []
    avoid: list[dict[str, Any]] = []

    def add(item_id: str, ko_title: str, en_title: str, ko_body: str, en_body: str, severity: str, contexts: list[str], tags: list[str]) -> None:
        evidence_id = f"external-{item_id}"
        evidence.append(
            {
                "id": evidence_id,
                "title": {"ko": ko_title, "en": en_title},
                "quote": {"ko": ko_body, "en": en_body},
                "source": "openFDA label section",
                "url": source_url,
            }
        )
        item = {
            "title": {"ko": ko_title, "en": en_title},
            "body": {"ko": ko_body, "en": en_body},
            "severity": severity,
            "context": contexts,
            "source": evidence_id,
        }
        prechecks.append(item)
        if severity in {"avoid", "caution"}:
            avoid.append({**item, "tags": tags})

    if "grapefruit" in warning_text:
        add("grapefruit", "자몽 상호작용 주의", "Grapefruit interaction warning", "레이블에서 자몽 관련 문구가 확인되었습니다. 복용 전 원문과 약사 상담을 확인하세요.", "The label includes grapefruit-related wording. Review the source label and check with a pharmacist before use.", "avoid", [], ["food", "grapefruit"])
    if "alcohol" in warning_text:
        add("alcohol", "음주 관련 주의", "Alcohol caution in label", "레이블에서 알코올 관련 주의 문구가 확인되었습니다.", "The label includes alcohol-related caution wording.", "caution", ["alcohol"], ["condition", "alcohol"])
    if any(word in warning_text for word in ["drowsiness", "dizzy", "driving", "machinery"]):
        add("driving", "운전/기계 조작 전 개인 반응 확인", "Check your response before driving or operating machinery", "졸림, 어지러움, 운전 관련 문구가 확인되었습니다.", "The label includes wording about drowsiness, dizziness, or driving.", "caution", ["driving"], ["condition", "driving"])
    if any(word in warning_text for word in ["sunlight", "photosensitivity", "tanning"]):
        add("sun", "햇빛 노출 주의", "Sun exposure caution", "광과민성 또는 햇빛 노출 관련 문구가 확인되었습니다.", "The label includes wording about photosensitivity or sun exposure.", "caution", ["sun"], ["environment", "sun"])
    if any(word in warning_text for word in ["calcium", "iron", "magnesium", "antacid", "dairy", "milk"]):
        add("minerals", "미네랄/제산제 간격 확인", "Check spacing from minerals or antacids", "미네랄, 제산제, 유제품 관련 문구가 확인되었습니다.", "The label includes wording about minerals, antacids, or dairy products.", "caution", ["supplements"], ["supplement", "absorption"])
    if any(word in warning_text for word in ["pregnancy", "pregnant", "breastfeeding", "lactation"]):
        add("pregnancy", "임신/수유 관련 레이블 확인", "Pregnancy / breastfeeding label caution", "임신, 수유 또는 특정 인구집단 관련 문구가 확인되었습니다.", "The label includes wording about pregnancy, breastfeeding, or specific populations.", "caution", ["pregnancy"], ["condition", "pregnancy"])
    if not prechecks:
        add("review", "원문 레이블 확인 필요", "Review source label", "자동 추출된 특정 음식/환경 제한은 없습니다. 원문 레이블의 warnings, interactions 섹션을 확인하세요.", "No specific food or environment restriction was automatically extracted. Review the warnings and interactions sections in the source label.", "info", [], ["review"])

    def section_cards(text: str, ko_title: str, en_title: str, ko_fallback: str, en_fallback: str, limit: int = 2) -> list[tuple[dict[str, str], dict[str, str]]]:
        extracted = sentences(text, limit)
        if not extracted:
            return [({"ko": ko_title, "en": en_title}, {"ko": ko_fallback, "en": en_fallback})]
        return [
            (
                {"ko": ko_title, "en": en_title},
                {"ko": f"레이블 원문: {sentence}", "en": sentence},
            )
            for sentence in extracted
        ]

    return {
        "id": f"external-{normalize(name).replace(' ', '-')}",
        "name": name,
        "aliases": [query.lower(), name.lower()],
        "active": active,
        "concept": {"ko": first(openfda.get("rxcui")) or "RxCUI 확인 필요", "en": first(openfda.get("rxcui")) or "RxCUI needs review"},
        "product": product,
        "status": {"ko": "openFDA 조회", "en": "openFDA lookup"},
        "label_date": {"ko": f"effective_time {label.get('effective_time', 'unknown')}", "en": f"effective_time {label.get('effective_time', 'unknown')}"},
        "summary": {
            "ko": f"openFDA 레이블에서 기본 정보를 가져왔습니다. {official_summary or '세부 원문은 근거 링크에서 확인할 수 있습니다.'}",
            "en": official_summary or "Basic information was loaded from the openFDA label. Detailed source text is available through the evidence links.",
        },
        "prechecks": prechecks,
        "avoid": avoid,
        "side_effects": {
            "common": section_cards(
                adverse_text_source,
                "부작용 섹션 요약",
                "Adverse reactions section",
                "adverse reactions 섹션이 구조화되어 있지 않습니다. 원문 레이블을 확인하세요.",
                "The adverse reactions section is not structured in this label. Review the source label.",
            ),
            "caution": section_cards(
                warning_text_source,
                "주의 문구 요약",
                "Warnings section",
                "warnings 또는 precautions 섹션을 원문에서 확인하세요.",
                "Check the warnings or precautions section in the source label.",
            ),
            "urgent": section_cards(
                urgent_text_source,
                "즉시 확인할 문구",
                "Stop-use / contraindication section",
                "호흡곤란, 얼굴 부종, 심한 알레르기 반응은 즉시 도움을 받아야 합니다.",
                "Trouble breathing, face swelling, or severe allergic reaction needs immediate help.",
                limit=1,
            ),
        },
        "evidence": evidence,
    }


def main() -> None:
    css()
    if "external_drug" not in st.session_state:
        st.session_state.external_drug = None
    if "external_query" not in st.session_state:
        st.session_state.external_query = ""
    if "external_miss_query" not in st.session_state:
        st.session_state.external_miss_query = ""

    lang = st.sidebar.segmented_control(
        "Language",
        options=["ko", "en"],
        default="ko",
        format_func=lambda value: "한국어" if value == "ko" else "English",
    )
    render_brand(lang)

    query = st.sidebar.text_input(t(lang, "search"), value="", help=t(lang, "search_help"))
    normalized_query = normalize(query)
    matches = match_drugs(query)
    external_matches_query = (
        bool(normalized_query)
        and st.session_state.external_drug
        and st.session_state.external_query == normalized_query
    )

    if external_matches_query:
        selected = st.session_state.external_drug
        st.sidebar.success(t(lang, "external_loaded"))
        st.sidebar.caption(t(lang, "official_result"))
    elif matches:
        selected_name = st.sidebar.selectbox(
            t(lang, "search_results"),
            options=[drug["name"] for drug in matches],
            index=0,
            help=t(lang, "sample_result"),
        )
        selected = next(drug for drug in matches if drug["name"] == selected_name)
    elif normalized_query and st.session_state.external_miss_query != normalized_query:
        with st.spinner(t(lang, "official_searching")):
            found = fetch_openfda(official_query(query))
        if found:
            st.session_state.external_drug = found
            st.session_state.external_query = normalized_query
            st.session_state.external_miss_query = ""
            st.rerun()
        st.session_state.external_miss_query = normalized_query
        selected = SAMPLE_DRUGS[0]
        st.sidebar.warning(t(lang, "search_not_found"))
    else:
        selected = SAMPLE_DRUGS[0]
        if normalized_query:
            st.sidebar.warning(t(lang, "search_not_found"))
        else:
            st.sidebar.caption(t(lang, "sample_result"))

    st.sidebar.markdown(f"### {t(lang, 'try_openfda')}")
    st.sidebar.caption(t(lang, "source_lookup_caption"))
    refresh_label = t(lang, "refresh_official") if normalized_query else t(lang, "openfda_button")
    if st.sidebar.button(refresh_label, type="primary", icon=":material/search:", use_container_width=True):
        lookup_source = query.strip() or selected["name"]
        lookup_key = normalize(query) or normalize(selected["name"])
        if not lookup_source:
            st.sidebar.warning(t(lang, "no_query"))
        else:
            with st.spinner(t(lang, "official_searching")):
                found = fetch_openfda(official_query(lookup_source))
            if found:
                st.session_state.external_drug = found
                st.session_state.external_query = lookup_key
                st.session_state.external_miss_query = ""
                st.rerun()
            else:
                st.session_state.external_miss_query = lookup_key
                st.sidebar.error(t(lang, "lookup_empty"))

    st.sidebar.markdown(f"### {t(lang, 'context')}")
    active_contexts: set[str] = set()
    for context in CONTEXTS:
        checked = st.sidebar.checkbox(l(context["label"], lang), help=l(context["note"], lang), key=f"context-{context['id']}")
        if checked:
            active_contexts.add(context["id"])

    st.sidebar.markdown(f"### {t(lang, 'sources')}")
    st.sidebar.link_button("RxNorm", SOURCE_LINKS["rxnorm"], icon=":material/hub:", use_container_width=True)
    st.sidebar.link_button("openFDA Drug Label", SOURCE_LINKS["openfda"], icon=":material/open_in_new:", use_container_width=True)
    st.sidebar.link_button("DailyMed SPL", SOURCE_LINKS["dailymed"], icon=":material/source:", use_container_width=True)
    st.sidebar.caption(t(lang, "source_note"))

    with st.container(border=True):
        st.caption(t(lang, "top_eyebrow"))
        st.markdown(f"## {t(lang, 'top_title')}")
        st.write(t(lang, "top_copy"))

    render_drug_header(selected, lang)

    cards = ranked_prechecks(selected, active_contexts)
    risk_class, risk_text = risk_label(lang, cards)
    render_visual_overview(selected, cards, risk_class, risk_text, active_contexts, lang)

    left, right = st.columns([1.08, 0.92], gap="large")
    with left:
        with st.container(border=True):
            title_col, risk_col = st.columns([0.72, 0.28], vertical_alignment="center")
            title_col.markdown(f"### {t(lang, 'precheck')}")
            risk_col.badge(
                risk_text,
                icon=SEVERITY_ICONS.get(risk_class),
                color=SEVERITY_COLORS.get(risk_class, "gray"),
            )
        for item in cards:
            evidence = evidence_by_id(selected, item.get("source"))
            card(l(item["title"], lang), l(item["body"], lang), item["severity"], lang, evidence.get("source"))

    with right:
        render_evidence_flow(selected, cards, lang)

    side_col, avoid_col = st.columns([1, 1], gap="large")
    with side_col:
        st.markdown(f"### {t(lang, 'side_effects')}")
        tab_common, tab_caution, tab_urgent = st.tabs([t(lang, "common"), t(lang, "caution_tab"), t(lang, "urgent_tab")])
        for tab, key, severity in [
            (tab_common, "common", "info"),
            (tab_caution, "caution", "caution"),
            (tab_urgent, "urgent", "urgent"),
        ]:
            with tab:
                for title, body in selected.get("side_effects", {}).get(key, []):
                    card(l(title, lang), l(body, lang), severity, lang)

    with avoid_col:
        st.markdown(f"### {t(lang, 'avoid')}")
        for item in selected.get("avoid", []):
            card(l(item["title"], lang), l(item["body"], lang), item["severity"], lang, tags=item.get("tags", []))

    st.markdown(f"### {t(lang, 'evidence')}")
    for item in selected.get("evidence", []):
        with st.container(border=True):
            st.markdown(f"**{l(item['title'], lang)}**")
            st.write(l(item["quote"], lang))
            st.caption(f"{t(lang, 'source')}: {item['source']}")
            st.link_button(t(lang, "view_source"), item["url"], icon=":material/open_in_new:")

    st.info(t(lang, "disclaimer"))


if __name__ == "__main__":
    main()
