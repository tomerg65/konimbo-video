import asyncio, sys, subprocess, os, json, time, pathlib
SCENES = pathlib.Path(__file__).resolve().parent.parent / 'scenes'
PORT = 8765
from playwright.async_api import async_playwright

# שימוש:
#   python3 render.py video long  out.mp4    רינדור גרסת 2 הדקות (בלי אודיו)
#   python3 render.py video short out.mp4    רינדור גרסת 60 השניות
#   python3 render.py stills long 5,30,60 out_dir   צילום פריימים בודדים לבדיקה
async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SCENES, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
    mode, tl = sys.argv[1], sys.argv[2]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--disable-background-networking','--disable-component-update'], executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome' if os.path.exists('/opt/pw-browsers/chromium-1194/chrome-linux/chrome') else None)
        pg = await b.new_page(viewport={'width':1920,'height':1080})
        pg.on('console', lambda m: print('console:', m.text) if m.type in ('error','warning') else None)
        pg.on('pageerror', lambda e: print('PAGEERROR', e))
        await pg.route('**/*', lambda rt: rt.continue_() if rt.request.url.startswith(('http://127.0.0.1','data:','blob:')) else rt.abort())
        await pg.goto('http://127.0.0.1:8765/index.html')
        await pg.evaluate('setup()')
        total = await pg.evaluate(f'total("{tl}")')
        if mode == 'stills':
            ts = [float(x) for x in sys.argv[3].split(',')]
            out = sys.argv[4]; os.makedirs(out, exist_ok=True)
            for t in ts:
                await pg.evaluate(f'renderAt({t},"{tl}")'); await pg.evaluate('Promise.all([...document.querySelectorAll("iframe")].filter(f=>f.offsetParent).map(f=>f.contentDocument.fonts.ready))')
                await pg.screenshot(path=f'{out}/{tl}_{t:07.2f}.jpg', type='jpeg', quality=85)
            print('total', total)
        else:
            out = sys.argv[3]; fps = int(sys.argv[4]) if len(sys.argv) > 4 else 30
            n = int(round(total * fps))
            ff = subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate',str(fps),'-c:v','mjpeg','-i','-',
                                   '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p',out], stdin=subprocess.PIPE)
            for i in range(n):
                t = i / fps
                await pg.evaluate(f'renderAt({t},"{tl}")'); await pg.evaluate('Promise.all([...document.querySelectorAll("iframe")].filter(f=>f.offsetParent).map(f=>f.contentDocument.fonts.ready))')
                buf = await pg.screenshot(type='jpeg', quality=93)
                ff.stdin.write(buf)
                if i % 300 == 0: print(tl, i, '/', n, flush=True)
            ff.stdin.close(); ff.wait()
            print('done', out, total)
        await b.close()
    srv.terminate()
asyncio.run(main())
