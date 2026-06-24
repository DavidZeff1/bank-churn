/* Bank Churn showcase — tabs + slide gallery */
(function () {
  const TABS = ["overview", "dashboard", "presentation", "report", "data"];

  function showTab(id) {
    if (!TABS.includes(id)) id = "overview";
    document.querySelectorAll(".tab").forEach(s =>
      s.classList.toggle("active", s.id === "tab-" + id));
    document.querySelectorAll(".tab-link").forEach(a =>
      a.classList.toggle("active", a.dataset.tab === id));
    // lazy-load the dashboard iframe only when its tab is first opened
    if (id === "dashboard") {
      const f = document.getElementById("dashFrame");
      if (f && !f.src) f.src = f.dataset.src;
    }
    window.scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  }

  function route() { showTab((location.hash || "#overview").slice(1)); }

  document.addEventListener("click", e => {
    if (e.target.closest(".menu-toggle")) {
      document.querySelector(".tabs").classList.toggle("open");
      return;
    }
    const link = e.target.closest("[data-tab]");
    if (!link) return;
    e.preventDefault();
    location.hash = link.dataset.tab;
    document.querySelector(".tabs").classList.remove("open");
  });
  window.addEventListener("hashchange", route);

  /* ---- slide gallery ---- */
  function initSlides() {
    const stage = document.getElementById("slideStage");
    if (!stage) return;
    const n = +stage.dataset.slides;
    const pad = i => String(i).padStart(2, "0");
    const src = i => `deliverables/slides/slide-${pad(i)}.png`;
    const big = document.getElementById("slideImg");
    const counter = document.getElementById("slideCount");
    const thumbs = document.getElementById("thumbs");
    let cur = 1;

    for (let i = 1; i <= n; i++) {
      const t = document.createElement("img");
      t.src = src(i); t.alt = "Slide " + i; t.loading = "lazy";
      t.addEventListener("click", () => go(i));
      thumbs.appendChild(t);
    }
    function go(i) {
      cur = (i < 1) ? n : (i > n ? 1 : i);
      big.src = src(cur);
      counter.textContent = `Slide ${cur} / ${n}`;
      [...thumbs.children].forEach((c, idx) =>
        c.classList.toggle("active", idx + 1 === cur));
      const act = thumbs.children[cur - 1];
      if (act) act.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
    }
    document.getElementById("prev").addEventListener("click", () => go(cur - 1));
    document.getElementById("next").addEventListener("click", () => go(cur + 1));
    document.addEventListener("keydown", e => {
      if (!document.getElementById("tab-presentation").classList.contains("active")) return;
      if (e.key === "ArrowLeft") go(cur - 1);
      if (e.key === "ArrowRight") go(cur + 1);
    });
    go(1);
  }

  document.addEventListener("DOMContentLoaded", () => { initSlides(); route(); });
})();
