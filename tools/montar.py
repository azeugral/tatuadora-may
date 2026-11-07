# -*- coding: utf-8 -*-
"""Monta index.html a partir de tools/modelo.html + tools/dados.py, com previa embutida em cada foto. Uso: python tools/montar.py"""
import base64, io, json, sys
from pathlib import Path
import numpy as np
from PIL import Image
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref'
sys.path.insert(0, str(S / 'tools'))
import dados
SENT = dict(dados.SENT)
LEGS = [dict(p='saudade', t='Tatuagem real: homenagem ao pai'), dict(p='amizade', t='Tatuagem real: cada amiga desenhou uma flor'), dict(p='amor próprio', t='Arte da May: bem me quero'), dict(p='amor de mãe', t='Tatuagem real: mãe e filho'), dict(p='recomeço', t='Tatuagem real: tudo tem seu tempo')]

def previa(f):
    i = Image.open(f).convert('RGB').resize((16, 20), Image.LANCZOS)
    b = io.BytesIO(); i.save(b, 'WEBP', quality=40)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def tile(i, p):
    f = S / f"assets/img/p/{p['id']}.webp"
    return (f'<button class="peca" type="button" data-i="{i}" data-s="{p["s"]}" aria-label="Abrir {p["leg"]}" style="background:url({previa(f)}) center/cover">'
            f'<img src="assets/img/p/{p["id"]}.webp" alt="Tatuagem: {p["leg"]}" width="640" height="800" loading="lazy" draggable="false"><span>{p["leg"]}</span></button>')

# arte da acao de Natal: bem me quero em ouro sobre o verde da pagina
m = np.asarray(Image.open(S / 'assets/img/hero/bemmequero.webp').convert('L')).astype(np.float32) / 255
c = Image.new('RGB', (1080, 1350), (17, 44, 40)); o = Image.new('RGB', (1024, 1024), (232, 200, 132))
c.paste(o, (28, 163), Image.fromarray((m ** .8 * 255).astype(np.uint8)))
c.save(S / 'assets/img/acao.webp', quality=88, method=6)
n = Image.open(R / 'ig/fotos/191_0.jpg').convert('RGB'); w, h = n.size; k = min(w, int(h * .8)); n = n.crop(((w - k) // 2, 0, (w - k) // 2 + k, int(k * 1.25))).resize((1080, 1350), Image.LANCZOS)
a = np.asarray(n).astype(np.float32); me = a.reshape(-1, 3).mean(0); a = np.clip(a * (1 + (me.mean() / me - 1) * .4), 0, 255); Image.fromarray(a.astype(np.uint8)).save(S / 'assets/img/o/191_0.webp', quality=80, method=6)

filtros = '<button class="tudo" type="button" data-f="tudo" aria-pressed="true">tudo</button>' + ''.join(f'<button type="button" data-f="{k}" aria-pressed="false">{v.lower()}</button>' for k, v in dados.SENT)
h = (S / 'tools/modelo.html').read_text(encoding='utf8')
rep = {
 '{{FILTROS}}': filtros, '{{GRADE}}': ''.join(tile(i, p) for i, p in enumerate(dados.P)),
 '{{OPC}}': ''.join(f'<option value="{k}">{v}</option>' for k, v in dados.SENT),
 '{{COB_TABS}}': ''.join(f'<button type="button" aria-pressed="{str(i == 0).lower()}">{c["leg"]}</button>' for i, c in enumerate(dados.C)),
 '{{COB1}}': dados.C[0]['id'], '{{COB1T}}': dados.C[0]['t'], '{{NEGRA}}': '191_0',
 '{{PECAS}}': json.dumps([dict(id=p['id'], s=p['s'], leg=p['leg'], t=p['t'], fotos=p['fotos']) for p in dados.P], ensure_ascii=False),
 '{{COBS}}': json.dumps([dict(id=c['id'], t=c['t']) for c in dados.C], ensure_ascii=False), '{{SENTJ}}': json.dumps(SENT, ensure_ascii=False),
 '{{LEGS}}': json.dumps(LEGS, ensure_ascii=False), '{{V}}': '5',
}
for k, v in rep.items(): h = h.replace(k, v)
(S / 'index.html').write_text(h, encoding='utf8')
print('index.html', round(len(h) / 1024), 'KB')
