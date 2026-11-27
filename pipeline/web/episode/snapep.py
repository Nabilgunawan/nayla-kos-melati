import sys,time,base64
from playwright.sync_api import sync_playwright
ts=[float(x) for x in sys.argv[1].split(',')]
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files","--autoplay-policy=no-user-gesture-required"])
    pg=b.new_page(viewport={'width':1200,'height':900})
    pg.on('console',lambda m: print('console',m.type,m.text[:300]) if m.type in('error',) else None); pg.on('pageerror',lambda e: print('PAGEERR',e))
    t=time.time(); pg.goto('file:///tmp/w/ep5/render_ep05/render_ep05.html'); pg.wait_for_function('window.__ready',timeout=280000); print('ready',round(time.time()-t,1))
    for x in ts:
        d=pg.evaluate(f'__snap({x},540)'); open(f'/tmp/w/ep5/snap_{x}.png','wb').write(base64.b64decode(d.split(',')[1]))
    b.close()
