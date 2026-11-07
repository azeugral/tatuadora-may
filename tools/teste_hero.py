# -*- coding: utf-8 -*-
import base64, io, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref'
b64 = lambda n: 'data:image/webp;base64,' + base64.b64encode((S / f'assets/img/hero/{n}.webp').read_bytes()).decode()
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    er = []; g.on('pageerror', lambda e: er.append(str(e))); g.on('console', lambda m: print('CON', m.text[:300]))
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/hero.js').read_text(encoding='utf8'))
    nomes = ['p-saudade', 'asas', 'p-amizade', 'buque']
    g.evaluate("""async(a)=>{window.T=heroMay(document.getElementById('c'),{guardar:true,n:260000,cenas:heroMay.CENAS.slice(0,2)});T.tamanho(1000,1000);
      for(let i=0;i<a.length;i++){const m=new Image();m.src=a[i];await m.decode();T.carrega(i,m)}}""", [b64(n) for n in nomes])
    print('flut', g.evaluate('T.flut'), er)
    tempos = [.5, 2.2, 2.8, 3.4, 4.0, 6, 8.4, 9.2, 10.0, 12.4]
    fol = Image.new('RGB', (5 * 500, 2 * 500))
    for i, t in enumerate(tempos):
        # varios quadros para o rastro assentar
        d = g.evaluate(f"(()=>{{for(let k=8;k>=0;k--)T.desenha({t}-k/30,{{lado:900,pt:1.8,a:.3}});return document.getElementById('c').toDataURL('image/jpeg',.95)}})()")
        im = Image.open(io.BytesIO(base64.b64decode(d.split(',', 1)[1])))
        fol.paste(im.resize((500, 500), Image.LANCZOS), ((i % 5) * 500, (i // 5) * 500))
        if t == 6: im.save(R / 'tinta/_h6.jpg', quality=92)
    fol.save(R / 'tinta/_hero.jpg', quality=88)
    print(er)
    b.close()
