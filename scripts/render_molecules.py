"""Build-time only: deterministically depict verified PubChem records with RDKit."""
import hashlib
import json
from pathlib import Path
from rdkit import Chem, rdBase
from rdkit.Chem import rdMolDescriptors
from rdkit.Chem.Draw import rdMolDraw2D
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets'/'molecules'
PROPERTIES_URL='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/property/IUPACName,InChIKey,IsomericSMILES,MolecularFormula/JSON'
SYNONYMS_URL='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/1983,2244,2519/synonyms/JSON'
ENTITIES={1983:('ACETAMINOPHEN','362O9ITL9D','#147d85'),2244:('ASPIRIN','R16CO5Y76E','#625cb4'),2519:('CAFFEINE','3G6A5W338E','#b16a2f')}
properties=json.loads((OUT/'pubchem-properties.json').read_text())['PropertyTable']['Properties']
synonyms={r['CID']:r['Synonym'] for r in json.loads((OUT/'pubchem-synonyms.json').read_text())['InformationList']['Information']}
manifest={}
for record in properties:
    cid=record['CID'];name,unii,color=ENTITIES[cid]
    terms={x.upper() for x in synonyms[cid]}
    assert name in terms and unii in terms, 'Identity verification failed'
    molecule=Chem.MolFromSmiles(record['SMILES'])
    assert molecule is not None
    assert Chem.MolToInchiKey(molecule)==record['InChIKey']
    assert rdMolDescriptors.CalcMolFormula(molecule)==record['MolecularFormula']
    # Neutral single-component achiral entities only in this curated release.
    assert len(Chem.GetMolFrags(molecule))==1 and Chem.GetFormalCharge(molecule)==0
    assert not Chem.FindMolChiralCenters(molecule,includeUnassigned=True)
    drawer=rdMolDraw2D.MolDraw2DCairo(600,420)
    options=drawer.drawOptions();options.clearBackground=False
    options.padding=.08;options.fixedBondLength=-1
    options.minFontSize=24;options.maxFontSize=28
    options.bondLineWidth=2.5
    options.useBWAtomPalette()
    rdMolDraw2D.PrepareAndDrawMolecule(drawer,molecule)
    drawer.FinishDrawing()
    data=drawer.GetDrawingText();filename=f'cid-{cid}.png';(OUT/filename).write_bytes(data)
    manifest[unii]={**record,'entity':name,'verified_names':[name],'unii':unii,'accent':color,'image':filename,'image_sha256':hashlib.sha256(data).hexdigest(),'source_url':f'https://pubchem.ncbi.nlm.nih.gov/compound/{cid}','properties_url':PROPERTIES_URL,'synonyms_url':SYNONYMS_URL,'retrieved_at':'2026-10-16','renderer':'RDKit '+rdBase.rdkitVersion,'identity_scope':'Exact neutral ingredient substance; not salt, metabolite or strength-basis substitution','depiction':'Deterministic 2D structure; transparent PNG 600 × 420'}
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Verified and rendered',len(manifest),'entities')
