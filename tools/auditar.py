# -*- coding: utf-8 -*-
"""Auditoria: estouro, corte de texto, corte de fonte, eixo, hero e funcoes, em 13 tamanhos. Uso: python tools/auditar.py [url]"""
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf8')
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8840/')
VPS = [(320, 568, 1), (360, 640, 1), (360, 740, 1), (390, 844, 1), (430, 932, 1), (600, 900, 1), (768, 1024, 1), (844, 390, 1), (1024, 768, 0), (1280, 720, 0), (1440, 900, 0), (1920, 1080, 0), (2560, 1300, 0)]
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
JS = r"""
() => {
  const W = document.documentElement.clientWidth, H = innerHeight, out = [];
  if (document.documentElement.scrollWidth > W) out.push('ESTOURO pagina ' + document.documentElement.scrollWidth + '>' + W);
  const vis = el => { const c = getComputedStyle(el); return c.display !== 'none' && c.visibility !== 'hidden' && el.getClientRects().length; };
  document.querySelectorAll('h2,h3,p,a,button,span,small,blockquote,cite,li,label,summary,figcaption,em,b').forEach(el => {
    if (el.closest('[hidden],.sr,.saltar,.menu,.lb') || !vis(el)) return;
    const cs = getComputedStyle(el), r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    const nome = el.tagName + '.' + el.className + ' "' + (el.textContent || '').trim().slice(0, 26) + '"';
    if (r.right > W + 1 || r.left < -1) out.push('FORA ' + nome + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
    if (el.scrollWidth > el.clientWidth + 1 && cs.display !== 'inline' && el.clientWidth > 0) out.push('CORTE-X ' + nome + ' ' + el.scrollWidth + '>' + el.clientWidth);
    if (cs.overflow !== 'visible' && el.scrollHeight > el.clientHeight + 1 && cs.display !== 'inline') out.push('CORTE-Y ' + nome);
  });
  // botao nunca quebra linha
  document.querySelectorAll('.bt').forEach(b => { if (!vis(b) || b.closest('[hidden],.menu,.lb')) return; if (b.getBoundingClientRect().height > 64) out.push('BOTAO quebrou "' + b.textContent + '"'); });
  // eixo das secoes
  document.querySelectorAll('.cab,.filtros,.grade,.etapas,.pele-g,.cics,.cob-par,.deps,.form,.faq').forEach(e => { if (!vis(e)) return; const r = e.getBoundingClientRect(); if (Math.abs((r.left + r.right) / 2 - W / 2) > 1.5) out.push('EIXO ' + e.className); });
  // grades: todas as celulas iguais
  document.querySelectorAll('.grade,.etapas,.cics,.cob-par').forEach(g => { const c = [...g.children].filter(vis); if (c.length < 2) return; const a = c[0].getBoundingClientRect(); c.forEach(x => { if (Math.abs(x.getBoundingClientRect().width - a.width) > 1) out.push('GRADE desigual ' + g.className); }); });
  // hero cabe
  const h = document.querySelector('.hero').getBoundingClientRect();
  document.querySelectorAll('.hero .bt').forEach(b => { if (!vis(b)) return; const r = b.getBoundingClientRect(); if (r.bottom > h.bottom + 1) out.push('HERO botao abaixo ' + Math.round(r.bottom) + '>' + Math.round(h.bottom)); });
  if (W >= 1024) {
    const es = document.querySelector('.hero-lado.e').getBoundingClientRect(), dr = document.querySelector('.hero-lado.d').getBoundingClientRect();
    if (Math.abs((W / 2 - es.right) - (dr.left - W / 2)) > 2) out.push('HERO lados fora do eixo ' + Math.round(es.right) + '/' + Math.round(dr.left));
    if (es.left < 0 || dr.right > W) out.push('HERO lado cortado');
    if (Math.abs(es.width - dr.width) > 1) out.push('HERO larguras');
    const a = parseFloat(getComputedStyle(document.querySelector('.hero')).getPropertyValue('--art')) || 0;
    if (es.width < 200) out.push('HERO coluna estreita ' + Math.round(es.width));
    if (es.top < 78) out.push('HERO lado sob a barra');
  } else {
    const f = document.querySelector('.hero-fundo').getBoundingClientRect();
    if (f.height < 200) out.push('HERO arte baixa ' + Math.round(f.height));
  }
  // corte de fonte: escrita precisa de folga
  document.querySelectorAll('.olho,.cob-q,.cita p').forEach(e => { if (!vis(e)) return; const c = getComputedStyle(e); if (parseFloat(c.lineHeight) < parseFloat(c.fontSize) * 1.2) out.push('ESCRITA apertada ' + e.textContent); });
  return [...new Set(out)];
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    tot = 0
    for w, h, tq in VPS:
        c = b.new_context(viewport={'width': w, 'height': h}, has_touch=bool(tq), is_mobile=bool(tq), device_scale_factor=1)
        g = c.new_page(); g.add_init_script('window.__n=30000'); er = []
        g.on('pageerror', lambda e: er.append('JS ' + str(e)[:200]))
        g.on('console', lambda m: er.append('CON ' + m.text[:160]) if m.type == 'error' else None)
        g.on('response', lambda r: er.append(f'{r.status} ' + r.url[-50:]) if r.status >= 400 else None)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(1000)
        o = g.evaluate(JS) + er
        print(f'{w}x{h}', 'ok' if not o else '')
        for x in o: print('   ', x)
        tot += len(o); c.close()
    print('TOTAL auditoria', tot)
    R = []
    def ok(n, v, x=''):
        R.append(bool(v)); print('OK ' if v else 'FALHOU', n, x)
    c = b.new_context(viewport={'width': 1440, 'height': 900}); g = c.new_page(); g.add_init_script('window.__n=30000')
    g.goto(URL); g.wait_for_timeout(2500)
    ok('canvas do hero', g.evaluate("!!document.querySelector('#heroFundo canvas')"))
    ok('12 de cara', g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length") == 12)
    g.click('#filtros [data-f=fe]'); g.wait_for_timeout(200)
    ok('filtro fe', g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).every(p=>p.dataset.s=='fe')"))
    ok('mais some no filtro', g.evaluate("document.querySelector('#verMais').parentNode.hidden"))
    g.evaluate("document.querySelector('.peca:not([hidden])').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(300)
    g.click('.peca:not([hidden])'); g.wait_for_timeout(500)
    ok('lightbox abre', not g.evaluate("document.querySelector('#lb').hidden"))
    ok('lightbox foto', g.evaluate("(()=>{const i=document.querySelector('#lbI');return i.complete&&i.naturalWidth>0})()"))
    g.keyboard.press('ArrowRight'); g.wait_for_timeout(300)
    leg = g.inner_text('#lbL')
    g.click('#lbQ'); g.wait_for_timeout(1200)
    ok('quero uma assim', leg in g.input_value('#fIdeia') and g.evaluate("document.querySelector('#lb').hidden"), leg)
    ok('sentimento marcado', g.input_value('#fSent') == 'fe')
    g.evaluate("document.querySelector('#form button[type=submit]').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(300)
    g.click('#form button[type=submit]'); g.wait_for_timeout(200)
    ok('erro sem nome', not g.evaluate("document.querySelector('#fErro').hidden"))
    g.fill('#fNome', 'Teste'); g.fill('#fLugar', 'Antebraço'); g.fill('#fTam', '12 cm')
    with c.expect_page() as pop: g.click('#form button[type=submit]')
    u = unquote(pop.value.url); pop.value.close()
    ok('whatsapp', '5575982071367' in u and 'Antebraço' in u, u[:110])
    g.evaluate("document.querySelector('#cobTabs').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(300)
    g.click('#cobTabs button:nth-child(2)'); g.wait_for_timeout(400)
    ok('cobertura troca', 'corvo' in g.evaluate("document.querySelector('#cobA').src"))
    g.evaluate("document.querySelector('.etapa video').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(1500)
    ok('etapas tocam', g.evaluate("[...document.querySelectorAll('.etapa video')].filter(v=>!v.paused).length") >= 2)
    c.close()
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(2500)
    ok('video no celular', g.evaluate("(()=>{const v=document.querySelector('#heroFundo video');return v&&!v.paused&&v.loop})()"))
    n0 = g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length")
    g.evaluate("document.querySelector('#verMais').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(200); g.tap('#verMais'); g.wait_for_timeout(300)
    n1 = g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length")
    ok('ver todas', n0 == 8 and n1 == 32, f'{n0}->{n1}')
    g.evaluate("window.scrollTo({top:0,behavior:'instant'})"); g.wait_for_timeout(200); g.tap('#btMenu'); g.wait_for_timeout(200)
    ok('menu abre', not g.evaluate("document.querySelector('#menu').hidden"))
    g.tap('.menu a[href="#sobre"]'); g.wait_for_timeout(1200)
    ok('menu fecha e rola', g.evaluate("document.querySelector('#menu').hidden && scrollY>500"))
    print('FUNCIONAL', sum(R), '/', len(R))
    b.close()
