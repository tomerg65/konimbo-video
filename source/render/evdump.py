import asyncio,json,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page()
    await pg.route('**/*', lambda rt: rt.continue_() if rt.request.url.startswith(('http://127.0.0.1','data:','blob:')) else rt.abort())
    await pg.goto('http://127.0.0.1:8765/index.html')
    for n in ('long','short'):
      e=await pg.evaluate(f'events("{n}")'); json.dump(e,open(f'ev_{n}.json','w')); print(n,e['duration'],len(e['clicks']))
    await b.close()
asyncio.run(m())
