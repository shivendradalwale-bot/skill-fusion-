import asyncio, json
from playwright.async_api import async_playwright
URL='http://127.0.0.1:8765/index(7).html'
async def main():
  out={'console_errors':[],'page_errors':[],'csp_violations':[],'requests':[],'tests':{}}
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--enable-webgl','--use-gl=swiftshader','--no-sandbox'])
    for name,w,h in [('desktop',1440,1000),('mobile',390,844)]:
      page=await b.new_page(viewport={'width':w,'height':h})
      page.on('console', lambda m,n=name: out['console_errors'].append({'viewport':n,'type':m.type,'text':m.text}) if m.type=='error' else None)
      page.on('pageerror', lambda e,n=name: out['page_errors'].append({'viewport':n,'text':str(e)}))
      page.on('requestfailed', lambda r,n=name: out['requests'].append({'viewport':n,'url':r.url,'failure':r.failure}))
      page.on('console', lambda m,n=name: out['csp_violations'].append({'viewport':n,'text':m.text}) if 'Content Security Policy' in m.text else None)
      await page.goto(URL,wait_until='networkidle',timeout=30000)
      await page.wait_for_timeout(1200)
      t=out['tests'][name]={}
      t['horizontal_overflow']=await page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
      t['page_errors']=len(out['page_errors'])
      t['canvas_count']=await page.locator('canvas').count()
      t['visible_canvas_count']=await page.locator('canvas').evaluate_all("els => els.filter(e => getComputedStyle(e).display !== 'none').length")
      t['missing_anchors']=[]
      for href in await page.locator('a[href^="#"]').evaluate_all("els=>els.map(e=>e.getAttribute('href'))"):
        if href!='#' and await page.locator(href).count()==0: t['missing_anchors'].append(href)
      t['new_tab_without_noopener']=await page.locator('a[target="_blank"]:not([rel~="noopener"])').count()
      t['mobile_menu_ok']=True
      if await page.locator('#hamburger').is_visible():
        await page.locator('#hamburger').click()
        t['mobile_menu_open']=await page.locator('#mobile-menu.open').count()==1 and await page.locator('#hamburger').get_attribute('aria-expanded')=='true'
        await page.locator('#mobile-menu a').first.click()
        t['mobile_menu_close']=await page.locator('#mobile-menu.open').count()==0 and await page.locator('#hamburger').get_attribute('aria-expanded')=='false'
      form=page.locator('#enquiry-form')
      t['form_present']=await form.count()==1
      t['labels_associated']=await page.locator('label[for]').count()>=5
      t['empty_form_invalid']=not await page.evaluate("document.querySelector('#enquiry-form').checkValidity()")
      await page.close()
    await b.close()
  print(json.dumps(out,indent=2))
asyncio.run(main())
