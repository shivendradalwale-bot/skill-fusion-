import asyncio, json
from playwright.async_api import async_playwright
URL='http://127.0.0.1:8765/index(7).html'
async def main():
  out={}
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--enable-webgl','--use-gl=swiftshader','--no-sandbox'])
    page=await b.new_page(viewport={'width':390,'height':844})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    await page.goto(URL,wait_until='networkidle')
    f=page.locator('#enquiry-form')
    fields=f.locator('input')
    await fields.nth(0).fill('QA User')
    await fields.nth(1).fill('9860706062')
    await fields.nth(2).fill('qa@example.com')
    await f.locator('select').select_option(label='Programming Courses')
    await f.locator('textarea').fill('Please contact me.')
    await f.locator('button[type=submit]').click()
    await page.wait_for_timeout(500)
    out['errors']=errors
    out['page_url_after_submit']=page.url
    out['fallback_links']=await page.locator('#form-note a').evaluate_all('els=>els.map(e=>e.getAttribute("href"))')
    out['note']=await page.locator('#form-note').inner_text()
    await b.close()
  print(json.dumps(out,indent=2))
asyncio.run(main())
