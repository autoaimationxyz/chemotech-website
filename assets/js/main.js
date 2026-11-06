/* Chemotech International — site behaviour (no dependencies) */
(function () {
  "use strict";

  var INBOX = "info.chemotechinternational@gmail.com";

  /* ---- Mobile navigation ---- */
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open menu");
        toggle.focus();
      }
    });
  }

  /* Reveal only when animation and intersection observation are supported.
     Content remains visible when JavaScript is unavailable. */
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var reveal = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); reveal.unobserve(entry.target); }
      });
    }, { threshold: 0.08 });
    document.querySelectorAll(".section-head, .feature-card, .vpanel, .partner, .steps").forEach(function (el) {
      el.classList.add("reveal-ready"); reveal.observe(el);
    });
  }

  /* ---- Footer year ---- */
  var y = document.querySelector("[data-year]");
  if (y) y.textContent = new Date().getFullYear();

  /* ---- Products: search filter ---- */
  var search = document.getElementById("product-search");
  if (search) {
    var out = document.getElementById("search-count");
    var empty = document.getElementById("no-results");
    var subcats = Array.prototype.slice.call(document.querySelectorAll(".subcat"));
    var sections = Array.prototype.slice.call(document.querySelectorAll(".vsection"));
    var total = document.querySelectorAll(".items li").length;

    var run = function () {
      var q = search.value.trim().toLowerCase();
      var hits = 0;
      subcats.forEach(function (sc) {
        var items = sc.querySelectorAll(".items li");
        var title = sc.querySelector("h3").textContent.toLowerCase();
        var titleHit = q && title.indexOf(q) !== -1;
        var any = false;
        items.forEach(function (li) {
          var m = !q || titleHit || li.textContent.toLowerCase().indexOf(q) !== -1;
          li.hidden = !m;
          li.classList.toggle("is-hit", !!q && m && !titleHit);
          if (m) { any = true; hits++; }
        });
        sc.hidden = !any;
      });
      sections.forEach(function (s) {
        s.hidden = !s.querySelector(".subcat:not([hidden])");
      });
      if (empty) empty.hidden = hits !== 0;
      if (out) out.textContent = q ? hits + " of " + total + " products match" : total + " products listed";
    };
    search.addEventListener("input", run);
    run();
  }

  /* ---- Products: highlight current vertical in the index ---- */
  var indexLinks = document.querySelectorAll(".cat-index nav a");
  if (indexLinks.length && "IntersectionObserver" in window) {
    var map = {};
    indexLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          indexLinks.forEach(function (a) { a.classList.remove("is-active"); });
          map[en.target.id].classList.add("is-active");
        }
      });
    }, { rootMargin: "-30% 0px -60% 0px" });
    document.querySelectorAll(".vsection").forEach(function (s) { io.observe(s); });
  }

  /* ---- Quote form: products picked in the catalogue ---- */
  var picked = document.getElementById("picked");
  if (picked) {
    var KEY = "chemotech-enquiry";
    var indexElement = document.getElementById("product-index");
    var productIndex = indexElement ? JSON.parse(indexElement.textContent) : {};
    var read = function () {
      try {
        var list = JSON.parse(localStorage.getItem(KEY) || "[]");
        if (!Array.isArray(list)) return [];
        var seen = {};
        return list.reduce(function (result, item) {
          if (!item) return result;
          var no = +item.no === 10 ? 9 : +item.no;
          var product = productIndex[no] || (!indexElement && typeof item.name === "string" ? {name: item.name, catalogue_no: item.catalogue_no || no} : null);
          if (product && !seen[no]) {
            seen[no] = true;
            result.push({no: no, catalogue_no: product.catalogue_no, name: product.name});
          }
          return result;
        }, []);
      } catch (e) { return []; }
    };
    var write = function (l) { try { localStorage.setItem(KEY, JSON.stringify(l)); } catch (e) { /* ignore */ } };
    var input = document.getElementById("picked-input");
    var list = picked.querySelector("ul");
    var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
    var pad = function (n) { return (n < 10 ? "0" : "") + n; };
    var render = function () {
      var items = read();
      picked.hidden = items.length === 0;
      list.innerHTML = items.map(function (x) {
        return '<li><code>' + pad(x.catalogue_no || x.no) + '</code>' + esc(x.name) + '<button type="button" data-remove="' + x.no + '" aria-label="Remove ' + esc(x.name) + '">&times;</button></li>';
      }).join("");
      input.value = items.map(function (x) { return pad(x.catalogue_no || x.no) + " " + x.name; }).join("; ");
    };
    picked.addEventListener("click", function (e) {
      var b = e.target.closest("[data-remove]");
      if (!b) return;
      write(read().filter(function (x) { return x.no !== +b.dataset.remove; }));
      render();
    });
    render();
  }

  /* ---- Forms: validate, then open the visitor's email app ---- */
  document.querySelectorAll("form[data-mailto]").forEach(function (form) {
    var status = form.querySelector(".form-status");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      form.querySelectorAll("[required]").forEach(function (el) {
        var err = form.querySelector('[data-err-for="' + el.id + '"]');
        var bad = !el.value.trim() || (el.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim()));
        el.setAttribute("aria-invalid", bad ? "true" : "false");
        if (err) err.textContent = bad ? (el.dataset.msg || "Please fill in this field.") : "";
        if (bad && ok) { el.focus(); ok = false; }
      });
      if (!ok) return;

      var lines = [];
      form.querySelectorAll("[data-label]").forEach(function (el) {
        var val;
        if (el.matches("fieldset, [role=group]")) {
          val = Array.prototype.map.call(el.querySelectorAll("input:checked"), function (c) { return c.value; }).join(", ");
        } else {
          val = el.value.trim();
        }
        if (val) lines.push(el.dataset.label + ": " + val);
      });

      var who = (form.querySelector("#name") || {}).value || "";
      var org = (form.querySelector("#company") || {}).value || "";
      var subject = form.dataset.mailto + (org ? " — " + org : who ? " — " + who : "");
      var body = lines.join("\n") + "\n\nSent from chemotech-international website";
      var href = "mailto:" + INBOX + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);

      if (status) status.hidden = false;
      window.location.href = href;
    });
  });
})();

