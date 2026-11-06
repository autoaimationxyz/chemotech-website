/* Chemotech International — interactive product catalogue
   Data is embedded in the page (#catalogue-data) so it also works when
   the site is opened straight from disk. */
(function () {
  "use strict";

  var dataEl = document.getElementById("catalogue-data");
  if (!dataEl) return;
  var DATA = JSON.parse(dataEl.textContent);
  var PRODUCTS = DATA.products;
  var REDIRECTS = DATA.redirects || {};
  var CATS = {};
  DATA.categories.forEach(function (c) { CATS[c.id] = c; });
  var BY_NO = {};
  PRODUCTS.forEach(function (p) { BY_NO[p.no] = p; });

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var norm = function (s) { return String(s).toLowerCase(); };

  /* Search text per product: name, description, variants and makes */
  PRODUCTS.forEach(function (p) {
    var parts = [p.name, p.desc, p.note, CATS[p.cat].name].concat(p.main);
    p.variants.forEach(function (v) { parts.push(v.name); parts = parts.concat(v.makes); });
    p._text = norm(parts.join(" | "));
    var set = {};
    p.main.forEach(function (m) { set[m] = 1; });
    p.variants.forEach(function (v) { v.makes.forEach(function (m) { set[m] = 1; }); });
    p._makes = set;
  });

  var pageSize = 12, limit = pageSize;
  var more = document.getElementById("show-more");
  var progress = document.getElementById("catalogue-progress");
  var state = { cat: "all", make: "", q: "" };
  var cards = $$(".pcard");
  var search = $("#cat-search");
  var makeSel = $("#cat-make");
  var countEl = $("#cat-count");
  var empty = $("#cat-empty");
  var title = $("#cat-title");
  var titleNote = $("#cat-title-note");

  function matches(p) {
    if (state.cat !== "all" && p.cat !== state.cat) return false;
    if (state.make && !p._makes[state.make]) return false;
    if (state.q) {
      var words = state.q.split(/\s+/).filter(Boolean);
      for (var i = 0; i < words.length; i++) if (p._text.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function visibleNos() {
    return PRODUCTS.filter(matches).map(function (p) { return p.no; });
  }

  function apply(keepLimit) {
    if (!keepLimit) limit = pageSize;
    var shown = 0;
    cards.forEach(function (card) {
      var p = BY_NO[card.dataset.no];
      var ok = matches(p);
      if (ok) shown++;
      card.hidden = !ok || shown > limit;
      $$(".mk li", card).forEach(function (li) { li.classList.toggle("is-hit", !!state.make && li.textContent === state.make); });
    });
    $$(".chips-row .chip").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.cat === state.cat)); });
    if (countEl) countEl.innerHTML = "<b>" + shown + "</b> matching " + (shown === 1 ? "product" : "products");
    if (empty) empty.hidden = shown !== 0;
    if (more) { more.hidden = shown <= limit; more.textContent = 'Show ' + Math.min(pageSize, Math.max(0, shown-limit)) + ' more products'; }
    if (progress) progress.textContent = shown ? Math.min(shown,limit) + ' of ' + shown + ' matching products displayed' : '';
    if (title) {
      var c = CATS[state.cat];
      title.textContent = c ? c.name : "All products";
      var bits = [];
      if (state.make) bits.push("make: " + state.make);
      if (state.q) bits.push("search: “" + search.value.trim() + "”");
      titleNote.textContent = bits.length ? "Filtered by " + bits.join(" · ") : (c ? c.blurb : "Select a product to see every variant and the makes we supply.");
    }
  }

  if (more) more.addEventListener('click', function () {
    var firstNew = PRODUCTS.filter(matches)[limit];
    limit += pageSize;
    apply(true);
    var next = firstNew && $('.pcard[data-no="' + firstNew.no + '"] .pcard__open');
    if (next) next.focus();
  });

  $$(".chips-row .chip").forEach(function (b) {
    b.addEventListener("click", function () {
      state.cat = b.dataset.cat;
      setHash(state.cat === "all" ? "" : "cat-" + state.cat);
      apply();
    });
  });
  $$("[data-gateway]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      event.preventDefault();
      state = { cat: link.dataset.gateway, make: "", q: "" };
      if (search) search.value = "";
      if (makeSel) makeSel.value = "";
      setHash("cat-" + state.cat);
      apply();
      var catalogue = $("#catalogue");
      if (catalogue) catalogue.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
    });
  });
  if (search) search.addEventListener("input", function () { state.q = norm(search.value.trim()); syncFilters(); apply(); });
  if (makeSel) makeSel.addEventListener("change", function () { state.make = makeSel.value; syncFilters(); apply(); });
  $$("[data-reset]").forEach(function (b) {
    b.addEventListener("click", function () {
      state = { cat: "all", make: "", q: "" };
      if (search) search.value = "";
      if (makeSel) makeSel.value = "";
      setHash("");
      apply();
    });
  });

  function syncFilters() {
    try {
      var url = new URL(location.href);
      if (state.q) url.searchParams.set('q', search.value.trim());
      else url.searchParams.delete('q');
      if (state.make) url.searchParams.set('make', state.make);
      else url.searchParams.delete('make');
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    } catch (e) { /* File previews and restricted histories keep filters usable. */ }
  }
  function setHash(h) {
    try {
      var url = new URL(location.href);
      url.hash = h;
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    } catch (e) { /* sandboxed preview: ignore */ }
    syncFilters();
  }
  function restoreFilters() {
    var params = new URLSearchParams(location.search);
    if (search) search.value = params.get('q') || '';
    if (makeSel) makeSel.value = params.get('make') || '';
    state.q = norm(search ? search.value.trim() : '');
    state.make = makeSel ? makeSel.value : '';
    if (makeSel && !state.make) makeSel.value = '';
  }

  /* ---------------- Enquiry list ---------------- */
  var KEY = "chemotech-enquiry";
  function readList() {
    var list;
    try { list = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { list = memList; }
    if (!Array.isArray(list)) return [];
    var seen = {};
    return list.reduce(function (result, item) {
      if (!item) return result;
      var no = +(REDIRECTS[item.no] || item.no);
      var product = BY_NO[no];
      if (product && !seen[no]) {
        seen[no] = true;
        result.push({ no: no, catalogue_no: product.catalogue_no, name: product.name });
      }
      return result;
    }, []);
  }
  var memList = [];
  function writeList(list) {
    memList = list;
    try { localStorage.setItem(KEY, JSON.stringify(list)); } catch (e) { /* storage blocked */ }
    renderTray();
  }
  function inList(no) { return readList().some(function (x) { return x.no === no; }); }
  function toggle(no) {
    var list = readList();
    var i = list.map(function (x) { return x.no; }).indexOf(no);
    if (i === -1) list.push({ no: no, catalogue_no: BY_NO[no].catalogue_no, name: BY_NO[no].name }); else list.splice(i, 1);
    writeList(list);
  }
  function syncButtons() {
    $$("[data-add]").forEach(function (b) { b.setAttribute("aria-pressed", String(inList(+b.dataset.add))); });
  }
  var tray = $("#tray");
  function renderTray() {
    var list = readList();
    syncButtons();
    if (!tray) return;
    tray.hidden = list.length === 0;
    document.body.classList.toggle("has-tray", list.length > 0);
    $("#tray-count", tray).textContent = list.length;
    $("#tray-label", tray).textContent = list.length === 1 ? "product in your enquiry" : "products in your enquiry";
    $("#tray-list", tray).innerHTML = list.map(function (x) { return "<span>" + pad(x.catalogue_no || x.no) + " · " + esc(x.name) + "</span>"; }).join("");
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-add]");
    if (b) { e.preventDefault(); toggle(+b.dataset.add); }
  });
  window.addEventListener('storage', function (event) {
    if (event.key === KEY || event.key === null) renderTray();
  });
  window.addEventListener('pageshow', function () { renderTray(); });
  var clearBtn = $("#tray-clear");
  if (clearBtn) clearBtn.addEventListener("click", function () { writeList([]); });

  /* ---------------- Product dialog ---------------- */
  var dlg = $("#pdialog");
  var current = null;
  function arrowSvg(direction) {
    var paths = { right: "M4 12h16m-6-6 6 6-6 6", left: "M20 12H4m6-6-6 6 6 6", "up-right": "M6 18 18 6M6 6h12v12" };
    return '<svg class="arrow arrow--' + direction + '" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="' + paths[direction] + '"/></svg>';
  }
  var RIGHT_ARROW = arrowSvg("right");
  var LEFT_ARROW = arrowSvg("left");
  var UP_RIGHT_ARROW = arrowSvg("up-right");
  var X_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

  function highlight(text) {
    if (!state.q) return esc(text);
    var words = state.q.split(/\s+/).filter(Boolean).map(function (w) { return w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); });
    var re = new RegExp("(" + words.join("|") + ")", "ig");
    return String(text).split(re).map(function (part, i) { return i % 2 ? '<mark class="hl">' + esc(part) + '</mark>' : esc(part); }).join('');
  }

  function groupVariants(p) {
    // Split "Group – Type" on en dashes (keeping numeric ranges like "30 – 200 mm" intact).
    // A group with a single item is shown as one full name instead.
    var rows = p.variants.map(function (v) {
      var safe = (v.name || "").replace(/(\d) – (\d)/g, "$1\u0000$2");
      var parts = safe ? safe.split(" – ").map(function (x) { return x.replace(/\u0000/g, " – "); }) : [""];
      return {
        g: parts.length > 1 ? parts.slice(0, -1).join(" – ") : "",
        n: parts.length > 1 ? parts[parts.length - 1] : (v.name || p.name),
        full: v.name || p.name, makes: v.makes
      };
    });
    var size = {};
    rows.forEach(function (r) { size[r.g] = (size[r.g] || 0) + 1; });
    var groups = [], idx = {};
    rows.forEach(function (r) {
      if (r.g && size[r.g] === 1) { r.n = r.full; r.g = ""; }
      var key = r.g || "\u0001" + groups.length; // keep ungrouped rows in order
      if (!r.g && groups.length && !groups[groups.length - 1].g) key = groups[groups.length - 1].key;
      if (!(key in idx)) { idx[key] = groups.length; groups.push({ key: key, g: r.g, items: [] }); }
      groups[idx[key]].items.push(r);
    });
    return groups;
  }

  function mediaHtml(p, i) {
    var imgs = p.images;
    var c = CATS[p.cat];
    if (!imgs.length) {
      return '<div class="pd-main"><div class="equipment-tile">' + (p.illustration || c.icon) + '<span class="illustration-caption">Configuration illustration</span></div></div>' +
        '<p class="pd-caption"><span>Conceptual illustration. Ask our team for model-specific photographs and datasheets.</span></p>';
    }
    var im = imgs[i];
    var h = '<div class="pd-main"><img src="' + im.src + '" alt="' + esc(im.title) + '"></div>' +
      '<div class="pd-caption"><b>' + esc(im.title) + "</b>" + (im.sub ? "<span>" + esc(im.sub) + "</span>" : "") +
      (im.make ? "<em>Make: " + esc(im.make) + "</em>" : "") +
      (im.source ? '<span class="photo-credit-links"><a href="' + esc(im.source) + '" target="_blank" rel="noopener noreferrer">Photo source ' + UP_RIGHT_ARROW + '</a>' + (im.license_url ? '<a href="' + esc(im.license_url) + '" target="_blank" rel="noopener noreferrer">Licence ' + UP_RIGHT_ARROW + '</a>' : '') + '</span>' : '') + "</div>";
    if (imgs.length > 1) {
      h += '<div class="thumbs" role="group" aria-label="More photos">' + imgs.map(function (x, k) {
        return '<button type="button" data-thumb="' + k + '" aria-current="' + (k === i) + '" aria-label="Photo ' + (k + 1) + ": " + esc(x.title) + '"><img src="' + x.src + '" alt=""></button>';
      }).join("") + "</div>";
    }
    return h;
  }

  function openProduct(no, imgIndex) {
    no = +(REDIRECTS[no] || no);
    var p = BY_NO[no];
    if (!p || !dlg) return;
    var position = PRODUCTS.filter(matches).findIndex(function (item) { return item.no === no; });
    if (position >= limit) { limit = Math.ceil((position + 1) / pageSize) * pageSize; apply(true); }
    current = no;
    var c = CATS[p.cat];
    dlg.className = "pdialog c-" + p.cat;
    var groups = groupVariants(p);
    var vhtml = groups.map(function (g) {
      return '<div class="vgroup">' + (g.g ? "<h4>" + highlight(g.g) + "</h4>" : "") + '<ul class="vlist">' + g.items.map(function (it) {
        var dim = state.make && it.makes.indexOf(state.make) === -1;
        return '<li class="' + (dim ? "is-dim" : "") + '"><b>' + highlight(it.n) + '</b><ul class="mk">' + it.makes.map(function (m) {
          return '<li class="' + (m === state.make ? "is-hit" : "") + '">' + highlight(m) + "</li>";
        }).join("") + "</ul></li>";
      }).join("") + "</ul></div>";
    }).join("");

    dlg.innerHTML =
      '<header class="pd-head"><div><small>' + esc(c.name) + " · Product " + pad(p.catalogue_no || p.no) + " of " + PRODUCTS.length + '</small><h2 id="pd-title">' + esc(p.name) + "</h2></div>" +
      '<button class="icon-btn" type="button" data-close aria-label="Close">' + X_ICON + "</button></header>" +
      '<div class="pd-body" tabindex="0" role="region" aria-label="Product specifications and variants"><div class="pd-media" id="pd-media">' + mediaHtml(p, imgIndex || 0) + "</div>" +
      '<div class="pd-info"><p class="lead">' + highlight(p.desc) + "</p>" +
      (p.note ? '<p class="pd-note">' + esc(p.note) + "</p>" : "") +
      '<div class="pd-block"><h3>Specifications at a glance</h3><dl class="spec-grid">' + (p.specs || []).map(function (s) { return '<div><dt>' + esc(s[0]) + '</dt><dd>' + esc(s[1]) + '</dd></div>'; }).join('') + '</dl><p class="spec-note">Ratings and options vary by model. Ask our team for the datasheet and selection for your site.</p></div>' +
      '<div class="application-note"><b>Where it fits</b>' + esc(p.application || '') + '</div>' +
      '<div class="pd-block"><h3>Main makes</h3><ul class="mk">' + p.main.map(function (m) { return '<li class="' + (m === state.make ? "is-hit" : "") + '">' + esc(m) + "</li>"; }).join("") + "</ul></div>" +
      '<div class="pd-block"><h3>' + p.variants.length + (p.variants.length === 1 ? " type" : " variants & types") + " · makes we supply</h3>" + vhtml + "</div></div></div>" +
      '<footer class="pd-foot"><div class="pd-nav"><button type="button" data-step="-1" aria-label="Previous product">' + LEFT_ARROW + '<span class="lbl"> Previous</span></button><button type="button" data-step="1" aria-label="Next product"><span class="lbl">Next </span>' + RIGHT_ARROW + '</button></div>' +
      '<div class="btn-row"><button class="add-btn" type="button" data-add="' + p.no + '" aria-pressed="' + inList(p.no) + '"><span class="ic-off">+ Add to enquiry</span><span class="ic-on">&check; In your enquiry</span></button>' +
      '<a class="btn" href="quote.html" data-quote-one="' + p.no + '">Request quote ' + RIGHT_ARROW + '</a></div></footer>';
    dlg.setAttribute("aria-labelledby", "pd-title");
    if (!dlg.open) {
      if (dlg.showModal) dlg.showModal(); else dlg.setAttribute("open", "");
      document.body.classList.add("has-dialog");
    }
    $(".pd-body", dlg).scrollTop = 0;
    setHash("p-" + p.no);
  }

  if (dlg) {
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg || e.target.closest("[data-close]")) { dlg.close(); return; }
      var t = e.target.closest("[data-thumb]");
      if (t) { $("#pd-media", dlg).innerHTML = mediaHtml(BY_NO[current], +t.dataset.thumb); return; }
      var s = e.target.closest("[data-step]");
      if (s) {
        var list = visibleNos();
        if (list.indexOf(current) === -1) list = PRODUCTS.map(function (p) { return p.no; });
        var i = list.indexOf(current) + (+s.dataset.step);
        openProduct(list[(i + list.length) % list.length]);
        return;
      }
      var q = e.target.closest("[data-quote-one]");
      if (q && !inList(+q.dataset.quoteOne)) toggle(+q.dataset.quoteOne);
    });
    dlg.addEventListener("close", function () {
      document.body.classList.remove("has-dialog");
      setHash(state.cat === "all" ? "" : "cat-" + state.cat);
      var card = $('.pcard[data-no="' + current + '"] .pcard__open');
      if (card && !card.closest(".pcard").hidden) card.focus({ preventScroll: true });
      else if (search) search.focus({ preventScroll: true });
    });
  }
  $$(".pcard__open, [data-open]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); openProduct(+(b.dataset.open || b.closest(".pcard").dataset.no)); });
  });

  /* ---------------- Start ---------------- */
  function fromHash() {
    restoreFilters();
    var h = location.hash.slice(1);
    var m;
    state.cat = "all";
    if (h === "solutions") { location.replace("solutions.html"); return; }
    if ((m = h.match(/^cat-([a-z]{2})$/)) && CATS[m[1]]) { state.cat = m[1]; apply(); var t = $("#catalogue"); if (t) t.scrollIntoView(); }
    else if ((m = h.match(/^p-(\d+)$/)) && (BY_NO[m[1]] || REDIRECTS[m[1]])) { apply(); openProduct(+m[1]); }
    else apply();
  }
  window.addEventListener("hashchange", fromHash);
  window.addEventListener("popstate", fromHash);
  renderTray();
  fromHash();
})();
