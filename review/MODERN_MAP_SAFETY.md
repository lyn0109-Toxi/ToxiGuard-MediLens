# Modern map and selected-label safety

Local review branch: `feature/modern-map-motion`, based on `431aea6653906065b075c7a94f66f7aa27a09310`. This revision is not deployed.

## Interface

A neutral scientific canvas, navy/teal conceptual dosage-form art and fixed equal-size ingredient cards emphasize exact declared amounts. One bounded 620ms reveal, with at most 130ms stagger, moves decorative graphics from the central art behind the cards. Text and targets stay fixed. Reveal can be replayed; lists over eight items stay static. Placement, size and motion encode no amount, risk or physical distribution. Existing verified PNG molecular assets and provenance remain unchanged; unverified structures use a generic symbol. No new third-party artwork or network font is added.

System reduced-motion preference and an in-app, session-persisted control disable reveal, card transitions, modal and backdrop animation. Resize, filtering and component teardown cancel reveal animations. Native dialog keyboard behavior, Escape, focus return and evidence tooltips remain available. Urgent conditional warnings are static and rendered before the map and basis controls.

## Safety evidence

The selected SPL and exact structured product drive cards for adverse reactions, food/drink, stop-use conditions, contraindications/duplicate actives, interactions, precautions and age/formulation/directions. There is no generic drug-class fallback. LOINC section codes and parent codes, full original wording, section date, SPL version, label date and retrieval metadata remain visible. Shared source-link resolution and existing icon assets are reused from the legacy workspace. The legacy safety workspace is otherwise unchanged.

Bilingual summaries cover a small explicitly guarded phrase set. Commonness/frequency appear only with explicit population and frequency in the source. Alcohol caution, food avoidance and food administration are distinct. Missing dedicated adverse-reaction sections and missing food advice have explicit missing-information states and are not safety clearance. Multiple-product labels require applicability review; automatic urgent summaries are withheld for them. Conditional urgent wording is never an assertion that the user has that condition.

Public retained examples include Mucinex solution, fexofenadine, metoprolol extended release and artificial tears. `tests/fixtures/SAFETY_SOURCES.json` records official source URLs, retrieval date, file completion time, SPL versions and hashes. Fixtures use a visible not-live banner; production requests retain their actual response retrieval timestamp.

## Validation and review

Run `python3 -m unittest discover -s tests -q`, `node --check ingredient_map_assets/map.js` and `git diff --check`.

The suite covers composition parsing/conversions/missing data/source failures, product disambiguation, ER salt/reference basis, no stale cards on product changes, classification and summary guards, source escaping/provenance and scoped motion cleanup. Streamlit AppTest verifies production composition integration and the legacy workspace. Browser review covers original and normalized Mucinex strengths, fexofenadine fruit-juice wording, metoprolol meal wording/population and strength switching, artificial-tears missing-food/external-use state, Korean and English, expanded exact evidence, actual pointer hover, keyboard modal/focus, reduced motion, final fixed-card reveal and 390px layouts including 16 inactive entries. No screenshots were uploaded or embedded.

Local fixtures: `python3 -m streamlit run review/visual_qa.py --server.port 8532`; open `http://127.0.0.1:8532/?example=mucinex-solution&lang=en`. Full app: `python3 -m streamlit run app.py --server.port 8533`. These are localhost previews on the connected Mac, not public preview hosting.

## Limits and deployment

Safety summaries are limited source navigation, not a comprehensive clinical validation or personal clearance. Original US label English remains authoritative. Korea/MFDS access remains unavailable; no Korean product results are fabricated. Only the existing three exact verified molecular identities have PNG structures. No therapeutic equivalence, approval status or missing excipient amounts are inferred. OS-level preference emulation and physical touch hardware were not tested; the in-app static alternative and CSS system-preference contract were checked.

Review and explicit deployment authorization are still needed before any push/merge/public release. Deployment needs the existing Streamlit dependencies and outbound access to official DailyMed services; no new secret is required for US labels. MFDS integration would require authorized API access and separate validation.
