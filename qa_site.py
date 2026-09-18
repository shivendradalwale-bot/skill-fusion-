import asyncio, json, os, sys
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:8765/index(7).html'

async def run():
    results = {'console': [], 'page_errors': [], 'tests': {}, 'screenshots': []}
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--enable-webgl', '--use-gl=swiftshader', '--no-sandbox'])
        for name, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
            page = await browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=1)
            page.on('console', lambda msg: results['console'].append({'viewport': name, 'type': msg.type, 'text': msg.text}) if msg.type in ('error','warning') else None)
            page.on('pageerror', lambda exc: results['page_errors'].append({'viewport': name, 'text': str(exc)}))
            await page.goto(URL, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1500)
            results['tests'][name] = {}
            results['tests'][name]['title'] = await page.title()
            results['tests'][name]['body_scroll_width'] = await page.evaluate('document.body.scrollWidth')
            results['tests'][name]['viewport_width'] = await page.evaluate('window.innerWidth')
            results['tests'][name]['horizontal_overflow'] = await page.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            results['tests'][name]['canvas_count'] = await page.locator('canvas').count()
            results['tests'][name]['webgl_canvas_visible'] = await page.locator('canvas').evaluate_all("els => els.filter(e => getComputedStyle(e).display !== 'none').length")
            # all in-page anchors resolve to an element
            anchors = await page.locator('a[href^="#"]').evaluate_all("els => els.map(a => ({href:a.getAttribute('href'), text:a.innerText.trim()}))")
            missing = []
            for a in anchors:
                if a['href'] != '#' and await page.locator(a['href']).count() == 0:
                    missing.append(a)
            results['tests'][name]['missing_anchor_targets'] = missing
            # desktop/mobile nav
            hamburger = page.locator('#hamburger')
            results['tests'][name]['hamburger_visible'] = await hamburger.is_visible()
            if await hamburger.is_visible():
                await hamburger.click()
                results['tests'][name]['mobile_menu_open_after_click'] = await page.locator('#mobile-menu.open').count() == 1
                await page.locator('#mobile-menu a').first.click()
                results['tests'][name]['mobile_menu_closed_after_nav'] = await page.locator('#mobile-menu.open').count() == 0
            # form validation and safe submit behavior (fill then submit; prevent navigation if app handles it)
            form = page.locator('#enquiry-form')
            results['tests'][name]['form_exists'] = await form.count() == 1
            if await form.count():
                results['tests'][name]['form_required_fields'] = await form.locator('[required]').count()
                results['tests'][name]['form_valid_empty'] = await page.evaluate("document.querySelector('#enquiry-form').checkValidity()")
                fields = form.locator('input')
                await fields.nth(0).fill('QA User')
                await fields.nth(1).fill('9876543210')
                await fields.nth(2).fill('qa@example.com')
                await form.locator('select').select_option(label='Website Development')
                results['tests'][name]['form_valid_filled'] = await page.evaluate("document.querySelector('#enquiry-form').checkValidity()")
            # a11y basics
            results['tests'][name]['images_without_alt'] = await page.locator('img:not([alt])').count()
            results['tests'][name]['buttons_without_name'] = await page.locator('button').evaluate_all("els => els.filter(e => !(e.getAttribute('aria-label') || e.innerText.trim())).length")
            await page.screenshot(path=f'/home/ubuntu/{name}_qa.png', full_page=True)
            results['screenshots'].append(f'/home/ubuntu/{name}_qa.png')
            await page.close()
        await browser.close()
    print(json.dumps(results, indent=2))

asyncio.run(run())
