# -*- coding: utf-8 -*-
"""Extrai o traco real das tatuagens das fotos (fundo de pele estimado localmente) e grava mascaras de tinta."""
import sys
from pathlib import Path
import numpy as np, cv2
R = Path(__file__).resolve().parent.parent.parent / '_ref'
OUT = R / 'tinta'; OUT.mkdir(exist_ok=True)

def le(f):
    return cv2.imdecode(np.fromfile(str(f), dtype=np.uint8), cv2.IMREAD_COLOR)

def tinta(img, caixa=None, t0=.06, t1=.30, esc=2, raio=41, minimo=14):
    if caixa:
        x0, y0, x1, y1 = caixa; img = img[y0:y1, x0:x1]
    img = cv2.resize(img, None, fx=esc, fy=esc, interpolation=cv2.INTER_LANCZOS4)
    L = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32) / 255
    L = cv2.bilateralFilter(L, 5, .06, 2)
    k = raio * esc | 1
    pq = cv2.resize(L, None, fx=.25, fy=.25, interpolation=cv2.INTER_AREA)
    # fundo = pele sem o traco: fechamento + blur
    kk = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k // 4 | 1, k // 4 | 1))
    bg = cv2.morphologyEx(pq, cv2.MORPH_CLOSE, kk)
    bg = cv2.GaussianBlur(bg, (0, 0), k / 12)
    bg = cv2.resize(bg, (L.shape[1], L.shape[0]), interpolation=cv2.INTER_CUBIC)
    d = np.clip((bg - L) / np.maximum(bg, .1), 0, 1)
    a = np.clip((d - t0) / (t1 - t0), 0, 1)
    a = a * a * (3 - 2 * a)
    # limpa poros: remove componentes pequenos
    bin_ = (a > .35).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(bin_, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= minimo * esc * esc
    dil = cv2.dilate(keep[lab].astype(np.uint8), np.ones((3, 3), np.uint8))
    return a * dil

CAND = {
 'bemmequero': (R/'hl/acao/009.jpg', (440, 800, 920, 1450)),
 'buque': (R/'ig/fotos/022_0.jpg', (440, 490, 880, 1180)),
 'borboleta': (R/'ig/fotos/081_0.jpg', None),
 'sollua': (R/'ig/fotos/065_0.jpg', None),
 'lirio': (R/'ig/fotos/028_0.jpg', None),
 'asas': (R/'ig/fotos/027_1.jpg', None),
 'fenix': (R/'ig/fotos/077_1.jpg', None),
 'hibisco': (R/'ig/fotos/059_0.jpg', None),
 'borb2': (R/'ig/fotos/041_0.jpg', None),
 'agua': (R/'ig/fotos/096_0.jpg', None),
 'sol': (R/'ig/fotos/020_1.jpg', None),
 'coracao': (R/'ig/fotos/083_0.jpg', None),
 'mae': (R/'ig/fotos/044_0.jpg', None),
 'borb3': (R/'ig/fotos/076_0.jpg', None),
 'ramo': (R/'ig/fotos/047_0.jpg', None),
 'pe': (R/'ig/fotos/042_0.jpg', None),
}
if __name__ == '__main__':
    ls = sys.argv[1:] or list(CAND)
    for n in ls:
        f, c = CAND[n]; a = tinta(le(f), c)
        cv2.imencode('.png', (a * 255).astype(np.uint8))[1].tofile(str(OUT / f'{n}.png'))
        print(n, a.shape, round(float(a.mean()), 4))
