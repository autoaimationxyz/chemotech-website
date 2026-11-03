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
        toggle.focus();
      }
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
        if (el.matches("fieldset")) {
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
