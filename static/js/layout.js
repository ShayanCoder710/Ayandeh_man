(function () {
  var toggle = document.getElementById("menu-toggle");
  var sheet = document.getElementById("nav-sheet");
  if (toggle && sheet) {
    function closeMenu() {
      document.body.classList.remove("menu-open");
      toggle.setAttribute("aria-expanded", "false");
    }
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    sheet.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
  }
  var yearEl = document.getElementById("footer-year");
  if (yearEl) {
    try {
      var year = new Intl.DateTimeFormat("fa-IR-u-ca-persian", { year: "numeric" }).format(new Date());
      yearEl.textContent = "© " + year + " آینده من";
    } catch (e) {}
  }
  var page = document.body.dataset.page;
  document.querySelectorAll("[data-key]").forEach(function (link) {
    if (link.dataset.key === page) link.classList.add("active");
  });
  var revealEls = Array.from(document.querySelectorAll(".reveal"));
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var observer = null;
  function markShown(el) {
    el.classList.add("in");
  }
  function revealAll() {
    Array.from(document.querySelectorAll(".reveal:not(.in)")).forEach(markShown);
  }
  if (reduced || !("IntersectionObserver" in window)) {
    revealAll();
  } else {
    observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var el = entry.target;
          if (el.classList.contains("in")) return;
          var parent = el.parentElement;
          var siblings = parent
            ? Array.from(parent.children).filter(function (c) {
                return c.classList.contains("reveal");
              })
            : [];
          var idx = siblings.indexOf(el);
          el.style.transitionDelay = Math.min(Math.max(idx, 0), 5) * 45 + "ms";
          el.classList.add("in");
          observer.unobserve(el);
        });
      },
      { threshold: 0.05, rootMargin: "0px 0px 160px 0px" },
    );
    revealEls.forEach(function (el) {
      observer.observe(el);
    });
    window.addEventListener("load", function () {
      window.setTimeout(revealAll, 2500);
    });
  }
  window.refreshReveal = function () {
    var newEls = Array.from(document.querySelectorAll(".reveal:not(.in)"));
    if (observer) newEls.forEach(function (el) {
      observer.observe(el);
    });
    else newEls.forEach(markShown);
    window.setTimeout(function () {
      newEls.forEach(markShown);
    }, 1800);
  };
})();
