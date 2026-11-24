// Tema "feixe" (prévia): o prisma do hero solta o feixe de quatro cores até a borda da tela e o título sobe.
// Um só momento, na abertura. Sem GSAP ou com movimento reduzido, a página aparece parada e completa.
(function () {
  var raiz = document.documentElement;
  var hero = document.querySelector(".hero"), mark = hero && hero.querySelector(".mark");
  var NS = "http://www.w3.org/2000/svg";
  var raios = null, ponto = null;

  // ponta do prisma no viewBox do símbolo do hero (-12 -12 122 124): o vértice (84, 35)
  var PX = (84 + 12) / 122, PY = (35 + 12) / 124, ALT = 260, MEIO = 130;
  var FINS = [[34, "#FF6B3D"], [100, "#FFC845"], [168, "#F8F6F2"], [230, "#C9A7FF"]];

  function monta() {
    if (!hero || !mark) return;
    raios = document.createElementNS(NS, "svg");
    raios.setAttribute("class", "feixe-raios"); raios.setAttribute("aria-hidden", "true");
    raios.setAttribute("viewBox", "0 0 1000 " + ALT); raios.setAttribute("preserveAspectRatio", "none");
    FINS.forEach(function (f) {
      var l = document.createElementNS(NS, "line");
      l.setAttribute("x1", 0); l.setAttribute("y1", MEIO); l.setAttribute("x2", 1000); l.setAttribute("y2", f[0]); l.setAttribute("stroke", f[1]);
      raios.appendChild(l);
    });
    ponto = document.createElement("span"); ponto.className = "feixe-ponto"; ponto.setAttribute("aria-hidden", "true");
    hero.appendChild(raios); hero.appendChild(ponto);
    posiciona();
    window.addEventListener("resize", posiciona);
  }
  function posiciona() {
    var h = hero.getBoundingClientRect(), m = mark.getBoundingClientRect();
    var x = m.left - h.left + PX * m.width, y = m.top - h.top + PY * m.height;
    raios.style.left = x + "px"; raios.style.top = (y - MEIO) + "px";
    raios.style.width = Math.max(0, h.width - x) + "px"; raios.style.height = ALT + "px";
    ponto.style.left = x + "px"; ponto.style.top = y + "px";
  }
  monta();

  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (window.gsap && !reduz && hero) {
    var mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", function () {
      var tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      tl.from(".hero .mark polygon:not(.echo)", { autoAlpha: 0, scale: 0.4, transformOrigin: "50% 50%", duration: 0.55, stagger: 0.07, ease: "back.out(1.7)", clearProps: "transform,opacity,visibility" })
        .from(".hero .mark .echo, .hero .mark .tick", { autoAlpha: 0, duration: 0.5 }, "<0.2")
        .from(".feixe-ponto", { autoAlpha: 0, scale: 0, duration: 0.3 }, "-=0.25")
        .from(".feixe-raios line", { scaleX: 0, svgOrigin: "0 " + MEIO, duration: 1.1, stagger: 0.08, ease: "power4.out" }, "<0.1")
        .fromTo(".feixe-ponto", { scale: 1 }, { scale: 1.7, duration: 0.22, repeat: 1, yoyo: true, ease: "power1.inOut", immediateRender: false }, ">-0.05")
        .from(".hero .eyebrow, .hero h1, .hero p.lead, .hero .cta", { autoAlpha: 0, y: 26, duration: 0.7, stagger: 0.09 }, "<0.1");
      raiz.classList.remove("feixe-espera");
    });
  } else {
    raiz.classList.remove("feixe-espera");
  }

  // hover: quando as facetas se abrem (CSS do site), a ponta laranja anda (9, -3) no viewBox do símbolo;
  // os raios e o ponto vão junto e o feixe se abre um pouco, com a mesma duração da transição das facetas
  if (window.gsap && !reduz && mark && raios) {
    var anda = function (on) {
      var k = mark.getBoundingClientRect().width / 122;   // px por unidade do viewBox
      var vars = { x: on ? 9 * k : 0, y: on ? -3 * k : 0, duration: 0.38, ease: "power3.out", overwrite: "auto" };
      gsap.to(raios, Object.assign({ scaleY: on ? 1.22 : 1, transformOrigin: "0% 50%" }, vars));
      gsap.to(ponto, Object.assign({ scale: on ? 1.5 : 1 }, vars));
    };
    mark.addEventListener("mouseenter", function () { anda(true); });
    mark.addEventListener("mouseleave", function () { anda(false); });
  }

  // aviso de prévia, com link para a estética atual (só nas páginas em /novo/)
  if (location.pathname.indexOf("/novo/") < 0) return;
  var aviso = document.createElement("div");
  aviso.className = "previa-aviso"; aviso.setAttribute("role", "note");
  aviso.innerHTML = '<span>Prévia da nova estética</span><a href="../' + location.hash + '">Ver a estética atual</a><button type="button" aria-label="Fechar aviso de prévia">×</button>';
  aviso.querySelector("button").addEventListener("click", function () { aviso.remove(); });
  document.body.appendChild(aviso);
})();