/* Illustrative engineering ecosystem: focus a discipline, or pause its motion. */
(function () {
  "use strict";
  var root = document.querySelector('.system-experience');
  if (!root) return;
  var descriptions = {
    all: 'Power, control and process utilities. Engineered to work together.',
    power: 'Electrical distribution, backup generation and renewable energy connect the site.',
    automation: 'PLC, HMI and SCADA connect equipment, monitoring and process control.',
    water: 'Treatment, filtration and process utilities connect resources to operations.'
  };
  root.querySelectorAll('[data-system-mode]').forEach(function (button) {
    button.addEventListener('click', function () {
      root.dataset.system = button.dataset.systemMode;
      root.querySelectorAll('[data-system-mode]').forEach(function (other) {
        other.setAttribute('aria-pressed', String(other === button));
      });
      root.querySelector('#system-copy').textContent = descriptions[button.dataset.systemMode];
    });
  });
  var pause = root.querySelector('.motion-toggle');
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  function syncMotion() {
    if (reduced.matches) {
      document.body.classList.add('motion-paused');
      pause.disabled = true;
      pause.textContent = 'Reduced motion enabled';
      pause.setAttribute('aria-pressed', 'true');
    } else {
      pause.disabled = false;
      document.body.classList.remove('motion-paused');
      pause.setAttribute('aria-pressed', 'false');
      pause.textContent = 'Pause animation Ⅱ';
    }
  }
  pause.addEventListener('click', function () {
    var paused = document.body.classList.toggle('motion-paused');
    pause.setAttribute('aria-pressed', String(paused));
    pause.textContent = paused ? 'Play animation ▷' : 'Pause animation Ⅱ';
  });
  if (reduced.addEventListener) reduced.addEventListener('change', syncMotion);
  syncMotion();
})();
