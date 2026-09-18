import asyncio, json
from playwright.async_api import async_playwright
URL='http://127.0.0.1:8765/index(7).html'
async def main():
  out={'errors':[],'requests':[],'tests':{}}
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--enable-webgl','--use-gl=swiftshader','--no-sandbox'])
    for name,w,h in [('desktop',1440,1000),('mobile',390,844)]:
      page=await b.new_page(viewport={'width':w,'height':h})
      page.on('console',lambda m,n=name:out['errors'].append({'viewport':n,'type':m.type,'text':m.text}) if m.type=='error' else None)
      page.on('pageerror',lambda e,n=name:out['errors'].append({'viewport':n,'type':'pageerror','text':str(e)}))
      page.on('requestfailed',lambda r,n=name:out['requests'].append({'viewport':n,'url':r.url,'failure':r.failure}))
      await page.goto(URL,wait_until='networkidle',timeout=30000); await page.wait_for_timeout(1000)
      t=out['tests'][name]={}
      t['overflow']=await page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
      t['canvas_count']=await page.locator('canvas').count(); t['visible_canvas_count']=await page.locator('canvas').evaluate_all("els=>els.filter(e=>getComputedStyle(e).display!='none').length")
      t['script_loaded']=await page.evaluate("typeof window.THREE === 'object' && typeof window.gsap === 'object'")
      t['stylesheet_loaded']=await page.evaluate("Array.from(document.styleSheets).some(s=>s.href && s.href.endsWith('/styles.css'))")
      hrefs=await page.locator('a[href^="#"]').evaluate_all('els=>els.map(e=>e.getAttribute("href")).filter(h=>h!=="#")')
      anchor_results=[]
      for h in hrefs:
        anchor_results.append(await page.locator(h).count()>0)
      t['anchors_ok']=all(anchor_results)
      if await page.locator('#hamburger').is_visible():
        await page.locator('#hamburger').click(); t['menu_open']=await page.locator('#mobile-menu.open').count()==1; await page.locator('#mobile-menu a').first.click(); t['menu_close']=await page.locator('#mobile-menu.open').count()==0
      t['form']=await page.locator('#enquiry-form').count()==1
      await page.close()
    await b.close()
  print(json.dumps(out,indent=2))
asyncio.run(main())
