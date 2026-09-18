import asyncio
from playwright.async_api import async_playwright
URL='http://127.0.0.1:8765/index(7).html'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--enable-webgl','--use-gl=swiftshader','--no-sandbox'])
    page=await b.new_page(viewport={'width':390,'height':844})
    bad=[]
    page.on('response', lambda r: print('404',r.url) if r.status==404 else None)
    await page.goto(URL,wait_until='networkidle')
    await page.wait_for_timeout(1000)
    bad=await page.evaluate('''() => Array.from(document.querySelectorAll('*')).map(el => { const r=el.getBoundingClientRect(); return {tag:el.tagName,id:el.id,cls:el.className,x:r.x,right:r.right,width:r.width,text:(el.innerText||'').trim().slice(0,60)}; }).filter(x => x.right > innerWidth + 1 || x.x < -1).slice(0,30)''')
    print('BAD_ELEMENTS')
    for x in bad: print(x)
    await b.close()
asyncio.run(main())
