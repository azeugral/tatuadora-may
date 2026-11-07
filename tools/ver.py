# -*- coding: utf-8 -*-
"""Tira prints do site. Uso: python tools/ver.py [w h nome [touch]]..."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf8')
S = Path(__file__).resolve().parent.parent; O = S.parent / '_ref/prints'; O.mkdir(exist_ok=True)
URL = 'http://localhost:8840/'
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    for w, h, n, tq in ((1440, 900, 'pc', 0), (390, 844, 'cel', 1)):
        c = b.new_context(viewport={'width': w, 'height': h}, has_touch=bool(tq), is_mobile=bool(tq), device_scale_factor=1)
        g = c.new_page(); g.add_init_script('window.__n=30000'); er = []
        g.on('pageerror', lambda e: er.append('JS ' + str(e)[:300])); g.on('console', lambda m: er.append('CON ' + m.text[:200]) if m.type == 'error' else None)
        g.on('response', lambda r: er.append(f'{r.status} ' + r.url[-60:]) if r.status >= 400 else None)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(5000 if not tq else 2500)
        g.screenshot(path=str(O / f'{n}-hero.jpg'), type='jpeg', quality=82)
        g.add_style_tag(content='.sobe{opacity:1!important;transform:none!important;transition:none!important}')
        g.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
        H = g.evaluate('document.documentElement.scrollHeight')
        y = 0
        while y < H:
            g.evaluate(f'scrollTo(0,{y})'); g.wait_for_timeout(120); y += h
        for sel in ('#coberturas', '#depoimentos', '#acao', '#orcamento', '#faq', '.rodape'):
            g.evaluate(f"document.querySelector('{sel}').scrollIntoView({{behavior:'instant'}})"); g.wait_for_timeout(350)
            g.locator(sel).screenshot(path=str(O / f"{n}-s-{sel.strip('#.')}.jpg"), type='jpeg', quality=80)
        g.evaluate('scrollTo(0,0)'); g.wait_for_timeout(900)
        g.evaluate("(()=>{const t=document.getElementById('topo');t.style.position='absolute'})()")
        g.screenshot(path=str(O / f'{n}-tudo.jpg'), type='jpeg', quality=70, full_page=True)
        print(n, H, er[:12])
        c.close()
    b.close()
