"""Conservative exact-identity mapping; no network or chemistry runtime dependency."""
import base64
import hashlib
import json
from html import escape
from pathlib import Path
ASSET_DIR=Path(__file__).parent/'assets'/'molecules'

def lookup_structure(ingredient, asset_dir=None):
    directory=Path(asset_dir) if asset_dir is not None else ASSET_DIR
    try:
        manifest=json.loads((directory/'manifest.json').read_text())
        entry=manifest.get(ingredient.get('unii'))
        name=' '.join(ingredient.get('name',ingredient.get('ingredient','')).upper().split())
        if not entry or name not in entry['verified_names'] or entry['unii'] != ingredient.get('unii'):
            return None
        path=directory/entry['image']
        if path.parent!=directory or path.suffix!='.png':return None
        data=path.read_bytes()
        if not data.startswith(b'\x89PNG\r\n\x1a\n') or hashlib.sha256(data).hexdigest()!=entry['image_sha256']:
            return None
        return {**entry,'data_uri':'data:image/png;base64,'+base64.b64encode(data).decode()}
    except (OSError,ValueError,TypeError,KeyError,AttributeError):
        return None

def structure_tile(ingredient,lang='en'):
    ko=lang=='ko'
    entry=lookup_structure(ingredient)
    if not entry:
        note='검증된 구조 없음' if ko else 'Structure not verified'
        generic='일반 기호 · 분자 구조 아님' if ko else 'Generic symbol · not a molecule'
        return '<div class="molecule-tile"><div class="molecule-placeholder" role="img" aria-label="'+generic+'"><span>▧</span></div><div class="molecule-caption">'+note+'<br><span>'+generic+'</span></div></div>'
    caption=('표현 물질: ' if ko else 'Depicted: ')+entry['entity']
    return '<div class="molecule-tile"><img class="molecule-image" width="600" height="420" src="'+entry['data_uri']+'" alt="'+escape(entry['entity']+' · verified 2D structure · PubChem CID '+str(entry['CID']),quote=True)+'"><div class="molecule-caption">'+escape(caption)+'<br><a target="_blank" rel="noopener noreferrer" href="'+escape(entry['source_url'],quote=True)+'">PubChem CID '+str(entry['CID'])+'</a></div></div>'

def accent(ingredient):
    entry=lookup_structure(ingredient)
    return entry['accent'] if entry else '#6b7d89'

def structure_evidence(ingredients):
    result=[]
    for i in ingredients:
        if not i['active']:continue
        entry=lookup_structure(i)
        result.append({'label_ingredient':i['name'],'label_unii':i.get('unii'),'structure_status':'verified' if entry else 'unavailable or identity mismatch','structure':{k:v for k,v in entry.items() if k!='data_uri'} if entry else None})
    return result
