# ToxiGuard-MediLens

ToxiGuard-MediLens is a Streamlit prototype for turning long medication labels into a short, evidence-traceable pre-dose safety view.

## What it does

- Search sample medications by brand, generic name, or Korean alias.
- Automatically look up non-sample medications through the openFDA Drug Label API.
- Show active ingredient, product form, and label provenance.
- Show a visual safety overview with Material design icons, risk meters, and evidence counts.
- Show a DUR-style prescription review panel for dose, duplication, interactions, age, pregnancy/breastfeeding, food, and treatment duration.
- Summarize pre-dose checks, side effects, foods/conditions to avoid, and source evidence.
- Display image-first cards and an illustrated check map for foods, conditions, and warning signals.
- Show pre-dose action cards for avoid-now, watch-symptoms, and ask-pharmacist decisions.
- Match user-entered medicines, supplements, foods, or drinks against current warning cards.
- Use richer medication-counseling illustration cards with medicine + food/context pairings, warning marks, and short supporting text.
- Prioritize specific organ, symptom, and food images when a label mentions liver risk, muscle symptoms, bleeding, grapefruit, milk, cheese, coffee, juice, or leafy greens.
- Show a side-effect image gallery before the detailed tabs so organ and symptom visuals are visible without extra clicks.
- Switch between Korean and English.
- Link recommendations back to openFDA, DailyMed SPL, RxNorm, and FDA consumer sources where available.

## Run

```bash
streamlit run app.py
```

Then open:

```text
http://127.0.0.1:8501
```

## Notes

This is an educational prototype based on official-label concepts. It is not a diagnosis, prescribing, or emergency-care tool.
