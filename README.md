# ToxiGuard-MediLens

ToxiGuard-MediLens is a Streamlit prototype for turning long medication labels into a short, evidence-traceable pre-dose safety view.

## What it does

- Search sample medications by brand, generic name, or Korean alias.
- Automatically look up non-sample medications through the openFDA Drug Label API.
- Show active ingredient, product form, and label provenance.
- Show a visual safety overview with Material design icons, risk meters, and evidence counts.
- Summarize pre-dose checks, side effects, foods/conditions to avoid, and source evidence.
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
