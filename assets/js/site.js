(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); }, $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var celular = matchMedia('(max-width:1023px)').matches || matchMedia('(pointer:coarse)').matches;
  var calmo = matchMedia('(prefers-reduced-motion:reduce)').matches;
  var LEG = window.CENAS_LEG;

  /* topo e menu */
  var topo = $('#topo'), sobe = function () { topo.classList.toggle('cheio', scrollY > 40); };
  addEventListener('scroll', sobe, { passive: true }); sobe();
  var bm = $('#btMenu'), menu = $('#menu');
  function fechaMenu() { menu.hidden = true; bm.setAttribute('aria-expanded', 'false'); bm.setAttribute('aria-label', 'Abrir menu'); document.body.style.overflow = ''; }
  bm.addEventListener('click', function () {
    var ab = menu.hidden; menu.hidden = !ab; bm.setAttribute('aria-expanded', ab); bm.setAttribute('aria-label', ab ? 'Fechar menu' : 'Abrir menu'); document.body.style.overflow = ab ? 'hidden' : '';
  });
  $$('a', menu).forEach(function (a) { a.addEventListener('click', fechaMenu); });
  $$('[data-m]').forEach(function (e) { e.hidden = !celular; });
  if (innerWidth < 1024) $$('[data-d]').forEach(function (e) { e.hidden = true; });

  /* entrada */
  var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('ve'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
  $$('.sobe').forEach(function (e) { io.observe(e); });
  if (calmo) $$('.sobe').forEach(function (e) { e.classList.add('ve'); });

  /* videos so tocam visiveis */
  var iv = new IntersectionObserver(function (es) {
    es.forEach(function (e) { var v = e.target; if (e.isIntersecting) { if (!calmo) { var p = v.play(); if (p) p.catch(function () {}); } } else v.pause(); });
  }, { threshold: .35 });
  $$('video.auto').forEach(function (v) { iv.observe(v); });

  /* hero */
  var fundo = $('#heroFundo'), pos = $('#heroPos'), hero = $('.hero'), pal = $('#heroPal'), leg = $('#heroLeg'), rod = $('#heroRod');
  var mesa = 0, vis = true;
  new IntersectionObserver(function (e) { vis = e[0].isIntersecting; }, { threshold: .02 }).observe(hero);
  document.addEventListener('visibilitychange', function () { vis = !document.hidden; });
  function legenda(c) { if (c === mesa) return; mesa = c; rod.style.opacity = 0; setTimeout(function () { pal.textContent = LEG[c].p; leg.textContent = LEG[c].t; rod.style.opacity = 1; }, 450); }
  function estatico() { pos.hidden = false; rod.hidden = true; }
  function webgl(n) {
    var cv = document.createElement('canvas'); fundo.appendChild(cv);
    var T;
    try { T = heroMay(cv, { n: n }); } catch (e) { T = null; }
    if (!T) { cv.remove(); estatico(); return; }
    var dpr = Math.min(devicePixelRatio || 1, 2), W, H, op = {};
    function mede() {
      var r = hero.getBoundingClientRect(), w = Math.min(innerWidth, 2560), h = r.height;
      var esc = Math.min(dpr, 2400 / w); W = Math.round(w * esc); H = Math.round(h * esc); T.tamanho(W, H);
      var art = Math.min(h * .84, w * .46); hero.style.setProperty('--art', art + 'px');
      op = { lado: art * esc * .96, pt: 1.55 * esc, a: .3 / Math.max(1, esc * .75), cx: 0, cy: -.015 };
    }
    mede(); addEventListener('resize', mede);
    var carregando = 0, t0 = null, tRel = 0, prev = 0;
    function proximo() {
      var k = carregando; if (k >= T.ordem.length) return;
      var im = new Image(); im.onload = function () { T.carrega(k, im); carregando++; if (carregando === 2 && !t0) { t0 = 1; cv.style.opacity = 1; requestAnimationFrame(voa); } setTimeout(proximo, 60); };
      im.src = 'assets/img/hero/' + T.ordem[k] + '.webp';
    }
    cv.style.opacity = 0; cv.style.transition = 'opacity 1.2s';
    proximo();
    function voa(ag) {
      requestAnimationFrame(voa);
      var dt = Math.min(.05, (ag - prev) / 1000); prev = ag;
      if (!vis) return;
      var e = T.estado(tRel), b = e.b;
      if (!T.pronto(b) && e.m === 0 && e.fase > T.D.pal - .05) { /* espera a proxima arte */ } else tRel += dt;
      var r = T.desenha(tRel, op); legenda(r.cena);
    }
  }
  function video() {
    var v = document.createElement('video'); v.className = 'vd'; v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.setAttribute('aria-hidden', 'true');
    v.poster = 'assets/img/hero/poster.webp'; v.src = 'assets/video/hero.mp4'; v.preload = 'auto'; fundo.appendChild(v);
    var P = heroMay.PAR, n = 3, VID = [0, 3, 4];
    var p = v.play();
    if (p) p.catch(function () { v.remove(); webgl(70000); });
    var ultimo = -1;
    (function lg() { requestAnimationFrame(lg); if (!vis) return; var c = Math.floor((v.currentTime || 0) / P) % n; if (c !== ultimo) { ultimo = c; legenda(VID[c]); } })();
  }
  if (calmo) estatico(); else if (celular) video(); else webgl(window.__n || 260000);

  /* portfolio */
  var P = window.PECAS, grade = $('#grade'), filtro = 'tudo', aberto = false;
  var tiles = $$('.peca', grade);
  function limite() { return innerWidth < 761 ? 8 : innerWidth < 1181 ? 9 : 12; }
  function aplica() {
    var n = 0, tot = 0, lim = limite();
    tiles.forEach(function (t) {
      var ok = filtro === 'tudo' || t.dataset.s === filtro; if (ok) tot++;
      t.hidden = !ok || (filtro === 'tudo' && !aberto && n >= lim);
      if (!t.hidden) n++;
    });
    $('#verMais').parentNode.hidden = filtro !== 'tudo' || aberto;
  }
  $$('#filtros button').forEach(function (b) {
    b.addEventListener('click', function () {
      filtro = b.dataset.f; $$('#filtros button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); aplica();
    });
  });
  $('#verMais').addEventListener('click', function () { aberto = true; aplica(); });
  aplica();

  /* lightbox */
  var lb = $('#lb'), li = $('#lbI'), ato = 0, vista = 0, foco = null, lista = [];
  function visiveis() { lista = tiles.filter(function (t) { return !t.hidden; }).map(function (t) { return P[+t.dataset.i]; }); }
  function mostra() {
    var p = lista[ato]; li.src = 'assets/img/o/' + p.fotos[vista] + '.webp'; li.alt = p.leg;
    $('#lbS').textContent = window.SENT[p.s]; $('#lbL').textContent = p.leg; $('#lbT').textContent = p.t;
    var bx = $('#lbV'); bx.innerHTML = '';
    if (p.fotos.length > 1) p.fotos.forEach(function (f, i) {
      var b = document.createElement('button'); b.type = 'button'; b.setAttribute('aria-label', 'Vista ' + (i + 1)); b.setAttribute('aria-pressed', i === vista);
      b.innerHTML = '<img src="assets/img/o/' + f + '.webp" alt="" loading="lazy">'; b.addEventListener('click', function () { vista = i; mostra(); }); bx.appendChild(b);
    });
  }
  function abre(id, el) { visiveis(); ato = lista.findIndex(function (p) { return p.id === id; }); vista = 0; foco = el; mostra(); lb.hidden = false; document.body.style.overflow = 'hidden'; $('#lbF').focus(); }
  function fecha() { lb.hidden = true; document.body.style.overflow = ''; li.removeAttribute('src'); if (foco) foco.focus({ preventScroll: true }); }
  function anda(d) { ato = (ato + d + lista.length) % lista.length; vista = 0; mostra(); }
  tiles.forEach(function (t) { t.addEventListener('click', function () { abre(P[+t.dataset.i].id, t); }); });
  $('#lbF').addEventListener('click', fecha); $('#lbA').addEventListener('click', function () { anda(-1); }); $('#lbP').addEventListener('click', function () { anda(1); });
  lb.addEventListener('click', function (e) { if (e.target === lb || e.target.className === 'lb-palco') fecha(); });
  addEventListener('keydown', function (e) { if (lb.hidden) { if (e.key === 'Escape' && !menu.hidden) fechaMenu(); return; } if (e.key === 'Escape') fecha(); if (e.key === 'ArrowRight') anda(1); if (e.key === 'ArrowLeft') anda(-1); });
  var xi = 0; li.addEventListener('touchstart', function (e) { xi = e.touches[0].clientX; }, { passive: true });
  li.addEventListener('touchend', function (e) { var d = e.changedTouches[0].clientX - xi; if (Math.abs(d) > 50) anda(d < 0 ? 1 : -1); }, { passive: true });
  $('#lbQ').addEventListener('click', function () {
    var p = lista[ato]; fecha(); $('#fIdeia').value = 'Vi a tatuagem "' + p.leg + '" no site e quero algo nesse caminho. '; $('#fSent').value = p.s;
    $('#orcamento').scrollIntoView(); setTimeout(function () { $('#fNome').focus({ preventScroll: true }); }, 600);
  });

  /* coberturas */
  $$('#cobTabs button').forEach(function (b, i) {
    b.addEventListener('click', function () {
      var c = window.COBS[i]; $$('#cobTabs button').forEach(function (x) { x.setAttribute('aria-pressed', x === b); });
      $('#cobA').src = 'assets/img/c/' + c.id + '-a.webp'; $('#cobD').src = 'assets/img/c/' + c.id + '-d.webp'; $('#cobT').textContent = c.t;
    });
  });

  /* acao de natal: some sozinha depois de 20/12/2026 */
  var acao = $('#acao'); if (new Date() > new Date('2026-12-20T23:59:59-03:00')) acao.hidden = true;
  $$('[data-acao]').forEach(function (a) { a.addEventListener('click', function () { var f = $('#fIdeia'); if (!f.value) f.value = 'Quero participar da Ação Solidária de Natal. '; }); });

  /* orcamento vira mensagem pronta no WhatsApp */
  $('#form').addEventListener('submit', function (e) {
    e.preventDefault();
    var n = $('#fNome').value.trim(), l = $('#fLugar').value.trim(), er = $('#fErro');
    if (!n || !l) { er.textContent = !n ? 'Escreva o seu nome.' : 'Diga em qual lugar do corpo será a tatuagem.'; er.hidden = false; (n ? $('#fLugar') : $('#fNome')).focus(); return; }
    er.hidden = true;
    var sel = $('#fSent'), s = sel.value ? sel.options[sel.selectedIndex].text : '', t = $('#fTam').value.trim(), i = $('#fIdeia').value.trim();
    var m = ['Oi, May! Vim pelo site e queria um orçamento.', '', 'Nome: ' + n, 'Lugar do corpo: ' + l];
    if (t) m.push('Tamanho: ' + t); if (s) m.push('Sentimento: ' + s); if (i) m.push('Ideia: ' + i);
    window.open('https://wa.me/5575982071367?text=' + encodeURIComponent(m.join('\n')), '_blank', 'noopener');
  });
})();
