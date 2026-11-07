# -*- coding: utf-8 -*-
"""Grava o hero do celular (tres cenas em laco, 900x900, 60 fps), o poster, a capa de link e o favicon. Uso: python tools/gerar_video.py [poster video]"""
import base64, io, shutil, subprocess, sys
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
S = Path(__file__).resolve().parent.parent
ff = shutil.which('ffmpeg'); FPS = 60; L = 900
Q = sys.argv[1:] or ['poster', 'video']
b64 = lambda n: 'data:image/webp;base64,' + base64.b64encode((S / f'assets/img/hero/{n}.webp').read_bytes()).decode()
def abre(p):
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/hero.js').read_text(encoding='utf8'))
    nomes = ['p-saudade', 'asas', 'p-mae', 'mae', 'p-recomeco', 'borboleta']
    g.evaluate("""async(a)=>{const C=heroMay.CENAS;window.T=heroMay(document.getElementById('c'),{guardar:true,n:260000,cenas:[C[0],C[3],C[4]]});T.tamanho(%d,%d);
      for(let i=0;i<a.length;i++){const m=new Image();m.src=a[i];await m.decode();T.carrega(i,m)}}""" % (L, L), [b64(n) for n in nomes])
    return b, g
OP = '{lado:%d,pt:1.55,a:.3}' % (L * .96)
def foto(g, t, q=.96):
    d = g.evaluate(f"(T.desenha({t},{OP}),document.getElementById('c').toDataURL('image/jpeg',{q}))")
    return base64.b64decode(d.split(',', 1)[1])
with sync_playwright() as p:
    b, g = abre(p)
    PAR = g.evaluate('heroMay.PAR'); D = g.evaluate('T.D')
    if 'poster' in Q:
        t = PAR * 2 + D['pal'] + D['ida'] + 1.6
        for k in range(14): foto(g, t - (14 - k) / 30)
        Image.open(io.BytesIO(foto(g, t, .98))).save(S / 'assets/img/hero/poster.webp', quality=88, method=6)
        print('poster', flush=True)
    b.close()
    if 'video' in Q:
        mp4 = S / 'assets/video/hero.mp4'; n = int(PAR * 3 * FPS); BL = 500
        tmp = S.parent / '_ref/hero-tmp.mp4'
        enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-profile:v', 'high', '-color_range', 'tv', '-r', str(FPS), '-movflags', '+faststart', '-an', str(tmp)], stdin=subprocess.PIPE)
        for i0 in range(0, n, BL):
            b, g = abre(p)  # navegador novo a cada bloco: o longo estoura a memoria da pagina
            for k in range(30): foto(g, (i0 - 30 + k) / FPS + (PAR * 3 if i0 == 0 else 0))
            for i in range(i0, min(n, i0 + BL)): enc.stdin.write(foto(g, i / FPS))
            b.close(); print(i0 + BL, n, flush=True)
        enc.stdin.close(); enc.wait(); shutil.move(str(tmp), str(mp4)); print(mp4.name, round(mp4.stat().st_size / 1e6, 2), 'MB', flush=True)
