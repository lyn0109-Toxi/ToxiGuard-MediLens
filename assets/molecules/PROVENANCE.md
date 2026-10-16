# Molecular image provenance and reuse

These images are **new deterministic depictions**, not downloaded illustration artwork and not generative chemistry. Built 2026-10-16 using RDKit 2026.03.1 from exact PubChem structure records. All are transparent PNG, 600 × 420. Build script: `scripts/render_molecules.py` (build-time RDKit only; no new production dependency).

| Depicted ingredient substance | SPL / PubChem UNII | PubChem CID | InChIKey |
|---|---|---|---|
| Acetaminophen (neutral) | 362O9ITL9D | 1983 | RZVAJINKPMORJF-UHFFFAOYSA-N |
| Aspirin (neutral acetylsalicylic acid) | R16CO5Y76E | 2244 | BSYNRYMUTXBXSQ-UHFFFAOYSA-N |
| Caffeine (neutral, anhydrous entity) | 3G6A5W338E | 2519 | RYYVLZVUVIJVGH-UHFFFAOYSA-N |

## Exact sources

- https://pubchem.ncbi.nlm.nih.gov/compound/1983
- https://pubchem.ncbi.nlm.nih.gov/compound/2244
- https://pubchem.ncbi.nlm.nih.gov/compound/2519
- Properties: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/property/IUPACName,InChIKey,IsomericSMILES,MolecularFormula/JSON
- Synonyms/UNII: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/synonyms/JSON

Original API responses are retained as `pubchem-properties.json` and `pubchem-synonyms.json`. The manifest retains source URLs, retrieval date, identifiers, structure SMILES, formula, renderer, identity scope and PNG SHA-256. No amounts are obtained from PubChem: every amount still comes from the selected SPL.

## Identity and rendering checks

Build checks require both the exact ingredient name and UNII in the PubChem CID synonym record. RDKit independently reproduces the supplied InChIKey and molecular formula. This curated set has one neutral component and no stereocenters. Runtime requires the exact case-insensitive ingredient name **and** UNII; it does not strip salt suffixes, hydration states or stereochemical qualifiers. No fuzzy match, parent-compound fallback, active-moiety substitution or strength-basis substitution occurs.

The registry currently covers only these three entities. A salt such as metoprolol succinate does not receive a metoprolol free-base drawing. Unknown, complex, unmapped, identity-mismatched or missing/corrupt image cases use a labeled generic non-molecular symbol. Future registry entries require explicit salt/stereochemical identity review, corresponding source identifiers and tests.

## Reuse information

- NCBI molecular data policy: https://www.ncbi.nlm.nih.gov/home/about/policies/#data — NCBI places no restrictions on use/distribution of molecular data, while expressly noting possible submitter intellectual-property claims. **This is not a blanket assertion that all PubChem content is CC0.**
- Only factual structure encodings/identifiers are used to generate these new diagrams; third-party article text, images, descriptive annotations and trademarks are not reproduced as artwork.
- RDKit is BSD 3-Clause licensed and permits commercial use subject to its terms: https://github.com/rdkit/rdkit/blob/master/license.txt . No RDKit binary or copied implementation is bundled with the app.
- Generated PNG depictions are original project outputs from chemical facts; they are not claimed to be downloaded CC0 artwork. No separate third-party image license is being relied on. Acknowledge PubChem/NCBI and RDKit as shown in the UI and this file.
- Prior Google-discovered supporting photo remains preserved in the repository but is not displayed in this design.

Colors identify ingredients only. Images use equal display boxes and are not proportional to dose, potency, toxicity or risk. 2D depictions are identity illustrations, not evidence of therapeutic equivalence or a model of the full product formulation.
