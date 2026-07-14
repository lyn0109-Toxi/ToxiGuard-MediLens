# ToxiGuard-MediLens

ToxiGuard-MediLens is a Streamlit prototype for turning long medication labels into a short, evidence-traceable pre-dose safety view.

## What it does

- Search sample medications by brand, generic name, or Korean alias.
- Show active ingredient, product form, and label provenance.
- Summarize pre-dose checks, side effects, foods/conditions to avoid, and source evidence.
- Switch between Korean and English.
- Optionally search openFDA Drug Label API for non-sample medications.

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
