# ToxiGuard-MediLens

ToxiGuard-MediLens is a Streamlit prototype for turning long medication labels into a short, evidence-traceable pre-dose safety view.

## What it does

- Search sample medications by brand, generic name, or Korean alias.
- Automatically look up non-sample medications through the openFDA Drug Label API.
- Show active ingredient, product form, and label provenance.
- Show a visual safety overview with Material design icons, risk meters, and evidence counts.
- Add a SmartDUR+-style medication lens that turns the selected drug plus entered medication/food lists into a prescription-level safety snapshot.
- Show a DUR-style prescription review panel for dose, duplication, interactions, age, pregnancy/breastfeeding, food, and treatment duration.
- Flag common review patterns such as warfarin + NSAID/aspirin/alcohol bleeding risk, simvastatin + grapefruit/CYP3A4 inhibitor risk, fexofenadine + fruit juice/antacid absorption issues, pregnancy-related NSAID checks, and age/duration review.
- Summarize pre-dose checks, side effects, foods/conditions to avoid, and source evidence.
- Display image-first cards and an illustrated check map for foods, conditions, and warning signals.
- Show pre-dose action cards for avoid-now, watch-symptoms, and ask-pharmacist decisions.
- Match user-entered medicines, supplements, foods, or drinks against current warning cards.
- Accept a prescription / medication list text input so users can paste several medicines and see recognized items visually.
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

## Composition preview

Current design: [verified molecular ingredient visuals](review/MOLECULAR_REVISION.md). Matching requires name and UNII; unverified identities use generic placeholders. See [molecular source/reuse evidence](assets/molecules/PROVENANCE.md).

The default **Composition** workspace searches DailyMed by product/generic name and optionally by manufacturer or labeler. Choose a label, then an exact structured product/strength/form/NDC. **Safety overview** preserves the existing application.

- Displays active ingredient quantity, strength basis, active moiety, original XML/text and provenance.
- Compares only supported mass units per dosage unit or per mL. Does not infer missing amounts, total tablet mass, therapeutic equivalence or approval status.
- Korean UI and English UI; label terminology remains in its original language.
- Korea reports MFDS access unavailable; kits with nested parts report missing structured composition.
- Public DailyMed access is required. Successful requests are cached for one hour; displayed retrieval timestamps describe the cached response.

Run checks with `python3 -m unittest discover -s tests -v`. See [the visual revision](review/VISUAL_REVISION.md) for the current proportional-bar interface and responsive QA; see [review/REVIEW.md](review/REVIEW.md) for original scope, screenshots, limitations and deployment requirements. See [new image provenance](assets/COMPOSITION_IMAGE_LICENSE.md).
