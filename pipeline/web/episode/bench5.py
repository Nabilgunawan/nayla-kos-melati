import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--allow-file-access-from-files"])
    pg=b.new_page(); pg.on('pageerror',lambda e: print('PAGEERR',e))
    pg.goto('file:///tmp/w/ep5/render_ep05/render_ep05.html'); pg.wait_for_function('window.__ready',timeout=200000)
    pg.evaluate('__snap(53,270)')
    print('ms per frame (pose+tv, 24 frame, tanpa render 3D):',pg.evaluate('''async()=>{ const t0=performance.now(); for(let i=0;i<24;i++){ await window.__poseOnly(53+i/24); } return (performance.now()-t0)/24; }'''))
    b.close()
