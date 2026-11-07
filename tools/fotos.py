# -*- coding: utf-8 -*-
"""Fotos do portfolio (sem recortar corpo: formato 4:5 original), coberturas, retratos e videos."""
import subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
S = Path(__file__).resolve().parent.parent; R = S.parent / '_ref'
sys.path.insert(0, str(S / 'tools')); import dados
def tom(im):
    """Puxa de leve o alaranjado das fotos antigas para a pele ficar proxima entre si."""
    a = np.asarray(im).astype(np.float32); m = a.reshape(-1, 3).mean(0); alvo = m.mean()
    g = 1 + (alvo / m - 1) * .28
    return Image.fromarray(np.clip(a * g, 0, 255).astype(np.uint8))
def q45(im, cima=0):
    w, h = im.size
    if cima: im = im.crop((0, cima, w, h)); w, h = im.size
    if w / h > .8:
        n = int(h * .8); im = im.crop(((w - n) // 2, 0, (w - n) // 2 + n, h))
    else:
        n = int(w / .8); y = 0 if cima else (h - n) // 2; im = im.crop((0, y, w, y + n))
    return im
for p in dados.P:
    for j, f in enumerate(p['fotos']):
        im = q45(tom(Image.open(R / f'ig/fotos/{f}.jpg').convert('RGB')))
        im.resize((1080, 1350), Image.LANCZOS).save(S / f'assets/img/o/{f}.webp', quality=80, method=6)
        if j == 0: im.resize((640, 800), Image.LANCZOS).save(S / f"assets/img/p/{p['id']}.webp", quality=78, method=6)
for c in dados.C:
    a = q45(tom(Image.open(R / f"ig/fotos/{c['a']}.jpg").convert('RGB')), cima=250)
    d = q45(tom(Image.open(R / f"ig/fotos/{c['d']}.jpg").convert('RGB')))
    a.resize((800, 1000), Image.LANCZOS).save(S / f"assets/img/c/{c['id']}-a.webp", quality=80, method=6)
    d.resize((800, 1000), Image.LANCZOS).save(S / f"assets/img/c/{c['id']}-d.webp", quality=80, method=6)
# foto de perfil do Instagram dela (768 px): amplia com nitidez leve para a coluna da secao Sobre
Image.open(R / 'retrato/perfil.jpg').convert('RGB').resize((1152, 1152), Image.LANCZOS).filter(ImageFilter.UnsharpMask(1.6, 45, 2)).save(S / 'assets/img/may.webp', quality=88, method=6)
for n, f in (('cic-1ano', 'hl/cicatrizadas2/005.jpg'), ('cic-2anos', 'hl/cicatrizadas2/006.jpg')):
    i = Image.open(R / f).convert('RGB'); w = 540; print(i.size)
    i.resize((w, round(i.height * w / i.width)), Image.LANCZOS).save(S / f'assets/img/{n}.webp', quality=78, method=6)
def corta(ent, sai, ss, dur, vf, crf=26):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(ss), '-t', str(dur), '-i', str(ent), '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(S / f'assets/video/{sai}.mp4')], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.3', '-i', str(S / f'assets/video/{sai}.mp4'), '-frames:v', '1', '-q:v', '3', '-update', '1', str(S / f'assets/img/{sai}.jpg')], check=True)
b = R / 'ig/videos/110_0.mp4'; q = 'crop=720:900:0:300,scale=640:800:flags=lanczos'
corta(b, 'etapa-ideia', 1, 11, q); corta(b, 'etapa-criacao', 27, 12, q); corta(b, 'etapa-pele', 45, 11, q)
for n, f, ss, dd in (('cic-30', 'hl/cicatrizadas2/002.mp4', 1, 9), ('cic-leao', 'hl/cicatrizadas2/003.mp4', 1, 9), ('cic-det', 'hl/cicatrizadas2/004.mp4', 0, 8)):
    corta(R / f, n, ss, dd, 'scale=540:960:flags=lanczos', 27)
