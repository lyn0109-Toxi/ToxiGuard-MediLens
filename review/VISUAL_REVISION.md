# Quantitative visualization revision

Request: prioritize visual data over number cards, tables and decorative images.

Branch: `feature/composition-preview`. No push or public deployment.

## Changed experience

- Replaced number cards and secondary chart with one dominant responsive horizontal mass chart.
- Bar lengths are proportional within a compatible unit/denominator group. Every bar has a directly attached amount and explicit **per tablet**, **per capsule**, **per dosage unit** or **per mL** denominator.
- Both normalized and original label quantities remain visible with the original strength basis. Separate chart groups handle per-unit versus per-mL quantities; incompatible units stay unscaled and labeled.
- Single-ingredient charts run from zero to the actual declared amount, with no invented comparator or dosing limit. No full-formulation percentages, potency or equivalence implication.
- Undisclosed excipient quantities appear as a gray hatched panel of named ingredients, with no quantitative bar or implied zero.
- Removed decorative photo presentation and reduced hero text. Manufacturer, labeler, provenance and original source evidence remain in expandable detail. Existing safety workspace remains available.
- Korean/English retained. Source ingredient names remain in the source language.

## Validation

- **31 offline automated tests passed**: prior 23 tests retained (card test updated to bars), plus 8 visualization tests covering ratios/direct labels, single ingredient axis semantics, liquid normalization/original denominator, strength basis, qualitative undisclosed excipients, incompatible denominator grouping, incompatible units, Korean display.
- Public SPL fixtures downloaded earlier remain unchanged. Mocked failures and synthetic conversion/release tests are offline. These are not 31 live API tests.
- Main app live check: DailyMed Excedrin search returned 30 candidates and the selected SPL was retrieved for the new chart.
- Desktop visual QA at 1406px and narrow QA at 390 × 844 for combination tablets, single tablets, and liquids. All six checks had `document.documentElement.scrollWidth <= window.innerWidth`.
- Combination measured desktop bar widths: 1184 / 1184 / 307.84 px; narrow: 324 / 324 / 84.23 px. The smaller bar represents 65/250 = 0.26 of the larger, within pixel rounding.
- Korean narrow liquid displays **1 mL당 32 mg** and original **160 mg / 5 mL**.
- Narrow viewports restored after verification. No physical-device test performed.

Screenshots in this directory:

| Case | Desktop | Narrow |
|---|---|---|
| Combination | v2-combination-desktop.jpg | v2-combination-narrow.jpg |
| Single ingredient | v2-single-desktop.jpg | v2-single-narrow.jpg |
| Liquid | v2-liquid-desktop.jpg | v2-liquid-narrow-ko.jpg |

Additional live main-app screenshot: `v2-live-combination-ko.jpg` (Korean Excedrin chart retrieved from DailyMed).

The six matrix screenshots use a clearly labeled public-fixture QA harness that runs the **production composition renderer**, not a separate mock design. Fixture mode is confined to `review/visual_qa.py`; the main app continues to use DailyMed live search with explicit product selection.

## Preview

Main app: http://127.0.0.1:8517

Offline visual review: http://127.0.0.1:8518/?example=liquid&lang=ko

Restart QA with `python3 -m streamlit run review/visual_qa.py --server.address 127.0.0.1 --server.port 8518`.

## Library delivery blocker

Attempted the required Library batch helper for three representative screenshots. First attempt failed TLS during tool discovery before any upload; retry with the installed certifi CA bundle retained certificate verification and returned `Library prepare_uploads is not available`. No screenshot from this revision was uploaded, and no new Library IDs were returned. All local screenshots remain intact. Earlier screenshot IDs refer to the previous card-based version and should not be presented as the new interface.

The required Library prepared-upload workflow forbids switching a started helper write to a direct upload. This blocker is tool availability, not denied user authorization.

Existing limitations from REVIEW.md remain: unavailable MFDS access, unsupported nested kits, release type unknown where unspecified, no inferred RxNorm strengths, and manufacturer/labeler kept separate.
