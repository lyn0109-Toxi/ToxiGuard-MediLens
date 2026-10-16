# Ingredient-specific molecular visualization

Branch: `feature/composition-preview`. No push, merge, public deployment or Streamlit Cloud changes.

## Result

Compact ingredient rows now combine a verified transparent 2D molecular PNG, a directly labeled amount and an integrated proportional horizontal bar. Acetaminophen uses teal, aspirin indigo and caffeine amber consistently across products. Colors identify ingredients only. Images use equal display boxes, independent of amount, potency or risk. Original strength basis and label quantity remain directly beneath each bar. Missing excipient quantities remain qualitative hatched labels.

Only exact curated identity matches are depicted: both ingredient name and UNII must agree. Runtime never searches by a partial name, strips a salt suffix, substitutes a free base or selects an unverified stereoisomer. Unknown/complex/unmapped entities, missing identifiers and missing/corrupt images use a clearly labeled generic non-molecular symbol. Metoprolol succinate demonstrates this fallback while preserving metoprolol tartrate as its declared strength basis.

## Verified data and reuse

| Depicted entity | UNII | PubChem CID | Source |
|---|---|---|---|
| Acetaminophen, neutral | 362O9ITL9D | 1983 | https://pubchem.ncbi.nlm.nih.gov/compound/1983 |
| Aspirin, neutral acetylsalicylic acid | R16CO5Y76E | 2244 | https://pubchem.ncbi.nlm.nih.gov/compound/2244 |
| Caffeine, neutral anhydrous entity | 3G6A5W338E | 2519 | https://pubchem.ncbi.nlm.nih.gov/compound/2519 |

Data retrieved 2026-10-16:

- https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/property/IUPACName,InChIKey,IsomericSMILES,MolecularFormula/JSON
- https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/synonyms/JSON

RDKit 2026.03.1 deterministically generated original 600 × 420 transparent PNGs from the returned structure encodings. Build validation checks name+UNII synonyms, exact InChIKey, formula, neutral single component and absence of stereocenters for this release's three entities. Source JSON, manifest, PNG hashes and renderer script are retained. RDKit is a build-time dependency only; deployed Streamlit uses bundled PNGs and Python's standard library, with no PubChem network dependency.

NCBI molecular-data policy: https://www.ncbi.nlm.nih.gov/home/about/policies/ . It places no NCBI restrictions on molecular-data use/distribution, but explicitly retains possible submitter IP claims. This is **not** a blanket CC0 assertion for PubChem. Only factual structure encodings/identifiers are used to produce new depictions; no third-party article or illustration artwork is copied. RDKit BSD 3-Clause license: https://github.com/rdkit/rdkit/blob/master/license.txt . Detailed reuse scope: `assets/molecules/PROVENANCE.md`.

## Validation

- **44 offline automated tests passed**: previous 31 tests, 12 structure-mapping/rendering tests and one legacy safety-workspace regression test.
- Added tests cover name+UNII→CID matches, wrong/missing identifiers, salts not mapped to parent, stereochemical name mismatch, strict normalization, missing manifest/image, corrupt PNG, malformed manifest, original-source synonym evidence, equal PNG dimensions, stable accents, and integrated bars/basis.
- Rendering script independently verifies PubChem structure identity with RDKit. Automated tests use the retained public SPL/PubChem snapshots, synthetic data and mocks, not 44 live API responses.
- Desktop 1406px and mobile 390 × 844: combination tablets (Korean), single tablets (English), liquids (English). All six checks show no horizontal overflow and loaded PNGs. Desktop image boxes 144 × 101; mobile 96 × 74, equal for all ingredients within a layout.
- Combination bar lengths remain proportional: desktop 1020/1020/265.20px; mobile 216/216/56.16px, consistent with 250/250/65mg.
- Salt fallback rendered separately: no metoprolol free-base molecule substituted; tartrate strength basis retained.
- Source quantities, separate incompatible-unit groups, single-ingredient axis semantics, both languages, source failures, unknown amounts and safety workspace remain covered.
- `compileall` and `git diff --check` passed.
- See `v3-layout-metrics.json`, `test-results-v3.txt` and `v3-*.jpg` screenshots.

## Preview and remaining limits

Main app: http://127.0.0.1:8517

Public-fixture review: http://127.0.0.1:8518/?example=excedrin&lang=ko

The fixture review uses production rendering, clearly labeled as stored public data. The main app retains real DailyMed search and explicit label/product selection.

Only three neutral entities currently have reviewed molecular mappings. Additional ingredients need verified data and corresponding identity tests; until then they receive generic placeholders. This is intentional, not an inferred molecular match. MFDS access and nested-kit limitations remain unchanged. No full formulation percentages or therapeutic-equivalence, safety, potency or approval inference is introduced.

## Final completion after reconnection

The saved diff was inspected on `feature/composition-preview`; it contains only the intended molecular visuals, identity parser metadata, source assets, tests and review evidence. No unrelated work was overwritten.

The full suite was rerun after Mac reconnection: **44 tests passed**. Compile and whitespace checks passed. Both localhost previews were restarted. Chrome reverified three loaded molecular PNGs, no horizontal overflow, and proportional combination bars (1020 / 1020 / 265.20 px). The actual main app also completed a fresh live DailyMed Excedrin search (30 candidates), exact SPL/product selection, and rendered all three molecular images with no overflow; see `v3-final-live-ko.jpg`.

## Screenshot delivery

The requested single representative molecular screenshot was successfully saved to ChatGPT Library as `v3-molecules-desktop-ko.jpg`. All desktop/mobile and placeholder screenshots remain in this repository. The earlier interrupted batch attempt created no files; the final single-file save succeeded.

No public push or deployment was performed. Clinical/data limitations described above remain; the previous Mac/Library delivery interruption is resolved.
