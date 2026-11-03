/* Chemotech International — interactive product catalogue
   Data is embedded in the page (#catalogue-data) so it also works when
   the site is opened straight from disk. */
(function () {
  "use strict";

  var dataEl = document.getElementById("catalogue-data");
  if (!dataEl) return;
  var DATA = JSON.parse(dataEl.textContent);
  var PRODUCTS = DATA.products;
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
    return cards.filter(function (c) { return !c.hidden; }).map(function (c) { return +c.dataset.no; });
  }

  function apply() {
    var shown = 0;
    cards.forEach(function (card) {
      var p = BY_NO[card.dataset.no];
      var ok = matches(p);
      card.hidden = !ok;
      if (ok) shown++;
      $$(".mk li", card).forEach(function (li) { li.classList.toggle("is-hit", !!state.make && li.textContent === state.make); });
    });
    $$(".chips-row .chip").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.cat === state.cat)); });
    if (countEl) countEl.innerHTML = "Showing <b>" + shown + "</b> of " + PRODUCTS.length + " products";
    if (empty) empty.hidden = shown !== 0;
    if (title) {
      var c = CATS[state.cat];
      title.textContent = c ? c.name : "All products";
      var bits = [];
      if (state.make) bits.push("make: " + state.make);
      if (state.q) bits.push("search: “" + search.value.trim() + "”");
      titleNote.textContent = bits.length ? "Filtered by " + bits.join(" · ") : (c ? c.blurb : "Select a product to see every variant and the makes we supply.");
    }
  }

  $$(".chips-row .chip").forEach(function (b) {
    b.addEventListener("click", function () {
      state.cat = b.dataset.cat;
      setHash(state.cat === "all" ? "" : "cat-" + state.cat);
      apply();
    });
  });
  if (search) search.addEventListener("input", function () { state.q = norm(search.value.trim()); apply(); });
  if (makeSel) makeSel.addEventListener("change", function () { state.make = makeSel.value; apply(); });
  $$("[data-reset]").forEach(function (b) {
    b.addEventListener("click", function () {
      state = { cat: "all", make: "", q: "" };
      if (search) search.value = "";
      if (makeSel) makeSel.value = "";
      setHash("");
      apply();
    });
  });

  function setHash(h) {
    try {
      if (h) { if (location.hash !== "#" + h) history.replaceState(null, "", "#" + h); }
      else if (location.hash) history.replaceState(null, "", location.pathname + location.search);
    } catch (e) { /* sandboxed preview: ignore */ }
  }

  /* ---------------- Enquiry list ---------------- */
  var KEY = "chemotech-enquiry";
  function readList() {
    try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return memList; }
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
    if (i === -1) list.push({ no: no, name: BY_NO[no].name }); else list.splice(i, 1);
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
    $("#tray-list", tray).innerHTML = list.map(function (x) { return "<span>" + pad(x.no) + " · " + esc(x.name) + "</span>"; }).join("");
  }
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-add]");
    if (b) { e.preventDefault(); toggle(+b.dataset.add); }
  });
  var clearBtn = $("#tray-clear");
  if (clearBtn) clearBtn.addEventListener("click", function () { writeList([]); });

  /* ---------------- Product dialog ---------------- */
  var dlg = $("#pdialog");
  var current = null;
  var X_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>';

  function highlight(text) {
    var t = esc(text);
    if (!state.q) return t;
    state.q.split(/\s+/).filter(Boolean).forEach(function (w) {
      var re = new RegExp("(" + w.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + ")", "ig");
      t = t.replace(re, '<mark class="hl">$1</mark>');
    });
    return t;
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
      return '<div class="pd-main"><div class="ph-tile"><b>' + pad(p.no) + "</b>" + c.icon + "</div></div>" +
        '<p class="pd-caption"><span>Photos for this product are coming soon. Ask us for datasheets and references.</span></p>';
    }
    var im = imgs[i];
    var h = '<div class="pd-main"><img src="' + im.src + '" alt="' + esc(im.title) + '"></div>' +
      '<div class="pd-caption"><b>' + esc(im.title) + "</b>" + (im.sub ? "<span>" + esc(im.sub) + "</span>" : "") +
      (im.make ? "<em>Make: " + esc(im.make) + "</em>" : "") + "</div>";
    if (imgs.length > 1) {
      h += '<div class="thumbs" role="group" aria-label="More photos">' + imgs.map(function (x, k) {
        return '<button type="button" data-thumb="' + k + '" aria-current="' + (k === i) + '" aria-label="Photo ' + (k + 1) + ": " + esc(x.title) + '"><img src="' + x.src + '" alt=""></button>';
      }).join("") + "</div>";
    }
    return h;
  }

  function openProduct(no, imgIndex) {
    var p = BY_NO[no];
    if (!p || !dlg) return;
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
      '<header class="pd-head"><div><small>' + esc(c.name) + " · Product " + pad(p.no) + " of " + PRODUCTS.length + '</small><h2 id="pd-title">' + esc(p.name) + "</h2></div>" +
      '<button class="icon-btn" type="button" data-close aria-label="Close">' + X_ICON + "</button></header>" +
      '<div class="pd-body"><div class="pd-media" id="pd-media">' + mediaHtml(p, imgIndex || 0) + "</div>" +
      '<div class="pd-info"><p class="lead">' + highlight(p.desc) + "</p>" +
      (p.note ? '<p class="pd-note">' + esc(p.note) + "</p>" : "") +
      '<div class="pd-block"><h3>Main makes</h3><ul class="mk">' + p.main.map(function (m) { return '<li class="' + (m === state.make ? "is-hit" : "") + '">' + esc(m) + "</li>"; }).join("") + "</ul></div>" +
      '<div class="pd-block"><h3>' + p.variants.length + (p.variants.length === 1 ? " type" : " variants & types") + " · makes we supply</h3>" + vhtml + "</div></div></div>" +
      '<footer class="pd-foot"><div class="pd-nav"><button type="button" data-step="-1" aria-label="Previous product">&larr;<span class="lbl"> Previous</span></button><button type="button" data-step="1" aria-label="Next product"><span class="lbl">Next </span>&rarr;</button></div>' +
      '<div class="btn-row"><button class="add-btn" type="button" data-add="' + p.no + '" aria-pressed="' + inList(p.no) + '"><span class="ic-off">+ Add to enquiry</span><span class="ic-on">&check; In your enquiry</span></button>' +
      '<a class="btn" href="quote.html" data-quote-one="' + p.no + '">Request quote &rarr;</a></div></footer>';
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
      if (card) card.focus({ preventScroll: true });
    });
  }
  $$(".pcard__open, [data-open]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); openProduct(+(b.dataset.open || b.closest(".pcard").dataset.no)); });
  });

  /* ---------------- Solutions gallery + lightbox ---------------- */
  var sols = $$(".sol");
  var lb = $("#lightbox");
  var lbIndex = 0;
  $$(".sol-tabs .chip").forEach(function (b) {
    b.addEventListener("click", function () {
      $$(".sol-tabs .chip").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      sols.forEach(function (s) { s.hidden = b.dataset.group !== "all" && s.dataset.group !== b.dataset.group; });
    });
  });
  function visibleSols() { return sols.filter(function (s) { return !s.hidden; }); }
  function showLb(i) {
    var list = visibleSols();
    lbIndex = (i + list.length) % list.length;
    var s = list[lbIndex];
    var d = DATA.solutions[+s.dataset.i];
    var prod = d.products[0];
    lb.innerHTML =
      '<div class="lb-head"><span>' + esc(d.group) + " · " + (lbIndex + 1) + " / " + list.length + '</span><button class="icon-btn" type="button" data-close aria-label="Close">' + X_ICON + "</button></div>" +
      '<div class="lb-stage"><img src="' + d.img + '" alt="' + esc(d.title) + '">' +
      '<button class="icon-btn lb-arrow prev" type="button" data-lb="-1" aria-label="Previous photo">&larr;</button><button class="icon-btn lb-arrow next" type="button" data-lb="1" aria-label="Next photo">&rarr;</button></div>' +
      '<div class="lb-cap"><div><b>' + esc(d.title) + "</b><span>" + esc(d.sub) + " · Make: " + esc(d.make) + "</span></div>" +
      (prod ? '<button class="btn btn--green" type="button" data-lb-product="' + prod + '">View ' + esc(BY_NO[prod].name) + " &rarr;</button>" : "") + "</div>";
    if (!lb.open) { lb.showModal(); document.body.classList.add("has-dialog"); }
  }
  sols.forEach(function (s) {
    s.addEventListener("click", function () { showLb(visibleSols().indexOf(s)); });
  });
  if (lb) {
    lb.addEventListener("click", function (e) {
      if (e.target === lb || e.target.closest("[data-close]")) { lb.close(); return; }
      var a = e.target.closest("[data-lb]");
      if (a) { showLb(lbIndex + (+a.dataset.lb)); return; }
      var p = e.target.closest("[data-lb-product]");
      if (p) { lb.close(); openProduct(+p.dataset.lbProduct); }
    });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") showLb(lbIndex + 1);
      if (e.key === "ArrowLeft") showLb(lbIndex - 1);
    });
    lb.addEventListener("close", function () { if (!dlg || !dlg.open) document.body.classList.remove("has-dialog"); });
  }

  /* ---------------- Start ---------------- */
  function fromHash() {
    var h = location.hash.slice(1);
    var m;
    if ((m = h.match(/^cat-([a-z]{2})$/)) && CATS[m[1]]) { state.cat = m[1]; apply(); var t = $("#catalogue"); if (t) t.scrollIntoView(); }
    else if ((m = h.match(/^p-(\d+)$/)) && BY_NO[m[1]]) { apply(); openProduct(+m[1]); }
  }
  window.addEventListener("hashchange", fromHash);
  apply();
  renderTray();
  fromHash();
})();
