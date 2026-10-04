import asyncio,sys
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':int(sys.argv[3]) if len(sys.argv)>3 else 1440,'height':900})
    await pg.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://127.0.0.1') or r.request.url.startswith('data:') else r.abort())
    await pg.goto(sys.argv[1]); await pg.wait_for_timeout(500); await pg.screenshot(path=sys.argv[2])
    await b.close()
asyncio.run(m())
