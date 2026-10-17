"""Reproducible Chromium layout, keyboard, and motion checks; no remote data."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent/'safety-graphics'
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=browser.new_page()
    for lang in ['en','ko']:
        for width in [1440,390,320]:
            page.set_viewport_size({'width':width,'height':1000})
            for name in ['mucinex-solution','fexofenadine','artificial-tears','metoprolol-er','empty']:
                page.set_content((ROOT/f'{name}-{lang}.html').read_text())
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'),(name,lang,width,'overflow')
                if name!='empty':
                    assert page.locator('.safety-card').count()==7
                    assert page.locator('img').evaluate_all('(els)=>els.every(e=>e.complete && e.naturalWidth>0)')
                    for card in page.locator('.safety-card:not(.safety-kind-adverse) details').all():
                        assert card.get_attribute('open') is not None
                    summary=page.locator('summary').first
                    summary.focus();was=summary.evaluate('(e)=>e.parentElement.open')
                    page.keyboard.press('Enter');assert summary.evaluate('(e)=>e.parentElement.open')!=was
                    page.keyboard.press('Space');assert summary.evaluate('(e)=>e.parentElement.open')==was
                    assert summary.evaluate('(e)=>getComputedStyle(e).outlineStyle')=='solid'
                results.append({'fixture':name,'lang':lang,'width':width,'overflow':False})
            if width in [1440,390]:
                page.set_content((ROOT/f'fexofenadine-{lang}.html').read_text())
                page.locator('.label-safety').screenshot(path=str(ROOT/f'cards-{lang}-{width}.png'))
    page.set_content((ROOT/'mucinex-solution-en.html').read_text())
    assert page.locator('.safety-urgent').first.evaluate('(e)=>getComputedStyle(e).opacity')=='1'
    assert page.locator('.safety-urgent').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
    page.emulate_media(reduced_motion='reduce')
    assert page.locator('.safety-icon').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
    page.locator('.safety-urgent').first.screenshot(path=str(ROOT/'urgent-en.png'))
    browser.close()
(ROOT/'browser-results.json').write_text(json.dumps({'cases':results,'keyboard':'Enter/Space and visible focus passed','reduced_motion':'passed','urgent_immediate_visibility':'passed'},indent=2))
print(f'{len(results)} layout cases; keyboard, motion and urgent visibility passed')
