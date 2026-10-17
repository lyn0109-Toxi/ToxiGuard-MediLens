from playwright.sync_api import sync_playwright
from pathlib import Path
out=Path(__file__).resolve().parent/'safety-graphics'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1100})
 page.goto('http://127.0.0.1:8532/?example=fexofenadine&lang=ko')
 page.locator('.label-safety').wait_for(timeout=60000)
 assert page.locator('.safety-card').count()==7
 page.locator('.label-safety').scroll_into_view_if_needed()
 page.screenshot(path=str(out/'streamlit-ko-desktop.png'))
 page.set_viewport_size({'width':390,'height':900})
 page.locator('.safety-kind-food').scroll_into_view_if_needed()
 page.screenshot(path=str(out/'streamlit-ko-mobile.png'))
 page.locator('.safety-kind-interactions').scroll_into_view_if_needed()
 page.screenshot(path=str(out/'streamlit-ko-interactions-mobile.png'))
 assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.emulate_media(reduced_motion='reduce')
 assert page.locator('.safety-icon').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
 assert page.locator('[data-testid="stException"]').count()==0
 print('Live Streamlit: seven categories, desktop/mobile, reduced motion, no horizontal overflow or exceptions passed')
 b.close()
