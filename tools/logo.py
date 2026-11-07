# -*- coding: utf-8 -*-
"""Logo real da May: recorta do destaque Pele (fundo quase preto) e tira o fundo preservando o dourado foil e o escaravelho."""
from pathlib import Path
import numpy as np
from PIL import Image
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref'
im = Image.open(R / 'hl/pele/004.jpg').convert('RGB'); s = im.width / 1125
c = im.crop((int(370 * s), int(1650 * s), int(770 * s), int(1868 * s)))
ESC = 4
c = c.resize((c.width * ESC, c.height * ESC), Image.BICUBIC)
a = np.asarray(c).astype(np.float32) / 255
fundo = np.median(a[:40].reshape(-1, 3), 0)
d = np.clip(a - fundo, 0, 1)
al = np.clip((d.max(2) - .035) / .30, 0, 1)
al = al ** .85
rgb = np.clip(d / np.maximum(al[..., None], .03), 0, 1)
# dourado consistente nas bordas: puxa pixels fracos para o tom do foil
out = np.dstack([rgb, al])
img = Image.fromarray((out * 255).astype(np.uint8), 'RGBA')
bb = img.getchannel('A').point(lambda v: 255 if v > 18 else 0).getbbox()
img = img.crop((bb[0] - 8, bb[1] - 8, bb[2] + 8, bb[3] + 8))
print(img.size)
img.save(S / 'assets/img/logo.webp', quality=92, method=6, exact=True)
w = 420; img.resize((w, round(img.height * w / img.width)), Image.LANCZOS).save(S / 'assets/img/logo-p.webp', quality=92, method=6, exact=True)
# marca isolada (borboleta-escaravelho) para favicon e detalhes
W, H = img.size
b = img.crop((int(W * .60), 0, W, int(H * .62))); bb = b.getchannel('A').point(lambda v: 255 if v > 18 else 0).getbbox()
b = b.crop(bb); print(b.size); b.save(S / 'assets/img/borb.webp', quality=92, method=6, exact=True)
p = Image.new('RGB', (W * 2 + 40, H + b.height + 40), (11, 15, 14)); p.paste(img, (10, 10), img); p.paste(b, (W + 30, 10), b)
p.paste((239, 231, 214), (W + 30, b.height + 30, W * 2 + 30, H + b.height + 30)); p.paste(img, (W + 30, b.height + 30), img)
p.save(R / 'retrato/_logo_teste.jpg', quality=90)
