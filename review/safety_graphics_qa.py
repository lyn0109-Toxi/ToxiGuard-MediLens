"""Generate offline, self-contained previews from the production safety renderer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from composition import parse_spl
from label_safety_ui import STYLE,safety_html,urgent_html
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'review/safety-graphics'
OUT.mkdir(exist_ok=True)
for name in ['mucinex-solution','fexofenadine','artificial-tears','metoprolol-er','empty']:
    for lang in ['en','ko']:
        record=parse_spl((ROOT/'tests/fixtures'/(name+'.xml')).read_bytes(),retrieved_at='2026-10-16 · retained public fixture, not live') if name!='empty' else None
        product=record['products'][0] if record else {}
        content=urgent_html(record,product,lang)+safety_html(record,product,lang)
        (OUT/f'{name}-{lang}.html').write_text('<!doctype html><html lang="'+lang+'"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MediLens safety review</title>'+STYLE+'<style>body{margin:0;background:#f7fafb;font-family:Arial,sans-serif}main{max-width:1160px;margin:auto;padding:24px}header{color:#365262;font-size:13px;line-height:1.6}</style><main><header>MediLens · OFFLINE PUBLIC LABEL FIXTURE · 2026-10-16 · not live medical advice</header>'+content+'</main></html>')
