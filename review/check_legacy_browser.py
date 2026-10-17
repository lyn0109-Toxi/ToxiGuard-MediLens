from pathlib import Path
from playwright.sync_api import sync_playwright, expect
OUT=Path(__file__).resolve().parent/'safety-graphics'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1440,'height':1050})
    page.goto('http://127.0.0.1:8533')
    page.get_by_text('기존 안전성 보기',exact=True).click()
    root=page.locator('.st-key-legacy-safety');root.wait_for(timeout=60000)
    assert page.locator('[data-testid="stException"]').count()==0
    icons=root.locator('.legacy-safety-icon img')
    assert icons.count()>10
    root.locator('.legacy-safety-icon').first.scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'legacy-ko-desktop.png'))
    for width in [390,320]:
        page.set_viewport_size({'width':width,'height':900})
        icons.first.scroll_into_view_if_needed()
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        assert icons.first.evaluate('(e)=>e.complete && e.naturalWidth>0')
        page.emulate_media(reduced_motion='reduce')
        assert icons.first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
        # No content uses entrance animations or fades.
        assert root.locator('[data-testid="stMarkdownContainer"] p').first.evaluate('(e)=>getComputedStyle(e).opacity')=='1'
        page.screenshot(path=str(OUT/f'legacy-ko-{width}.png'))
    disclosures=root.locator('[data-testid="stExpander"] details')
    assert disclosures.count()>=3
    assert all(disclosures.nth(i).get_attribute('open') is not None for i in range(3))
    summary=disclosures.first.locator('summary');summary.focus();page.keyboard.press('Enter')
    expect(disclosures.first).not_to_have_attribute('open','')
    page.keyboard.press('Space');expect(disclosures.first).to_have_attribute('open','')
    summary.scroll_into_view_if_needed();page.screenshot(path=str(OUT/'legacy-ko-effects-mobile.png'))
    page.set_viewport_size({'width':1440,'height':1050})
    page.get_by_text('English',exact=True).click()
    page.wait_for_timeout(800)
    assert page.locator('[data-testid="stException"]').count()==0
    root.locator('.legacy-safety-icon').first.scroll_into_view_if_needed()
    page.screenshot(path=str(OUT/'legacy-en-desktop.png'))
    b.close()
print('Legacy Chromium: ko/en, 1440/390/320 px, disclosures, icons, reduced motion and overflow passed')
