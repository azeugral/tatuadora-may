# -*- coding: utf-8 -*-
"""Isola cada arte real (mascara manual sobre a tinta extraida), nivela e centraliza em 1024; grava tambem as palavras."""
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref'; T = R / 'tinta'
ARTES = {  # poligono em fracoes do arquivo; rotacao em graus
 'asas': dict(pol=[(.05, .08), (.80, .08), (.80, .40), (.72, .62), (.62, .80), (.05, .80)], rot=17, apaga=[(0,0,222,455),(0,0,125,530),(840,660,1024,1024)]),
 'buque': dict(pol=None, rot=0, apaga=[(0,0,226,1024),(802,0,1024,1024)]),
 'bemmequero': dict(pol=[(.0, .0), (1, 0), (1, .62), (.96, 1), (0, 1)], rot=0, mini=60, apaga=[(825,250,1024,360),(700,530,790,600),(815,780,900,860)]),
 'borboleta': dict(pol=[(.28, .22), (.78, .22), (.78, .72), (.28, .72)], rot=0, t=.45, apaga=[(740,660,1024,1024)]),
 'mae': dict(elipse=(.515, .465, .245, .315, 18), rot=0, apaga=[(850,540,920,600),(735,760,812,900)]),
}
def le(n): return cv2.imdecode(np.fromfile(str(T / f'{n}.png'), np.uint8), 0).astype(np.float32) / 255
def isola(n, o):
    a = le(n); h, w = a.shape; m = np.zeros((h, w), np.uint8)
    if o.get('elipse'):
        cx, cy, rx, ry, ang = o['elipse']; cv2.ellipse(m, (int(cx * w), int(cy * h)), (int(rx * w), int(ry * h)), ang, 0, 360, 255, -1)
    elif o.get('pol'):
        cv2.fillPoly(m, [np.array([(x * w, y * h) for x, y in o['pol']], np.int32)], 255)
    else: m[:] = 255
    a = a * (m > 0)
    if o.get('t'): a = np.clip((a - o['t']) / (1 - o['t']), 0, 1)
    b = (a > .3).astype(np.uint8); n_, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    k = np.zeros(n_, bool); k[1:] = st[1:, cv2.CC_STAT_AREA] >= o.get('mini', 40)
    a = a * cv2.dilate(k[lab].astype(np.uint8), np.ones((5, 5), np.uint8))
    if o['rot']:
        M = cv2.getRotationMatrix2D((w / 2, h / 2), o['rot'], 1); a = cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_CUBIC)
    ys, xs = np.where(a > .25); a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    e = 960 / max(a.shape); a = cv2.resize(a, None, fx=e, fy=e, interpolation=cv2.INTER_AREA if e < 1 else cv2.INTER_CUBIC)
    a = np.clip(a, 0, 1); c = np.zeros((1024, 1024), np.float32); y = (1024 - a.shape[0]) // 2; x = (1024 - a.shape[1]) // 2
    c[y:y + a.shape[0], x:x + a.shape[1]] = a
    for x0, y0, x1, y1 in o.get('apaga', []): c[y0:y1, x0:x1] = 0
    ys, xs = np.where(c > .25); a = c[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    e = 960 / max(a.shape); a = np.clip(cv2.resize(a, None, fx=e, fy=e, interpolation=cv2.INTER_CUBIC), 0, 1)
    c = np.zeros((1024, 1024), np.float32); y = (1024 - a.shape[0]) // 2; x = (1024 - a.shape[1]) // 2
    c[y:y + a.shape[0], x:x + a.shape[1]] = a
    return c
PAL = {'saudade': 'saudade', 'amizade': 'amizade', 'amorproprio': 'amor próprio', 'mae': 'amor de mãe', 'recomeco': 'recomeço'}
def palavra(t):
    F = ImageFont.truetype(str(R / 'fontes/AlexBrush-Regular.ttf'), 400); im = Image.new('L', (2600, 1000)); d = ImageDraw.Draw(im); d.text((300, 200), t, font=F, fill=255)
    bb = im.getbbox(); im = im.crop(bb); e = min(960 / im.width, 330 / im.height); im = im.resize((round(im.width * e), round(im.height * e)), Image.LANCZOS)
    c = Image.new('L', (1024, 1024)); c.paste(im, ((1024 - im.width) // 2, (1024 - im.height) // 2)); return np.asarray(c).astype(np.float32) / 255
def grava(n, c): cv2.imencode('.webp', (c * 255).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 90])[1].tofile(str(S / f'assets/img/hero/{n}.webp'))
if __name__ == '__main__':
    f = []
    for n, o in ARTES.items():
        c = isola(n, o); grava(n, c); f.append(cv2.resize(c, (400, 400), interpolation=cv2.INTER_AREA)); print(n, round(float(c.mean()), 4))
    g = []
    for n, t in PAL.items():
        c = palavra(t); grava('p-' + n, c); g.append(cv2.resize(c, (400, 400), interpolation=cv2.INTER_AREA))
    cv2.imwrite(str(T / '_iso.jpg'), (np.vstack([np.hstack(f), np.hstack(g)]) * 255).astype(np.uint8))
