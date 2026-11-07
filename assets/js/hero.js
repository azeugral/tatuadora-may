/* Hero da May: uma palavra escrita em particulas de ouro escorre e vira o traco de uma tatuagem real.
   As mascaras em assets/img/hero saem das fotos dela (tools/tinta.py + tools/cortar.py). */
(function () {
  'use strict';
  var CENAS = [
    { p: 'saudade', a: 'asas' },
    { p: 'amizade', a: 'buque' },
    { p: 'amorproprio', a: 'bemmequero' },
    { p: 'mae', a: 'mae' },
    { p: 'recomeco', a: 'borboleta' }
  ];
  var D = { pal: 1.5, ida: 2.7, arte: 3.5, volta: 2.1 };
  var PAR = D.pal + D.ida + D.arte + D.volta;

  var VS_P = `#version 300 es
  precision highp float;
  layout(location=0) in vec4 aA;
  layout(location=1) in vec4 aB;
  uniform float uM, uT, uTam, uPx;
  uniform vec2 uEsc, uCentro;
  out vec2 vE;
  float h(float n){ return fract(sin(n*12.9898)*43758.5453); }
  vec2 fluxo(vec2 p, float t){
    return vec2(
      sin(p.y*3.1+t*.7)+.55*sin(p.y*7.3-t*.9+p.x*2.1)+.28*sin(p.y*15.-t*1.3+p.x*5.),
      cos(p.x*2.7-t*.6)+.55*cos(p.x*6.1+t*.8-p.y*3.)+.28*cos(p.x*13.+t*1.1-p.y*6.));
  }
  void main(){
    float id=float(gl_VertexID), r=h(id+1.), r2=h(id*1.7+3.), r3=h(id*.37+9.);
    float atraso=(aA.x*.5+.5)*.5+r*.18;
    float m=clamp((uM*1.68-atraso)/1.0,0.,1.);
    float e=m*m*m*(m*(6.*m-15.)+10.);
    vec2 p=mix(aA.xy,aB.xy,e);
    float voo=sin(3.14159*e);
    p+=fluxo(p*1.25+vec2(r2*.3),uT*.5+id*1e-6)*voo*(.11+.13*r3);
    p.y+=voo*voo*(.05+.09*r2);
    float nivel=mix(aA.z,aB.z,e);
    p+=(vec2(r,r2)-.5)*.0016;
    float pisca=.78+.22*sin(uT*(1.+r3*2.5)+r*6.283);
    if(nivel<.5){ p+=.018*vec2(sin(uT*.21+r*40.),cos(uT*.17+r2*40.)); pisca*=.5+.5*sin(uT*.6+r3*30.); }
    gl_Position=vec4(uCentro+p*uEsc,0.,1.);
    gl_PointSize=uTam*(.82+.5*r3)*(1.+voo*.25);
    float brilho=mix(.09,1.,smoothstep(.2,.8,nivel));
    float esm=step(.962,r3);
    vE=vec2(1.-esm,esm*1.5)*brilho*pisca*(1.-voo*.35);
  }`;
  var FS_P = `#version 300 es
  precision highp float;
  in vec2 vE; uniform float uA; out vec4 c;
  void main(){ vec2 q=gl_PointCoord-.5; float d=smoothstep(.5,.18,length(q)); c=vec4(vE*uA*d,0.,1.); }`;
  var VS_Q = `#version 300 es
  out vec2 v; void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); v=p; gl_Position=vec4(p*2.-1.,0.,1.); }`;
  var FS_F = `#version 300 es
  precision highp float; in vec2 v; uniform sampler2D uT; uniform float uD; out vec4 c;
  void main(){ c=vec4(texture(uT,v).rgb*uD,1.); }`;
  var FS_C = `#version 300 es
  precision highp float; in vec2 v; uniform sampler2D uT; uniform float uG, uTp; uniform vec2 uR, uCentro; uniform vec3 uFundo; out vec4 c;
  float h(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
  float n(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f);
    return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
  void main(){
    vec3 t=texture(uT,v).rgb*uG;
    float ouro=1.-exp(-t.r*1.5), esm=1.-exp(-t.g*1.5);
    float folha=.55*n(gl_FragCoord.xy/2.6+uTp*.02)+.3*n(gl_FragCoord.xy/9.)+.15*n(gl_FragCoord.xy/34.-uTp*.05);
    vec3 g=mix(vec3(.42,.27,.10),vec3(.86,.66,.33),smoothstep(.02,.5,ouro));
    g=mix(g,vec3(1.,.90,.64),smoothstep(.5,1.,ouro*(.72+.56*folha)));
    vec2 q=(v-.5-(uCentro*.5))*uR/min(uR.x,uR.y);
    vec3 fundo=uFundo+vec3(.0,.028,.024)*exp(-dot(q,q)*3.2);
    vec3 col=fundo+g*ouro+vec3(.07,.62,.52)*esm;
    c=vec4(col,1.);
  }`;

  function prog(gl, vs, fs) {
    var p = gl.createProgram();
    [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]].forEach(function (a) {
      var s = gl.createShader(a[0]); gl.shaderSource(s, a[1]); gl.compileShader(s);
      if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(s));
      gl.attachShader(p, s);
    });
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    var u = {}, n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (var i = 0; i < n; i++) { var nm = gl.getActiveUniform(p, i).name; u[nm] = gl.getUniformLocation(p, nm); }
    return { p: p, u: u };
  }

  /* amostra a mascara: quanto mais tinta no pixel, mais particulas. Ordena por colunas para o caminho ser coerente. */
  function amostra(im, N, sem) {
    var S = 1024, cv = amostra.c || (amostra.c = document.createElement('canvas'));
    cv.width = cv.height = S;
    var x = cv.getContext('2d', { willReadFrequently: true });
    x.clearRect(0, 0, S, S); x.drawImage(im, 0, 0, S, S);
    var d = x.getImageData(0, 0, S, S).data, tot = 0, i, a, px = new Float32Array(S * S);
    for (i = 0; i < S * S; i++) { a = d[i * 4] / 255; a = a < .1 ? 0 : a * a; px[i] = a; tot += a; }
    var at = Math.min(.92, Math.max(.6, tot * 9 / N)), Na = Math.floor(N * at);
    var pos = new Float32Array(Na * 2), passo = tot / Na, acu = 0, lim = passo * .5, c = 0, sx = sem, rnd = function () { sx = (sx * 16807) % 2147483647; return sx / 2147483647; };
    for (i = 0; i < S * S && c < Na; i++) {
      var w = px[i]; if (!w) continue; acu += w;
      while (acu >= lim && c < Na) { pos[c * 2] = (i % S) + rnd(); pos[c * 2 + 1] = Math.floor(i / S) + rnd(); c++; lim += passo; }
    }
    Na = c;
    var ch = new Float64Array(Na);
    for (i = 0; i < Na; i++) ch[i] = Math.floor(pos[i * 2] / 12) * 4096 * 4096 + Math.floor(pos[i * 2 + 1] * 8) * 4096 + 0 + (i % 4096) / 8192;
    var id = new Uint32Array(Na); for (i = 0; i < Na; i++) id[i] = i;
    id.sort(function (p, q) { return ch[p] - ch[q]; });
    var o = new Int16Array(N * 4), K = 32767 / 512;
    for (i = 0; i < Na; i++) {
      var j = id[i];
      o[i * 4] = (pos[j * 2] - 512) * K; o[i * 4 + 1] = (512 - pos[j * 2 + 1]) * K; o[i * 4 + 2] = 32767;
    }
    for (i = Na; i < N; i++) {  // o resto vira poeira ao redor
      var t = rnd() * 6.2832, r = .35 + 1.25 * Math.sqrt(rnd());
      o[i * 4] = Math.max(-1, Math.min(1, Math.cos(t) * r * .78)) * 32767; o[i * 4 + 1] = Math.max(-1, Math.min(1, Math.sin(t) * r * .78)) * 32767; o[i * 4 + 2] = 0;
    }
    return o;
  }

  window.heroMay = function (canvas, op) {
    op = op || {};
    var gl = canvas.getContext('webgl2', { antialias: false, alpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'high-performance' });
    if (!gl) return null;
    var flut = !!gl.getExtension('EXT_color_buffer_float') ;
    var N = op.n || 260000, cenas = op.cenas || CENAS, ordem = [];
    cenas.forEach(function (c) { ordem.push('p-' + c.p, c.a); });
    var P = prog(gl, VS_P, FS_P), F = prog(gl, VS_Q, FS_F), C = prog(gl, VS_Q, FS_C);
    var vaoP = gl.createVertexArray(), vaoQ = gl.createVertexArray();
    var alvos = ordem.map(function () { return null; }), W = 0, H = 0, fb = [], u0 = op.fundo || [11 / 255, 15 / 255, 14 / 255];
    gl.bindVertexArray(vaoP); gl.enableVertexAttribArray(0); gl.enableVertexAttribArray(1);
    gl.disable(gl.DEPTH_TEST);

    function alvo() {
      var t = gl.createTexture(); gl.bindTexture(gl.TEXTURE_2D, t);
      if (flut) gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA16F, W, H, 0, gl.RGBA, gl.HALF_FLOAT, null);
      else gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, W, H, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      var f = gl.createFramebuffer(); gl.bindFramebuffer(gl.FRAMEBUFFER, f);
      gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, t, 0);
      gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT);
      return { t: t, f: f };
    }
    function tamanho(w, h) {
      if (w === W && h === H) return;
      fb.forEach(function (b) { gl.deleteTexture(b.t); gl.deleteFramebuffer(b.f); });
      W = canvas.width = w; H = canvas.height = h; fb = [alvo(), alvo()];
    }
    function carrega(k, im) {
      var o = amostra(im, N, 1234 + k * 77), b = gl.createBuffer();
      gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, o, gl.STATIC_DRAW);
      alvos[k] = b;
    }
    function estado(t) {
      var n = cenas.length, tt = ((t % (PAR * n)) + PAR * n) % (PAR * n), c = Math.floor(tt / PAR), s = tt - c * PAR, k = c * 2, m = 0, a, b;
      if (s < D.pal) { a = k; b = k + 1; m = 0; }
      else if (s < D.pal + D.ida) { a = k; b = k + 1; m = (s - D.pal) / D.ida; }
      else if (s < D.pal + D.ida + D.arte) { a = k; b = k + 1; m = 1; }
      else { a = k + 1; b = (k + 2) % (n * 2); m = (s - D.pal - D.ida - D.arte) / D.volta; }
      return { a: a, b: b, m: m, cena: c, fase: s };
    }
    function liga(loc, b) { gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.vertexAttribPointer(loc, 4, gl.SHORT, true, 8, 0); }
    var ult = -1;
    function desenha(t, o) {
      var e = estado(t), ba = alvos[e.a], bb = alvos[e.b];
      if (!ba || !bb) { ba = alvos[e.a] || alvos[0]; bb = ba; e.m = 0; }
      if (!ba) return e;
      var dt = ult < 0 ? 1 / 60 : Math.min(.05, Math.max(.001, t - ult)); ult = t;
      var dec = flut ? Math.pow(.84, dt * 60) : 0;
      var cor = fb[0], ant = fb[1]; fb = [ant, cor];
      gl.bindFramebuffer(gl.FRAMEBUFFER, cor.f); gl.viewport(0, 0, W, H);
      gl.disable(gl.BLEND);
      gl.useProgram(F.p); gl.bindVertexArray(vaoQ); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, ant.t);
      gl.uniform1i(F.u.uT, 0); gl.uniform1f(F.u.uD, dec); gl.drawArrays(gl.TRIANGLES, 0, 3);
      gl.useProgram(P.p); gl.bindVertexArray(vaoP); liga(0, ba); liga(1, bb);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);
      var lado = o.lado, ex = lado / W, ey = lado / H;
      gl.uniform1f(P.u.uM, e.m); gl.uniform1f(P.u.uT, t); gl.uniform2f(P.u.uEsc, ex, ey); gl.uniform2f(P.u.uCentro, o.cx || 0, o.cy || 0);
      gl.uniform1f(P.u.uTam, o.pt || 1.9); gl.uniform1f(P.u.uA, (o.a || .3)); gl.uniform1f(P.u.uPx, 1);
      gl.drawArrays(gl.POINTS, 0, N);
      gl.disable(gl.BLEND);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null); gl.viewport(0, 0, W, H);
      gl.useProgram(C.p); gl.bindVertexArray(vaoQ); gl.bindTexture(gl.TEXTURE_2D, cor.t);
      gl.uniform1i(C.u.uT, 0); gl.uniform1f(C.u.uG, 1 - dec); gl.uniform1f(C.u.uTp, t); gl.uniform2f(C.u.uR, W, H);
      gl.uniform2f(C.u.uCentro, o.cx || 0, o.cy || 0); gl.uniform3fv(C.u.uFundo, u0);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      return e;
    }
    return { ordem: ordem, cenas: cenas, carrega: carrega, tamanho: tamanho, desenha: desenha, estado: estado, pronto: function (k) { return !!alvos[k]; }, total: PAR * cenas.length, D: D, flut: flut };
  };
  window.heroMay.CENAS = CENAS;
  window.heroMay.PAR = PAR;
})();
