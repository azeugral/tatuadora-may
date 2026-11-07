# -*- coding: utf-8 -*-
"""Favicon (a borboleta-escaravelho dela) e capa de link com composicao centrada, segura para recorte quadrado."""
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parent.parent
BG = (11, 15, 14)
b = Image.open(S / 'assets/img/borb.webp').convert('RGBA')
f = Image.new('RGB', (256, 256), BG); e = 224 / max(b.size); r = b.resize((round(b.width * e), round(b.height * e)), Image.LANCZOS)
f.paste(r, ((256 - r.width) // 2, (256 - r.height) // 2), r); f.save(S / 'assets/img/favicon.png')
og = Image.new('RGB', (1200, 630), BG)
p = Image.open(S / 'assets/img/hero/poster.webp').convert('RGB').resize((630, 630), Image.LANCZOS)
og.paste(p, (285, 0)); og.save(S / 'assets/img/og.jpg', quality=88)
print('ok')
