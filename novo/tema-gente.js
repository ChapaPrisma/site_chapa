// Versão "menos IA" do tema feixe (prévia em /novo/).
// Um só movimento, ligado à marca: o prisma se monta e solta o feixe. O texto do topo já aparece parado
// (sai a subida em sequência), e sai o ponto branco com halo na ponta do prisma.
// Sem GSAP ou com movimento reduzido, a página aparece parada e completa.
(function () {
  var raiz = document.documentElement;
  var hero = document.querySelector(".hero"), mark = hero && hero.querySelector(".mark");
  var NS = "http://www.w3.org/2000/svg";
  var raios = null;

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
    hero.appendChild(raios);
    posiciona();
    window.addEventListener("resize", posiciona);
  }
  function posiciona() {
    var h = hero.getBoundingClientRect(), m = mark.getBoundingClientRect();
    var x = m.left - h.left + PX * m.width, y = m.top - h.top + PY * m.height;
    raios.style.left = x + "px"; raios.style.top = (y - MEIO) + "px";
    raios.style.width = Math.max(0, h.width - x) + "px"; raios.style.height = ALT + "px";
  }
  monta();

  var reduz = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (window.gsap && !reduz && hero) {
    var mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", function () {
      var tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      tl.from(".hero .mark polygon:not(.echo)", { autoAlpha: 0, scale: 0.4, transformOrigin: "50% 50%", duration: 0.55, stagger: 0.07, ease: "back.out(1.7)", clearProps: "transform,opacity,visibility" })
        .from(".hero .mark .echo, .hero .mark .tick", { autoAlpha: 0, duration: 0.5 }, "<0.2")
        .from(".feixe-raios line", { scaleX: 0, svgOrigin: "0 " + MEIO, duration: 1.1, stagger: 0.08, ease: "power4.out" }, "-=0.2");
      raiz.classList.remove("feixe-espera");
    });
  } else {
    raiz.classList.remove("feixe-espera");
  }

  // hover: quando as facetas se abrem (CSS do site), a ponta laranja anda (9, -3) no viewBox do símbolo e o feixe vai junto
  if (window.gsap && !reduz && mark && raios) {
    var anda = function (on) {
      var k = mark.getBoundingClientRect().width / 122;
      gsap.to(raios, { x: on ? 9 * k : 0, y: on ? -3 * k : 0, scaleY: on ? 1.22 : 1, transformOrigin: "0% 50%", duration: 0.38, ease: "power3.out", overwrite: "auto" });
    };
    mark.addEventListener("mouseenter", function () { anda(true); });
    mark.addEventListener("mouseleave", function () { anda(false); });
  }

  // o link "Onde e como votar" do topo abre o mesmo pop-up do botão do menu
  var votar = document.getElementById("voteHero"), btn = document.getElementById("voteBtn");
  if (votar && btn) votar.addEventListener("click", function () { btn.click(); });

  // aviso de prévia, com link para a versão atual (só nas páginas em /novo/)
  if (location.pathname.indexOf("/novo/") < 0) return;
  var aviso = document.createElement("div");
  aviso.className = "previa-aviso"; aviso.setAttribute("role", "note");
  aviso.innerHTML = '<span>Prévia da versão nova</span><a href="../' + location.hash + '">Ver a versão atual</a><button type="button" aria-label="Fechar aviso de prévia">×</button>';
  aviso.querySelector("button").addEventListener("click", function () { aviso.remove(); });
  document.body.appendChild(aviso);
})();
