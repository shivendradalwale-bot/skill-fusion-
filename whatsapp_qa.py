import asyncio, json
from playwright.async_api import async_playwright
URL='http://127.0.0.1:8765/index(7).html'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    page=await b.new_page()
    await page.goto(URL,wait_until='domcontentloaded')
    f=page.locator('#enquiry-form'); fields=f.locator('input')
    await fields.nth(0).fill('QA Customer'); await fields.nth(1).fill('9876543210'); await fields.nth(2).fill('qa@example.com')
    await f.locator('select').select_option(label='Website Development'); await f.locator('textarea').fill('Test WhatsApp enquiry')
    await page.evaluate("document.querySelector('#enquiry-form').addEventListener('submit', e => e.preventDefault(), {once:true})")
    # Inspect implementation contract without navigating externally.
    result=await page.evaluate("""() => {
      const f=document.querySelector('#enquiry-form');
      return {phone:f.elements.phone.value, email:f.elements.email.value, interest:f.elements.interest.value, message:f.elements.message.value, target:'https://wa.me/916361435651'};
    }""")
    print(json.dumps(result,indent=2)); await b.close()
asyncio.run(main())
