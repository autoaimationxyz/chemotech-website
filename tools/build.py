#!/usr/bin/env python3
"""Generates the static Chemotech International site.

Usage:  python3 tools/build.py .

Content sources (edit these, then re-run):
  tools/products.json   56 products / 328 variants / makes (from the Product Master List,
                        regenerate with tools/parse_master_list.py)
  tools/solutions.json  solution photos, captions, makes and linked product numbers
  this file             page copy, clients, partners, registrations, contact details
"""
import hashlib, html, json, os, re, sys

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

# Set to False to hide per-variant makes on the public site (main makes still show).
SHOW_VARIANT_MAKES = True

INBOX = "info.chemotechinternational@gmail.com"
MAIL_MAIN = "chemotech.international@gmail.com"
MAIL_TAPAN = "tapan.chemotech@gmail.com"

NAV = [
    ("index.html", "Home"),
    ("about.html", "About Us"),
    ("products.html", "Our Products"),
    ("company-profile.html", "Company"),
    ("certifications.html", "Certifications"),
    ("contact.html", "Contact"),
]

ARROW = '<span class="arrow" aria-hidden="true">&rarr;</span>'

ICONS = {
    "electrical": '<rect x="4" y="3" width="16" height="18"/><path d="M13 6.5 9.5 12h4L11 17.5"/>',
    "switch": '<rect x="5" y="3" width="14" height="18"/><circle cx="12" cy="9" r="2.6"/><path d="M12 11.6V17M9 17h6"/>',
    "cable": '<path d="M3 6h7a3.5 3.5 0 0 1 0 7H7a3.5 3.5 0 0 0 0 7h14"/><circle cx="3" cy="6" r="1"/>',
    "power": '<rect x="3" y="7" width="15" height="10"/><path d="M18 10h2.5v4H18"/><path d="M11 8.8 8.6 12h3.6L10 15.2"/>',
    "automation": '<rect x="7" y="7" width="10" height="10"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>',
    "water": '<path d="M12 3c-4 5-6.2 8.2-6.2 11.2a6.2 6.2 0 0 0 12.4 0C18.2 11.2 16 8 12 3z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "chemicals": '<path d="M9 3h6M10 3v6.2l-5.3 8.9A2 2 0 0 0 6.4 21h11.2a2 2 0 0 0 1.7-2.9L14 9.2V3"/><path d="M7.4 15h9.2"/>',
    "building": '<path d="M4 21V8.5L12 3l8 5.5V21"/><path d="M2.5 21h19M9.5 21v-5.5h5V21M8 10.5h2M14 10.5h2"/>',
    "ict": '<rect x="3" y="4" width="18" height="12"/><path d="M8 20h8M12 16v4M7 8h4M7 11h7"/>',
    "service": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3.5 17.5l3 3 5.8-5.8a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.9-2.9z"/>',
}


def icon(key, cls="vicon"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.5" stroke-linecap="square" aria-hidden="true">{ICONS[key]}</svg>')


# --------------------------------------------------------------------------
# Data
# --------------------------------------------------------------------------
PRODUCTS = json.load(open(os.path.join(HERE, "products.json"), encoding="utf-8"))
SOLUTIONS = json.load(open(os.path.join(HERE, "solutions.json"), encoding="utf-8"))
COMPANY = json.load(open(os.path.join(HERE, "company.json"), encoding="utf-8"))

# 8 product categories, as colour-keyed in the 2026 company profile (product numbers in order)
CATEGORIES = [
    ("pd", "Power Distribution", range(1, 11), "electrical", "HT and LT panels, MCC, synchronising and APFC panels, transformers, substations and multi-brand DG sets."),
    ("sw", "Switchgear & Controls", range(11, 17), "switch", "Breakers, earth-leakage protection, DBs, changeovers, contactors, relays, indication and metering."),
    ("cl", "Cabling, Lighting & Safety", range(17, 27), "cable", "Power and control cables, wires, accessories, LED and street lighting, fans, earthing, fire alarm and PA."),
    ("pb", "Power Backup & Energy", range(27, 34), "power", "Online UPS and data-centre power, batteries, stabilisers, harmonic filters, EMS, solar and EV charging."),
    ("au", "Automation & Instrumentation", range(34, 39), "automation", "Motors, VFD and servo drives, PLC / HMI / SCADA, robotics, dam-gate control and field instruments."),
    ("wp", "Water & Process", range(39, 47), "water", "WTP, ETP, STP, RO / DM / UF plants, components and O&M, steam and piping, process chemicals and hygiene."),
    ("bi", "Building & ICT", range(47, 55), "building", "BMS, lifts, AC and ventilation, LED video walls, pre-fab structures, networking, CCTV and IT."),
    ("sv", "Services", range(55, 57), "service", "Licensed electrical installation, testing, commissioning, O&M and annual maintenance contracts."),
]
CAT_BY_NO = {}
for cid, _, rng, _, _ in CATEGORIES:
    for n in rng:
        CAT_BY_NO[n] = cid
CAT = {c[0]: c for c in CATEGORIES}

# Older photos (from the first profile) that add views not in the solutions set
EXTRA_IMAGES = {
    35: [("assets/img/delta-vfd.jpg", "Variable Frequency Drive", "Low-voltage AC drive", "Delta")],
    36: [("assets/img/delta-hmi.jpg", "HMI", "Touch-screen operator panel", "Delta")],
    33: [("assets/img/ev-charger-dc.jpg", "DC Fast Charger", "Dual-gun DC charging", "Delta"),
         ("assets/img/ev-charger-ac.jpg", "AC Wall-mount Charger", "For homes, offices & fleets", "Delta")],
    51: [("assets/img/fuf-panel.jpg", "FUF Panel Porta Cabin", "Building, clean room, godown, cold storage", "Dignus Infra")],
    29: [("assets/img/servo-stabilizer.jpg", "Servo Voltage Stabiliser", "Air-cooled, panel-mounted controls", "Krykard")],
    39: [("assets/img/wtp-softener.jpg", "Softener & Filter Vessels", "FRP vessels with multiport valves", "Micro Filteration Technologies")],
}

for p in PRODUCTS:
    p["cat"] = CAT_BY_NO[p["no"]]
    imgs = [dict(src=s["img"], title=s["title"], sub=s["sub"], make=s["make"]) for s in SOLUTIONS if p["no"] in s["products"]]
    imgs += [dict(src=a, title=b, sub=c, make=d) for a, b, c, d in EXTRA_IMAGES.get(p["no"], [])]
    p["images"] = imgs
    if not SHOW_VARIANT_MAKES:
        for v in p["variants"]:
            v["makes"] = []

N_PRODUCTS = len(PRODUCTS)
N_VARIANTS = sum(len(p["variants"]) for p in PRODUCTS)
N_MAKES = len({m for p in PRODUCTS for v in p["variants"] for m in v["makes"]} | {m for p in PRODUCTS for m in p["main_makes"]})
assert (N_PRODUCTS, N_VARIANTS) == (56, 328)
MAKES_LABEL = f"{(N_MAKES // 10) * 10}+"

# 7 business verticals (work profile) + services, each linking into the catalogue
VERTICALS = [
    ("v1", "electrical", "Electrical Works & Power Distribution", "pd", "HT / LT, MCC and synchronising panels, busbars, substations, transformers, switchgear, metering, cabling, lighting, earthing, surge protection and fire alarm systems."),
    ("v2", "power", "Power Backup, Quality & Energy", "pb", "Online UPS, data-centre infrastructure, batteries, multi-brand DG sets with service and spares, servo stabilisers, harmonic filters, APFC / VAR, solar, EV charging and EMS."),
    ("v3", "automation", "Automation & Instrumentation", "au", "VFDs, servo drives, PLC, HMI, SCADA, robotics, sensors, transmitters, flow meters, analysers and dam-gate automation."),
    ("v4", "water", "Water, Steam & Process Utilities", "wp", "WTP, ETP, STP, industrial RO, DM, softening, UF, packaged drinking water, membranes, pumps, steam distribution, PRV / PRS, valves, SS piping and tanks."),
    ("v5", "chemicals", "Process Chemicals & Hygiene Systems", "wp", "Cleaning, hygiene and CIP chemicals, water-treatment chemicals, conveyor lubrication, DE filter-aid powder, hygiene stations and cleanroom entry systems."),
    ("v6", "building", "Building & Infrastructure Solutions", "bi", "BMS, basement ventilation, LED screens and video walls, PUF / PIR pre-fab structures, clean rooms, cold rooms, plastic pallets and palletisers."),
    ("v7", "ict", "Low-Voltage, ICT & Security Systems", "bi", "Structured cabling and networking, CCTV and NVR systems, workstations, FHD LED displays, IP-PBX and telephone systems."),
    ("v8", "service", "Installation, Testing & AMC", "sv", "Licensed electrical contracting in Bihar and Delhi, plus testing, commissioning, troubleshooting, preventive maintenance and AMC for everything we supply."),
]

INDUSTRIES = COMPANY["industries"]

CLIENTS = ["OP Jindal Global University", "BML Munjal University", "Safdarjung Hospital, New Delhi",
           "JSW Hydro Energy Ltd (JSW Group)", "Triveni Sugar", "Indian Potash Limited",
           "Delhi Metro Rail Corporation", "Bisleri", "Catch", "Sagar Rice", "LG", "Pearl Global Industries Ltd",
           "Richa Global", "M.R. Proview Real Tech", "Pinax Paper Mills", "DPSG Faridabad",
           "Marriott Hotel, Ramnagar", "Lloyds Metals & Energy Ltd", "Aztek India Pvt Ltd",
           "Pradhan Mantri Awas Yojana Projects"]
SUGAR = [("Bazpur Sugar Mills", "Uttarakhand"), ("The Kisan Sugar Mills (Nadehi)", "Uttarakhand"),
         ("Triveni Sugar", "Khatauli"), ("White Gold", "Lanka, Assam"), ("Trivatinath Sugar", "Bareilly"),
         ("Baleni Sugar", "Meerut")]
DAIRY = [("Hira Lal Dairy", "ETP · Ghaziabad", "100 KLD"), ("Harbans Lal Dairy", "ETP · Meerut", "800 KLD"),
         ("Shri Gayatri Food", "ETP · Meerut", "1,200 KLD"), ("Kailash Dairy", "ETP · Meerut", "250 KLD")]
WATER = [("DPSG, Faridabad", "Water treatment", "150 KLD"),
         ("Bazpur Sugar Mills, Uttarakhand", "With mixed-bed plant", "2,500 KLD"),
         ("Nikita Greentech Recycling Ltd, Panipat", "Softening plant", "720 KLD"),
         ("Safdarjung Hospital, Delhi", "Softening plant", "500 KLD"),
         ("Lloyds Metals & Energy Ltd, Maharashtra", "Softening plant", "30 m³/hr")]
PARTNERS = COMPANY["partners"]

SERVICES = ["Engineering & technical solution design", "Equipment selection & supply", "System integration",
            "Installation", "Testing & commissioning", "Troubleshooting",
            "Preventive maintenance & O&M support", "After-sales service & plant improvement"]

PHONES_PATNA = [("+919899982418", "+91 98999 82418"), ("+919910680998", "+91 99106 80998"),
                ("+918757446605", "+91 87574 46605"), ("+919312282418", "+91 93122 82418")]
PHONES_DELHI = [("+919312282418", "+91 93122 82418"), ("+918757446605", "+91 87574 46605")]


def split_variant(name):
    """'Group – Type' split on en dashes, keeping numeric ranges like '30 – 200 mm' intact."""
    safe = re.sub(r"(\d) – (\d)", lambda m: m.group(1) + "\x00" + m.group(2), name)
    parts = [x.replace("\x00", " – ") for x in safe.split(" – ")]
    return (" – ".join(parts[:-1]), parts[-1]) if len(parts) > 1 else ("", name)


def tile_names(p):
    """Short variant labels for the spec-sheet tile (single-item groups keep their full name)."""
    rows = [split_variant(v["name"]) + (v["name"],) for v in p["variants"] if v["name"]]
    size = {}
    for g, _, _ in rows:
        size[g] = size.get(g, 0) + 1
    return [full if (not g or size[g] == 1) else n for g, n, full in rows] or [p["name"]]


def sol(slug):
    return next(s for s in SOLUTIONS if s["img"].endswith("/" + slug + ".jpg"))


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    qcur = ' aria-current="page"' if active == "quote.html" else ""
    links.append(f'<a class="btn" href="quote.html"{qcur}>Request Quote</a>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="wrap">
    <div class="topbar__group">
      <span class="topbar__countries">INDIA · NEPAL · BHUTAN</span>
      <span class="topbar__hide-sm">Patna · Delhi</span>
    </div>
    <div class="topbar__group">
      <a href="mailto:{INBOX}">{INBOX}</a>
    </div>
  </div>
</div>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html" aria-label="Chemotech International, home">
      <img src="assets/img/chemotech-logo.png" width="880" height="135" alt="Chemotech International – a Clean and Conditioning Company">
    </a>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-nav" aria-label="Open menu">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h12"/></svg>
    </button>
    <nav class="nav" id="site-nav" aria-label="Main">
      {"".join(links)}
    </nav>
  </div>
</header>"""


def footer():
    clinks = "".join(f'<li><a href="products.html#cat-{c[0]}">{E(c[1])}</a></li>' for c in CATEGORIES)
    phones = "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_PATNA)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="logo-tile"><img src="assets/img/chemotech-logo.png" width="880" height="135" alt="Chemotech International" loading="lazy"></div>
        <p class="tagline">…a Clean and Conditioning company</p>
        <p>Integrated electrical, power, automation, water, process, building and ICT solutions for industry and government projects since 2014–15.</p>
      </div>
      <div>
        <h4>Our products</h4>
        <ul>{clinks}</ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="company-profile.html">Company &amp; Credentials</a></li>
          <li><a href="company-profile.html#clients">Clients &amp; Projects</a></li>
          <li><a href="certifications.html">Certifications</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="quote.html">Request Quote</a></li>
        </ul>
      </div>
      <div>
        <h4>Reach us</h4>
        <ul>
          {phones}
          <li><a href="mailto:{INBOX}">{INBOX}</a></li>

        </ul>
      </div>
    </div>
    <div class="titleblock" aria-label="Registration details">
      <div><small>Head office</small><span>Patna, Bihar 800026</span></div>
      <div><small>Branch</small><span>Burari, Delhi 110084</span></div>
      <div><small>GSTIN Bihar</small><span>10AATFC8340G1ZJ</span></div>
      <div><small>GSTIN Delhi</small><span>07AATFC8340G1Z6</span></div>
      <div><small>PAN · Udyam</small><span>AATFC8340G · UDYAM-BR-26-0136033</span></div>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>© <span data-year>2026</span> Chemotech International. All rights reserved.</span>
    <span>Est. 2014–15 · Serving India, Nepal &amp; Bhutan</span>
  </div>
</footer>"""


def page(filename, title, description, body, extra_scripts=""):
    full_title = "Chemotech International" if filename == "index.html" else f"{title} · Chemotech International"
    with open(os.path.join(HERE, "../assets/css/immersive.css"), "rb") as theme:
        theme_version = hashlib.sha256(theme.read()).hexdigest()[:12]
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{E(description)}">
<meta name="theme-color" content="#080e17">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{E(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/img/chemotech-logo.png">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/modern.css">
<link rel="stylesheet" href="assets/css/immersive.css?v={theme_version}">
</head>
<body>
{header(filename)}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/js/main.js"></script>
{extra_scripts}
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w", encoding="utf-8") as f:
        f.write(doc)


def page_hero(crumb, title, text, tag=None):
    t = f'<span class="tag">{tag}</span>' if tag else ""
    return f"""<section class="page-hero on-navy">
  <div class="wrap">
    <div class="crumbs"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{crumb}</span></div>
    {t}
    <h1>{title}</h1>
    <p>{text}</p>
  </div>
  <div class="page-hero__rule"></div>
</section>"""


def cta():
    return f"""<section class="cta on-navy">
  <div class="wrap">
    <div>
      <h2>Tell us about your plant. We will propose the right system.</h2>
      <p>Call <a href="tel:+919899982418">+91 98999 82418</a> or write to <a href="mailto:{INBOX}">{INBOX}</a></p>
    </div>
    <div class="btn-row">
      <a class="btn btn--green" href="quote.html">Request a quote {ARROW}</a>
      <a class="btn btn--line-light" href="products.html">Browse products</a>
    </div>
  </div>
</section>"""


def industries_list():
    return "".join(f'<li{" class=\"is-key\"" if "Government" in n else ""}><span>{i:02d}</span>{E(n)}</li>' for i, n in enumerate(INDUSTRIES, 1))


def office_cards():
    pp = "<br>".join(f'<a href="tel:{a}">{b}</a>' for a, b in PHONES_PATNA)
    dp = "<br>".join(f'<a href="tel:{a}">{b}</a>' for a, b in PHONES_DELHI)
    return f"""<div class="offices">
      <article class="office" id="office-patna">
        <span class="tag">Head office · Bihar</span>
        <h3>Patna</h3>
        <address>Pratiksha Bhawan, Maurya Vihar Colony,<br>Near Bihar Urology Centre, Transport Nagar,<br>Patna, Bihar – 800026</address>
        <dl>
          <dt>Phone</dt><dd>{pp}</dd>
          <dt>Email</dt><dd><a href="mailto:{INBOX}">{INBOX}</a><br><a href="mailto:{MAIL_MAIN}">{MAIL_MAIN}</a><br><a href="mailto:{MAIL_TAPAN}">{MAIL_TAPAN}</a></dd>
        </dl>
        <div class="gstin"><span class="gstin__label">GSTIN · Bihar</span><span class="gstin__number">10AATFC8340G1ZJ</span></div>
      </article>
      <article class="office" id="office-delhi">
        <span class="tag">Branch office · Delhi</span>
        <h3>Delhi</h3>
        <address>Maya Garden, Ground Floor, Kh. No. 44/18 &amp; 44/19,<br>Gate No. 02, Inderprastha (IP) Colony, Block-C,<br>Village Burari, North Delhi – 110084</address>
        <dl>
          <dt>Phone</dt><dd>{dp}</dd>
          <dt>Email</dt><dd><a href="mailto:{INBOX}">{INBOX}</a><br><a href="mailto:{MAIL_MAIN}">{MAIL_MAIN}</a><br><a href="mailto:{MAIL_TAPAN}">{MAIL_TAPAN}</a></dd>
        </dl>
        <div class="gstin"><span class="gstin__label">GSTIN · Delhi</span><span class="gstin__number">07AATFC8340G1Z6</span></div>
      </article>
    </div>"""


# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------
HERO_SVG = """<svg viewBox="0 0 640 420" role="img" aria-labelledby="sch-t sch-d">
  <title id="sch-t">Plant scope schematic</title>
  <desc id="sch-d">A single-line diagram: HT incomer and transformer feed an LT panel, which powers a UPS for critical loads, a VFD driving a pump motor that feeds a water treatment plant, and EV chargers. Solar PV feeds the bus. A PLC and SCADA system supervises the drive and the treatment plant.</desc>
  <text class="sch-label" x="78" y="34">HT INCOMER</text>
  <path class="sch-line" d="M60 18v66"/><path class="sch-flow" d="M60 18v66"/>
  <circle class="sch-box" cx="60" cy="100" r="17"/><circle class="sch-box" cx="60" cy="124" r="17" style="fill:none"/>
  <text class="sch-label" x="88" y="116">TRANSFORMER</text>
  <path class="sch-line" d="M60 141v53"/><path class="sch-flow" d="M60 141v53"/>
  <rect class="sch-box" x="52" y="160" width="16" height="16"/>
  <path class="sch-box sch-box--green" d="M498 70h70l-14 34h-70z"/>
  <path d="M519 70l-14 34M540 70l-14 34M492 87h69" stroke="#9bbb59" stroke-width="1.5" fill="none"/>
  <text class="sch-label sch-label--green" x="488" y="58">SOLAR PV</text>
  <path class="sch-line" d="M526 104v90"/><path class="sch-flow" d="M526 104v90"/>
  <text class="sch-label sch-label--in" x="86" y="186">LT / MCC PANEL · 415 V</text>
  <path class="sch-bus" d="M36 200h580"/>
  <path class="sch-line" d="M120 200v52"/><path class="sch-flow" d="M120 200v52"/>
  <rect class="sch-box" x="92" y="252" width="56" height="36"/>
  <text class="sch-label sch-label--in" x="104" y="275">UPS</text>
  <path class="sch-line" d="M120 288v40"/>
  <rect class="sch-box sch-box--green" x="84" y="328" width="72" height="28"/>
  <text class="sch-label" x="92" y="346" style="font-size:9px">CRITICAL</text>
  <path class="sch-line" d="M250 200v44"/><path class="sch-flow" d="M250 200v44"/>
  <rect class="sch-box" x="222" y="244" width="56" height="36"/>
  <text class="sch-label sch-label--in" x="236" y="267">VFD</text>
  <path class="sch-line" d="M250 280v34"/>
  <circle class="sch-box" cx="250" cy="334" r="20"/>
  <text class="sch-label sch-label--in" x="243" y="339">M</text>
  <path class="sch-line" d="M270 334h18"/>
  <circle class="sch-box sch-box--green" cx="306" cy="334" r="18"/>
  <path d="M297 324l20 10-20 10z" fill="#9bbb59"/>
  <text class="sch-label" x="286" y="372">PUMP</text>
  <path class="sch-pipe" d="M324 334h70"/><path class="sch-flow sch-flow--water" d="M324 334h70"/>
  <rect class="sch-box sch-box--green" x="394" y="286" width="64" height="96" rx="14"/>
  <path d="M402 330h48" stroke="#9bbb59" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text class="sch-label sch-label--in" x="409" y="316">WTP</text>
  <path class="sch-pipe" d="M458 360h150"/><path class="sch-flow sch-flow--water" d="M458 360h150"/>
  <text class="sch-label sch-label--green" x="488" y="392">TREATED WATER</text>
  <path class="sch-line" d="M580 200v52"/><path class="sch-flow" d="M580 200v52"/>
  <rect class="sch-box" x="556" y="252" width="48" height="36"/>
  <text class="sch-label sch-label--in" x="569" y="275">EV</text>
  <rect class="sch-box" x="330" y="226" width="118" height="34" style="stroke:#b8a6e6"/>
  <text class="sch-label sch-label--in" x="340" y="248">PLC · SCADA</text>
  <circle class="sch-pulse" cx="436" cy="236" r="4"/>
  <path class="sch-ctrl" d="M330 252h-52"/><path class="sch-ctrl" d="M426 260v26"/><path class="sch-ctrl" d="M389 226V140h137"/>
  <text class="sch-label" x="334" y="132" style="fill:#b8a6e6">CONTROL · MONITORING</text>
</svg>"""



APPLICATIONS = {
    "pd": "Industrial plants, commercial facilities and infrastructure power networks.",
    "sw": "Electrical distribution, circuit protection and motor control systems.",
    "cl": "Industrial and building electrical, lighting and safety installations.",
    "pb": "Power continuity, power quality and energy systems for facilities and industry.",
    "au": "Machine control, plant automation and process monitoring.",
    "wp": "Industrial utilities, process plants, institutions and townships.",
    "bi": "Commercial facilities, industrial buildings and connected infrastructure.",
    "sv": "New installations, operating facilities and plant improvement projects.",
}
SPECIFICATIONS = {
    1: [("Voltage", "11 kV"), ("Breaker technology", "VCB / SF6"), ("Installation", "Indoor / outdoor kiosk")],
    7: [("Construction", "Oil & dry type"), ("Tap changing", "OLTC / OCTC"), ("Options", "Isolation & special purpose")],
    9: [("Configuration", "Silent / open"), ("Emissions", "CPCB IV+ options"), ("Support", "Service & spare parts")],
    12: [("Protection", "ELCB / RCCB / RCBO"), ("Sensitivity options", "30 / 100 / 300 mA")],
    27: [("Portfolio range", "1–4000 kVA"), ("Architecture", "Online / modular"), ("Scope", "UPS & data-centre power")],
    28: [("Battery options", "Lithium-ion / VRLA"), ("Systems", "Inverters, storage & chargers")],
    32: [("Installation", "Rooftop / ground-mounted"), ("Configuration", "On-grid / off-grid")],
    33: [("AC charging", "Wall-mount"), ("DC charging", "Fast chargers"), ("Make", "Delta")],
    34: [("Motor type", "LT induction"), ("Efficiency options", "IE2 / IE3")],
    35: [("Drive options", "Variable frequency / servo"), ("Scope", "Drives & servo motors"), ("Make", "Delta")],
    36: [("Controls", "PLC / HMI / SCADA"), ("Connectivity", "Industrial PCs & IIoT"), ("Make", "Delta")],
    39: [("Processes", "Filtration & clarification"), ("Applications", "Industrial, institutional & township")],
    40: [("Scope", "Effluent treatment & recycling"), ("Options", "Zero-liquid discharge")],
    41: [("Process options", "MBBR / SBR / MBR"), ("Scope", "Sewage treatment")],
    42: [("Technologies", "RO / DM / UF / softening"), ("Options", "Packaged drinking water plants")],
    46: [("Material", "Stainless steel 304"), ("Operation", "Touch-free"), ("Application", "Hygiene & cleanroom entry")],
}

def product_specs(p):
    return SPECIFICATIONS.get(p["no"], [("Product scope", p["desc"]), ("Options", str(len(p["variants"])) + " variants / types")])

def product_illustration(p):
    """Conceptual equipment drawings for products without supplied photos."""
    cat = p["cat"]
    if cat == "pd":
        parts = []
        for i in range(3):
            x = 160 + i * 92
            parts.append(f'<rect x="{x}" y="60" width="87" height="225" rx="3" fill="#e3e9e6"/><rect x="{x+9}" y="75" width="69" height="78" rx="2" fill="#f9fcf7"/><circle cx="{x+44}" cy="111" r="20"/><path d="M{x+44} 111l10-12"/><rect x="{x+22}" y="177" width="43" height="59" rx="2"/><path d="M{x+68} 193v24M{x+14} 257h59M{x+14} 264h59"/><circle cx="{x+26}" cy="164" r="3" fill="#85b95e"/><circle cx="{x+44}" cy="164" r="3" fill="#cda674"/>')
        shapes = ''.join(parts)
    elif cat == "sw":
        shapes = '<rect x="205" y="65" width="190" height="218" rx="8" fill="#e3e9e6"/><rect x="220" y="95" width="160" height="82" rx="3" fill="#fafbf8"/><rect x="274" y="123" width="52" height="72" rx="4" fill="#52677a"/><path d="M239 45v45M300 45v45M361 45v45M239 260v42M300 260v42M361 260v42" stroke-width="10"/><path d="M230 220h140M230 232h140M230 244h140"/>'
    elif cat == "cl":
        shapes = '<ellipse cx="300" cy="187" rx="116" ry="90" fill="#e3e9e6"/><ellipse cx="300" cy="187" rx="94" ry="72"/><ellipse cx="300" cy="187" rx="70" ry="54"/><ellipse cx="300" cy="187" rx="46" ry="36"/><ellipse cx="300" cy="187" rx="22" ry="17" fill="#fafbf8"/><path d="M416 187h60v-78M184 187h-56v65" stroke-width="7"/>'
    elif cat == "pb":
        shapes = '<rect x="217" y="49" width="166" height="246" rx="8" fill="#e3e9e6"/><rect x="239" y="73" width="122" height="51" rx="3" fill="#52677a"/><path d="M251 101h18l9-13 15 27 14-22 9 8h32" stroke="#c2e581"/><path d="M241 164h118M241 178h118M241 192h118M241 206h118M241 220h118M241 234h118M241 248h118"/><circle cx="344" cy="275" r="4" fill="#85b95e"/>'
    elif cat == "au":
        shapes = '<path d="M127 250h347" stroke-width="8"/><rect x="138" y="116" width="102" height="128" rx="4" fill="#e3e9e6"/><rect x="151" y="134" width="75" height="48" fill="#52677a"/><path d="M162 148h23M162 158h42" stroke="#c2e581"/>' + ''.join(f'<rect x="{x}" y="134" width="40" height="110" rx="3" fill="#e3e9e6"/><path d="M{x+10} 149h20M{x+10} 161h20M{x+10} 173h20M{x+10} 215h20M{x+10} 227h20"/>' for x in [250,298,346,394])
    elif cat == "wp":
        shapes = '<path d="M145 277h316M168 277V100h263v177M208 80V58h182v22"/>' + ''.join(f'<rect x="{x}" y="80" width="68" height="187" rx="30" fill="#e3e9e6"/><path d="M{x+34} 80V58M{x+34} 267v20M{x+12} 152h44"/>' for x in [190,278,366])
    elif cat == "bi":
        shapes = '<rect x="172" y="73" width="256" height="215" rx="3" fill="#e3e9e6"/><path d="M155 288h290M204 73V53h192v20M280 288v-55h40v55"/>' + ''.join(f'<rect x="{x}" y="{y}" width="35" height="35" rx="2" fill="#fafbf8"/>' for x in [196,254,312,370] for y in [100,161])
    else:
        shapes = '<circle cx="300" cy="177" r="105" fill="#e3e9e6"/><path d="M334 91a61 61 0 0 0-78 78l-68 68 32 32 68-68a61 61 0 0 0 78-78l-35 35-32-32z" fill="#fafbf8"/><circle cx="219" cy="237" r="9"/>'
    return f'<svg class="equipment-illustration" viewBox="0 0 600 340" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><ellipse cx="300" cy="302" rx="158" ry="8" fill="currentColor" opacity=".07" stroke="none"/>{shapes}</svg>'


def featured_products(numbers=(27, 35, 39, 33)):
    cards = []
    for no, label in [(27, "Power without interruption"), (35, "Control with precision"), (39, "Water that works harder"), (33, "Moving energy forward")]:
        if no not in numbers:
            continue
        p = next(p for p in PRODUCTS if p["no"] == no)
        im = p["images"][0]
        cards.append(f'''<a class="feature-card" href="products.html#p-{no}"><div class="feature-card__image"><img src="{im['src']}" alt="{E(im['title'])}" loading="lazy"><span>{E(CAT[p['cat']][1])}</span></div><div class="feature-card__copy"><small>{E(label)}</small><h3>{E(p['name'])}</h3><p>{E(p['desc'])}</p><span class="text-link">Explore {len(p['variants'])} variants {ARROW}</span></div></a>''')
    return "".join(cards)


def system_graphic():
    return open(os.path.join(HERE, "system-graphic.html"), encoding="utf-8").read()


def ecosystem_band():
    names = ["Delta", "Siemens", "ABB", "Schneider", "Honeywell", "Grundfos", "Kirloskar", "Eaton"]
    brands = ''.join(f'<span>{E(n)}</span>' for n in names if n in PARTNERS)
    return f'<section class="ecosystem-band" aria-label="Selected makes from our technology ecosystem"><div class="wrap"><p>Global technology.<br><b>Local accountability.</b></p><div class="ecosystem-makes">{brands}</div><a href="company-profile.html#partners" aria-label="See all business partners and makes">↗</a></div></section>'


def solution_gateways():
    groups = [("pd", "01", "Power that keeps you moving.", "From HT distribution to backup generation. Connect reliable equipment with complete electrical execution.", "silent-dg-set"), ("au", "02", "Intelligence in every process.", "Drives, controls and instrumentation that bring your machines, people and plant together.", "scada-system"), ("wp", "03", "A better flow of resources.", "Water treatment, wastewater, steam and process utilities. Designed around your operating conditions.", "wtp-on-site"), ("bi", "04", "Infrastructure for what’s next.", "Building systems, clean rooms, ICT and security. Connected spaces built for real working environments.", "cold-clean-rooms")]
    return ''.join(f'''<a class="solution-gateway" href="#cat-{cid}" data-gateway="{cid}"><img src="{sol(slug)['img']}" alt="{E(sol(slug)['title'])}" loading="lazy"><div><span>{num} / {E(CAT[cid][1])}</span><h3>{E(title)}</h3><p>{E(desc)}</p><b>Explore the capability <span aria-hidden="true">↗</span></b></div></a>''' for cid, num, title, desc, slug in groups)


def home():
    facts = [("2014–15", "Established"), ("3", "Countries: India · Nepal · Bhutan"), (str(len(INDUSTRIES)), "Industry sectors served"),
             (str(N_PRODUCTS), "Products"), (str(N_VARIANTS), "Variants &amp; types"), (MAKES_LABEL, "Makes supplied")]
    facts_html = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in facts)

    capabilities = [
        ("electrical", "Power & energy", "pd", "Electrical distribution, backup power, renewables and power quality, connected around your site."),
        ("automation", "Automation & control", "au", "Drives, instrumentation and PLC / HMI / SCADA integration for smarter plant operations."),
        ("water", "Water & process", "wp", "Water treatment, process utilities, chemicals and hygiene systems, from selection to service."),
        ("building", "Buildings & infrastructure", "bi", "Building systems, clean rooms, ICT and security for connected working environments."),
    ]
    vpanels = "".join(f'''<a class="vpanel" href="products.html#cat-{cat}">{icon(ic)}<h3>{E(name)}</h3><p>{E(text)}</p><span class="text-link">Explore solutions {ARROW}</span></a>''' for ic, name, cat, text in capabilities)

    body = f"""
<section class="hero on-navy">
  <div class="wrap">
    <div class="hero__copy">
      <span class="tag">Integrated engineering · Since 2014–15</span>
      <h1>Complex systems.<br>One <em>clear vision.</em></h1>
      <p>We connect power, automation, water and infrastructure. From engineering and integration to commissioning and long-term support, your entire project moves with one team.</p>
      <div class="btn-row">
        <a class="btn btn--green" href="products.html">Discover our solutions {ARROW}</a>
        <a class="btn btn--line-light" href="contact.html">Talk to our team ↗</a>
      </div>
    </div>
    {system_graphic()}
  </div>
</section>

{ecosystem_band()}
<section class="facts" aria-label="At a glance">
  <div class="wrap"><ul>{facts_html}</ul></div>
</section>

<section class="section home-capabilities">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">What we do</span>
        <h2>Connected expertise.<br>One accountable team.</h2>
        <p>Engineering, supply, installation and support across the systems your facility depends on.</p>
      </div>
      <a class="text-link" href="products.html">Explore all capabilities {ARROW}</a>
    </div>
    <div class="verticals verticals--4">{vpanels}</div>
  </div>
</section>

<section class="section section--wash featured-section">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px"><span class="tag">Selected systems</span><h2>Solutions in focus.</h2><p>A starting point for your next project. Explore our full portfolio for every product family and variant.</p></div>
      <a class="text-link" href="products.html">All {N_PRODUCTS} product families {ARROW}</a>
    </div>
    <div class="featured-grid home-featured-grid">{featured_products((27, 39))}</div>
  </div>
</section>

<nav class="home-explore" aria-label="Explore Chemotech">
  <div class="wrap">
    <a href="about.html"><span>Our people &amp; approach</span><b>Meet Chemotech <span aria-hidden="true">↗</span></b></a>
    <a href="company-profile.html#clients"><span>Clients &amp; project references</span><b>Explore our experience <span aria-hidden="true">↗</span></b></a>
    <a href="certifications.html"><span>Licences &amp; registrations</span><b>View our credentials <span aria-hidden="true">↗</span></b></a>
  </div>
</nav>
{cta()}"""
    page("index.html", "Home",
         "Chemotech International: electrical works, DG sets, UPS, VFD / PLC / SCADA automation, water and wastewater treatment, solar, EV charging, building and ICT systems for industry across India, Nepal and Bhutan.",
         body)


# --------------------------------------------------------------------------
# ABOUT
# --------------------------------------------------------------------------
def about():
    chain = ["Requirement & Design", "Sourcing & Supply", "Installation", "Commissioning", "Service & AMC"]
    chain_html = "".join(f"<li><small>Step {i}</small><b>{c}</b></li>" for i, c in enumerate(chain, 1))
    mission = ["Understand each customer's needs, priorities and operating conditions.",
               "Provide tailored solutions through a team committed to results and engagement.",
               "Keep improving customer satisfaction through a customer-driven approach."]
    values = [("Passion", "We stay curious and accountable to our customers' needs."),
              ("Teamwork", "Strong cooperation across disciplines and departments."),
              ("Efficiency", "Efficient, effective service at an affordable cost."),
              ("Innovation", "We support trade enquiries and question products and assumptions."),
              ("Profitability", "Customer loyalty that sustains long-term growth."),
              ("Integrity", "Business success and service quality built on ethical conduct.")]
    key_people = [
        ("30+", "Raman Kumar Jha", "", "Operations &amp; Project Handling",
         "Mechanical Engineer with more than 30 years in marketing and after-sales support for electro-mechanical equipment: diesel generating sets, industrial motors, power and distribution transformers and electrical panels."),
        ("25+", "Tapan Kumar Jha", "Partner", "Sales &amp; Marketing",
         "Science graduate with more than 25 years in marketing and project execution."),
        ("15+", "Shailendra Kumar Jha", "Partner", "Sales &amp; Marketing",
         "Graduate with more than 15 years in engineering material purchase and project execution, and 10 years in sales and marketing of industrial equipment, consumables and chemicals."),
        ("5+", "Mukund Jha", "", "Marketing &amp; Project Handling",
         "Mechanical Engineering graduate with more than 5 years in industrial water treatment and steam distribution projects."),
    ]
    people_html = "".join(f"""<article class="person">
        <div class="person__yrs"><b>{y}</b><span>years</span></div>
        <div><h3>{n}{f' <small>{p}</small>' if p else ''}</h3><p class="role">{r}</p><p>{d}</p></div>
      </article>""" for y, n, p, r, d in key_people)
    crew = [("18", "Murari Prashad", "Graduate", "Sales &amp; Marketing"),
            ("5", "Ajitanshu Anand", "B.Tech – Electrical &amp; Electronics", "Design, Programming, Sales &amp; Support"),
            ("5", "Manish Kumar", "Graduate", "Sales &amp; Services"),
            ("2", "Gunjan Kumar Mandal", "B.Tech – Electrical Engineering", "Service &amp; Support")]
    crew_html = "".join(f'<li><b class="yrs">{y}<small> yrs</small></b><h3>{n}</h3><span>{q}</span><span class="role">{r}</span></li>' for y, n, q, r in crew)
    reasons = ["Single-point coordination across electrical, automation and process requirements.",
               "Practical engineering focused on reliability, maintainability and ease of operation.",
               "Service support for commissioning, troubleshooting and plant improvement."]

    body = f"""
{page_hero("About Us", "A young team with decades of plant experience", "We understand how production works, what quality means on the shop floor, and how to present a solution that fits. That is how we have earned the trust of organisations of repute.", "About Chemotech")}

<section class="section">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <span class="tag">Who we are</span>
      <h2 style="font-size:var(--fs-2xl)">Focused, versatile and built around the client</h2>
      <p class="lead">Since 2014–15, Chemotech has grown into a stronger, more focused firm, with a team that brings a wide range of experience and looks for new challenges.</p>
    </div>
    <div class="prose">
      <p>We bring products, engineering and service together under one roof. Our team recommends equipment around site conditions, specifications and budget, then coordinates supply, installation, commissioning and after-sales support.</p>
      <p>Our best projects are collaborative. We work closely with clients to develop practical solutions, coordinate the disciplines involved and maintain a clear point of responsibility through execution and ongoing service.</p>
    </div>
  </div>
  <div class="wrap mt-lg">
    <p class="tag" style="margin-bottom:14px">End to end, handled seamlessly</p>
    <ol class="chain">{chain_html}</ol>
  </div>
</section>

<section class="section section--wash" id="vision">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Vision for Chemotech International</span>
      <h2>Vision, mission &amp; values</h2>
    </div>
    <div class="vision"><h3>Our vision</h3><p>To serve every customer with a clear understanding of their work, which drives our passion for innovative power solutions.</p></div>
    <div class="split mt-lg">
      <div class="stack" style="gap:14px">
        <h3 style="font-size:var(--fs-xl)">Our mission</h3>
        <p class="muted">Consistently exceed customer expectations. To do this, we commit to:</p>
      </div>
      <ul class="checklist">{"".join(f"<li>{m}</li>" for m in mission)}</ul>
    </div>
    <div class="mt-lg stack" style="gap:20px">
      <div class="stack" style="gap:8px">
        <h3 style="font-size:var(--fs-xl)">What we value</h3>
        <p class="muted">Our values are our voice. We pursue competitive excellence through:</p>
      </div>
      <ul class="values">{"".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in values)}</ul>
    </div>
  </div>
</section>

<section class="section" id="quality">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <span class="tag">Quality policy</span>
      <div class="quote-block"><blockquote>At Chemotech, quality means consistently exceeding our customers' needs, in service and in every other part of our business.</blockquote></div>
    </div>
    <div class="stack" style="gap:20px">
      <h3 style="font-size:var(--fs-lg)">We will</h3>
      <ol class="commit">
        <li><b>01</b>Understand the needs of our customers.</li>
        <li><b>02</b>Keep improving our systems and our Quality Management System.</li>
        <li><b>03</b>Give our customers the best of our services.</li>
      </ol>
      <p class="note">Everyone in the company is responsible for striving for the highest level of excellence and performance in everything we do.</p>
    </div>
  </div>
</section>

<section class="section section--wash" id="team">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Key persons in the Chemotech team</span>
      <h2>Our team</h2>
      <p>Engineers and commercial leads with experience across electro-mechanical equipment, water treatment, steam distribution and industrial sales.</p>
    </div>
    <div class="team">{people_html}</div>
    <h3 class="tag mt-lg" style="margin-bottom:16px">Sales, design &amp; service team</h3>
    <ul class="crew">{crew_html}</ul>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our approach</span>
      <h2>Expertise you can build on</h2>
    </div>
    <ul class="reasons">{"".join(f"<li>{r}</li>" for r in reasons)}</ul>
  </div>
</section>
{cta()}"""
    page("about.html", "About Us",
         "About Chemotech International: our story, vision, mission, values, quality policy and the team behind our electrical, automation, water and building projects.",
         body)


# --------------------------------------------------------------------------
# PRODUCTS (interactive catalogue)
# --------------------------------------------------------------------------
def products():
    counts = {c[0]: sum(1 for p in PRODUCTS if p["cat"] == c[0]) for c in CATEGORIES}
    chips = f'<button class="chip chip--all" type="button" data-cat="all" aria-pressed="true">All products <span>{N_PRODUCTS}</span></button>' + "".join(
        f'<button class="chip c-{c[0]}" type="button" data-cat="{c[0]}" aria-pressed="false">{E(c[1])} <span>{counts[c[0]]}</span></button>' for c in CATEGORIES)

    make_count = {}
    for p in PRODUCTS:
        for m in set(p["main_makes"]) | {m for v in p["variants"] for m in v["makes"]}:
            make_count[m] = make_count.get(m, 0) + 1
    make_opts = "".join(f'<option value="{E(m)}">{E(m)} ({n})</option>' for m, n in sorted(make_count.items(), key=lambda x: x[0].lower()))

    cards = []
    for p in PRODUCTS:
        c = CAT[p["cat"]]
        if p["images"]:
            im = p["images"][0]
            badge = f'<span class="count-badge">{len(p["images"])} photos</span>' if len(p["images"]) > 1 else ""
            media = f'<img src="{im["src"]}" alt="" loading="lazy">{badge}'
        else:
            media = f'<div class="equipment-tile"><span class="equipment-no">{p["no"]:02d} / {E(c[1])}</span>{product_illustration(p)}<span class="illustration-caption">Configuration illustration</span></div>'
        mk = "".join(f"<li>{E(m)}</li>" for m in p["main_makes"][:3])
        if len(p["main_makes"]) > 3:
            mk += f'<li>+{len(p["main_makes"])-3} makes</li>'
        nv = len(p["variants"])
        cards.append(f"""<article class="pcard c-{p['cat']}" data-no="{p['no']}" id="product-{p['no']}">
        <button class="pcard__open" type="button" aria-haspopup="dialog">
          <div class="pcard__media">{media}</div>
          <div class="pcard__body">
            <div class="pcard__meta"><span>{E(c[1])}</span><span>{len(p["variants"])} types</span></div>
            <h3>{E(p['name'])}</h3>
            <p>{E(p['desc'])}</p>
            <div class="variant-preview"><span>Available options</span><ul>{"".join(f"<li>{E(n)}</li>" for n in tile_names(p)[:2])}</ul></div>
            <ul class="mk" aria-label="Main makes">{mk}</ul>
            <span class="pcard__discover">Specifications &amp; all variants <span aria-hidden="true">↗</span></span>
          </div>
        </button>
        <div class="pcard__foot"><small>{nv} {"type" if nv == 1 else "variants"}</small>
          <button class="add-btn" type="button" data-add="{p['no']}" aria-pressed="false"><span class="ic-off">+ Add to enquiry</span><span class="ic-on">&check; Added</span></button></div>
      </article>""")

    groups = []
    for s in SOLUTIONS:
        if s["group"] not in groups:
            groups.append(s["group"])
    tabs = '<button class="chip chip--all" type="button" data-group="all" aria-pressed="true">All <span>30</span></button>' + "".join(
        f'<button class="chip" type="button" data-group="{E(g)}" aria-pressed="false">{E(g)} <span>{sum(1 for s in SOLUTIONS if s["group"] == g)}</span></button>' for g in groups)
    sol_cards = "".join(
        f'<button class="sol c-{CAT_BY_NO[s["products"][0]]}" type="button" data-i="{i}" data-group="{E(s["group"])}" aria-label="Enlarge photo: {E(s["title"])}">'
        f'<span class="media"><img src="{s["img"]}" alt="{E(s["title"])}" loading="lazy"></span>'
        f'<span class="cap"><em>{E(s["make"])}</em><b>{E(s["title"])}</b><span>{E(s["sub"])}</span></span></button>'
        for i, s in enumerate(SOLUTIONS))

    services = "".join(f"<li><span>{i:02d}</span>{E(s)}</li>" for i, s in enumerate(SERVICES, 1))

    data = {
        "categories": [{"id": c[0], "name": c[1], "blurb": c[4], "icon": icon(c[3], "")} for c in CATEGORIES],
        "products": [{"no": p["no"], "name": p["name"], "cat": p["cat"], "desc": p["desc"], "note": p["note"],
                      "main": p["main_makes"], "variants": p["variants"], "images": p["images"], "specs": product_specs(p), "application": APPLICATIONS[p["cat"]], "illustration": product_illustration(p) if not p["images"] else ""} for p in PRODUCTS],
        "solutions": [{"group": s["group"], "img": s["img"], "title": s["title"], "sub": s["sub"], "make": s["make"], "products": s["products"]} for s in SOLUTIONS],
    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    body = f"""
{page_hero("Our Products", "Intelligent systems.<br>Lasting impact.", f"Explore {N_PRODUCTS} product families, {N_VARIANTS} variants and connected engineering expertise. Explore the capability, discover the equipment, and shape a solution around your site.", "Product catalogue")}

<section class="section solution-discovery"><div class="wrap"><div class="section-head section-head--split"><div class="stack"><span class="tag">Explore by capability</span><h2>Start with the outcome.</h2><p>Every system begins with a real operating need. Find the discipline behind your next project.</p></div><a class="text-link" href="#catalogue">Browse all product families ↓</a></div><div class="solution-gateways">{solution_gateways()}</div></div></section>
<div class="cat-toolbar" role="search" aria-label="Filter products">
  <div class="wrap">
    <div class="cat-row">
      <div class="searchbox">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>
        <label class="visually-hidden" for="cat-search">Search products, variants and makes</label>
        <input id="cat-search" type="search" placeholder="Search e.g. 11 kV VCB, MBBR, Kirloskar, CCTV" autocomplete="off">
      </div>
      <div>
        <label class="visually-hidden" for="cat-make">Filter by make</label>
        <select id="cat-make"><option value="">All makes ({len(make_count)})</option>{make_opts}</select>
      </div>
      <span class="cat-count" id="cat-count" aria-live="polite">Showing <b>{N_PRODUCTS}</b> of {N_PRODUCTS} products</span>
    </div>
    <div class="chips-row" role="group" aria-label="Product categories">{chips}</div>
  </div>
</div>

<section class="section" id="catalogue" style="padding-top:36px">
  <div class="wrap">
    <div class="cat-intro">
      <h2 id="cat-title">All products</h2>
      <button class="link-btn" type="button" data-reset>Reset filters</button>
      <p id="cat-title-note">Select a product to see every variant and the makes we supply.</p>
    </div>
    <p class="catalogue-guidance">Explore specifications and types in each product. Final ratings, model availability and selection are confirmed against your project requirements.</p>
    <div class="pgrid">{"".join(cards)}</div>
    <div class="empty-state" id="cat-empty" hidden>
      <b>No products match these filters</b>
      <p>Try a shorter search, another make, or all categories. We also source items outside this list, so ask us if you can't find something.</p>
      <div class="btn-row"><button class="btn btn--ghost" type="button" data-reset>Clear filters</button><a class="btn" href="contact.html">Ask us</a></div>
    </div>
  </div>
</section>

<section class="section on-navy" style="background:var(--navy)">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Beyond equipment supply</span>
      <h2 style="color:var(--on-navy)">Support matched to your project</h2>
      <p>Engineering, installation, commissioning and maintenance are available to match the agreed scope of work.</p>
    </div>
    <ol class="services">{services}</ol>
  </div>
</section>

<section class="section section--wash" id="solutions">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our solutions</span>
      <h2>Solutions in pictures</h2>
      <p>Explore equipment and solution imagery from our supplied makes. Open a photo for details and related product families.</p>
    </div>
    <div class="chips-row sol-tabs" role="group" aria-label="Solution groups">{tabs}</div>
    <div class="sol-grid">{sol_cards}</div>
  </div>
</section>
{cta()}

<div class="tray" id="tray" hidden>
  <div class="tray__in">
    <span class="tray__count"><b id="tray-count">0</b><span class="tray__long" id="tray-label">products in your enquiry</span><span class="tray__short">in enquiry</span></span>
    <div class="tray__list" id="tray-list"></div>
    <div class="tray__actions"><button class="link-btn" type="button" id="tray-clear">Clear</button><a class="btn btn--green" href="quote.html">Request quote {ARROW}</a></div>
  </div>
</div>
<dialog class="pdialog" id="pdialog" aria-label="Product details"></dialog>
<dialog class="lightbox" id="lightbox" aria-label="Solution photo"></dialog>
<script type="application/json" id="catalogue-data">{data_json}</script>"""
    page("products.html", "Our Products",
         f"Chemotech International product catalogue: {N_PRODUCTS} products and {N_VARIANTS} variants across power distribution, switchgear, cabling, power backup, automation, water & process, building & ICT and services.",
         body, '<script src="assets/js/catalogue.js"></script>')


# --------------------------------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------------------------------
def company_profile():
    clients = "".join(f"<li>{E(c)}</li>" for c in CLIENTS)
    sugar = "".join(f"<li><span><b>{E(a)}</b><small>{E(b)}</small></span><span class=\"cap\">Sugar mill</span></li>" for a, b in SUGAR)
    dairy = "".join(f"<li><span><b>{E(a)}</b><small>{E(b)}</small></span><span class=\"cap\">{E(c)}</span></li>" for a, b, c in DAIRY)
    water = "".join(f"<li><span><b>{E(a)}</b><small>{E(b)}</small></span><span class=\"cap\">{E(c)}</span></li>" for a, b, c in WATER)
    partners = "".join(f'<li{" class=\"is-own\"" if n == "Delta" else ""}>{E(n)}</li>' for n in PARTNERS)

    body = f"""
{page_hero("Company Profile", "Chemotech International at a glance", "Engineering capabilities, verified registrations, project references and the people behind our work.", "Company profile")}

<section class="section">
  <div class="wrap split">
    <div class="stack" style="gap:18px">
      <span class="tag">Key information</span>
      <h2 style="font-size:var(--fs-2xl)">Company details</h2>
      <p class="muted">A partnership firm established in 2014–15, headquartered in Patna with a branch office in Delhi. One PAN covers both offices.</p>
      <a class="btn btn--ghost" href="certifications.html" style="justify-self:start">Licences &amp; registrations {ARROW}</a>
    </div>
    <div class="table-wrap">
      <table class="data data--kv">
        <tbody>
          <tr><th scope="row">Name of the company</th><td><b>Chemotech International</b></td></tr>
          <tr><th scope="row">Type of company</th><td>Partnership</td></tr>
          <tr><th scope="row">Partners</th><td>Tapan Kumar Jha · Shailendra Kumar Jha</td></tr>
          <tr><th scope="row">Year of establishment</th><td>2014–15</td></tr>
          <tr><th scope="row">PAN</th><td class="mono">AATFC8340G <small>Common for all offices</small></td></tr>
          <tr><th scope="row">Contact</th><td><a href="contact.html">Office addresses, phone numbers &amp; email</a></td></tr>
          <tr><th scope="row">Auditor</th><td>Mr. Ajit Choudhary, CA</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<nav class="office-links" aria-label="Office locations"><div class="wrap"><a href="contact.html#office-patna"><span>Head office · Bihar</span><b>Patna <span aria-hidden="true">↗</span></b></a><a href="contact.html#office-delhi"><span>Branch office · Delhi</span><b>Delhi <span aria-hidden="true">↗</span></b></a></div></nav>

<section class="section" id="clients">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our clients</span>
      <h2>Clients &amp; project references</h2>
      <p>A growing base of industries, institutions, hospitals, townships and government projects across India.</p>
    </div>
    <ul class="names">{clients}</ul>
    <div class="refs mt-lg">
      <article class="ref"><h3>Sugar mills</h3><ul>{sugar}</ul></article>
      <article class="ref"><h3>Dairy plants · ETP</h3><ul>{dairy}</ul></article>
      <article class="ref"><h3>Water softening, DM &amp; RO</h3><ul>{water}</ul></article>
    </div>
  </div>
</section>

<section class="section section--wash" id="presence">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">Our presence</span>
        <h2>We supply and serve these {len(INDUSTRIES)} industries</h2>
        <div class="presence"><span>India</span><span>Nepal</span><span>Bhutan</span></div>
      </div>
    </div>
    <ul class="industries">{industries_list()}</ul>
  </div>
</section>

<section class="section" id="partners">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our business partners</span>
      <h2>Leading makes we supply, install and service</h2>
    </div>
    <ul class="names names--partners">{partners}</ul>
    <p class="more-band">+ 90 more makes <span>across electrical, power, automation, water, building &amp; ICT</span></p>
  </div>
</section>

<section class="section section--tight"><div class="wrap portfolio-link"><div><span class="tag">Explore our capabilities</span><h2>{N_PRODUCTS} product families. One integrated portfolio.</h2><p>Browse specifications, variants and makes in our dedicated product catalogue.</p></div><a class="btn btn--ghost" href="products.html">Explore products {ARROW}</a></div></section>


{cta()}"""
    page("company-profile.html", "Company Profile",
         "Chemotech International company profile: key information, offices in Patna and Delhi, clients and project references, business partners and industries served.",
         body)


# --------------------------------------------------------------------------
# CERTIFICATIONS
# --------------------------------------------------------------------------
def certifications():
    body = f"""
{page_hero("Certifications", "Licensed and registered to execute", "Electrical contractor licences in Bihar and Delhi, BCD Bihar Class 3 and Haryana Engineering Works Portal registration, with valid GST registrations in both states.", "Licences &amp; registrations")}

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Electrical contractor licences</span>
      <h2>Licences to execute electrical works</h2>
    </div>
    <div class="lic-cards">
      <article class="lic">
        <header><small>Govt. of NCT of Delhi · Labour Department</small><h3>Delhi – Licence to Electrical Contractors</h3></header>
        <dl>
          <dt>Application No.</dt><dd class="mono">50590000009296</dd>
          <dt>Valid</dt><dd>16/06/2025 – 15/06/2050</dd>
          <dt>Premises</dt><dd>Kh. No. 44/18 &amp; 44/19, Inderprastha Colony, Burari, Delhi – 110084</dd>
          <dt>Represented by</dt><dd>Tapan Kumar Jha, Partner</dd>
        </dl>
      </article>
      <article class="lic">
        <header><small>Govt. of Bihar · Electrical Licensing Board, Patna</small><h3>Bihar – Electrical Contractor Licence</h3></header>
        <dl>
          <dt>Registration No.</dt><dd class="mono">50/2025</dd>
          <dt>File ref.</dt><dd class="mono">IV-03(72)/2025</dd>
          <dt>Valid</dt><dd>08/07/2025 – 07/07/2030</dd>
          <dt>Licensee</dt><dd>Tapan Kumar Jha, Partner</dd>
          <dt>Test equipment</dt><dd>Insulation Megger &amp; Earth Tester (National)</dd>
        </dl>
      </article>
    </div>
  </div>
</section>

<section class="section section--tight section--wash">
  <div class="wrap">
    <div class="section-head" style="margin-bottom:24px">
      <span class="tag">Contractor registrations</span>
      <h2>Works contractor registrations</h2>
    </div>
    <div class="stack" style="gap:12px">
      <div class="reg-banner" style="background:var(--paper)">
        <div><h3>Building Construction Department, Govt. of Bihar</h3><p>Registration No. <b>3260569</b> · Valid 08/07/2026 – 07/07/2031</p></div>
        <span class="class">Class 3</span>
      </div>
      <div class="reg-banner" style="background:var(--paper);border-left-color:var(--green)">
        <div><h3>Haryana Engineering Works Portal, Govt. of Haryana</h3><p>Contractor ID <b>2026R31684</b> · Dated 26/10/2026</p></div>
        <span class="class" style="background:var(--green);color:var(--navy-deep)">Haryana</span>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Tax &amp; business registrations</span>
      <h2>Registration details</h2>
    </div>
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th scope="col">Registration</th><th scope="col">Number</th><th scope="col">Valid from</th></tr></thead>
        <tbody>
          <tr><th scope="row">GST – Bihar</th><td class="mono">10AATFC8340G1ZJ</td><td>21/06/2024</td></tr>
          <tr><th scope="row">GST – Delhi</th><td class="mono">07AATFC8340G1Z6</td><td>01/06/2024</td></tr>
          <tr><th scope="row">PAN</th><td class="mono">AATFC8340G</td><td>09/04/2024</td></tr>
          <tr><th scope="row">Udyam (MSME) – Micro</th><td class="mono">UDYAM-BR-26-0136033</td><td>10/07/2024</td></tr>
          <tr><th scope="row">Firm Registration – Bihar</th><td class="mono">F2600000083<small>Register No. F000233/2026 · Indian Partnership Act, 1932</small></td><td>21/04/2026</td></tr>
        </tbody>
      </table>
    </div>
    <div class="note mt-md">Need copies of any licence or registration for vendor onboarding? <a href="contact.html">Contact us</a> and we will send them.</div>
  </div>
</section>
{cta()}"""
    page("certifications.html", "Certifications",
         "Chemotech International licences and registrations: Delhi and Bihar electrical contractor licences, BCD Bihar Class 3, Haryana Engineering Works Portal, GST, PAN, Udyam MSME and firm registration.",
         body)


# --------------------------------------------------------------------------
# CONTACT & QUOTE
# --------------------------------------------------------------------------
def status_box():
    return f"""<div class="form-status" role="status" hidden>
        <b>Your email app should now open with the message ready to send.</b>
        Press send there to reach us. If nothing opened, email <a href="mailto:{INBOX}">{INBOX}</a> or call +91 98999 82418.
      </div>"""


def field(id_, label, kind="text", required=False, opt=False, attrs="", msg="", full_label=None):
    req = " required" if required else ""
    o = ' <span class="opt">(optional)</span>' if opt else ""
    dmsg = f' data-msg="{msg}"' if msg else ""
    dl = E(full_label or label)
    if kind == "textarea":
        ctl = f'<textarea id="{id_}" name="{id_}" data-label="{dl}"{req}{dmsg} {attrs}></textarea>'
    else:
        ctl = f'<input id="{id_}" name="{id_}" type="{kind}" data-label="{dl}"{req}{dmsg} {attrs}>'
    err = f'<span class="err" data-err-for="{id_}" aria-live="polite"></span>' if required else ""
    return f'<div class="field"><label for="{id_}">{label}{o}</label>{ctl}{err}</div>'


def contact():
    body = f"""
{page_hero("Contact", "Talk to our engineers", "Discuss your project with our team in Patna or Delhi. Share your site, scope and priorities so we can help you select the right approach.", "Contact us")}

<section class="section">
  <div class="wrap">
    {office_cards()}
    <div class="btn-row mt-md">
      <a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query=Pratiksha+Bhawan+Maurya+Vihar+Colony+Transport+Nagar+Patna+800026" target="_blank" rel="noopener">Patna office on map {ARROW}</a>
      <span aria-hidden="true" class="muted">·</span>
      <a class="text-link" href="https://www.google.com/maps/search/?api=1&amp;query=Inderprastha+Colony+Burari+Delhi+110084" target="_blank" rel="noopener">Delhi office on map {ARROW}</a>
    </div>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap form-layout">
    <form class="form" data-mailto="Website enquiry" novalidate>
      <fieldset>
        <legend>Send us a message</legend>
        <div class="row">
          {field("name", "Your name", required=True, attrs='autocomplete="name"', msg="Please enter your name.", full_label="Name")}
          {field("company", "Company", opt=True, attrs='autocomplete="organization"')}
        </div>
        <div class="row">
          {field("email", "Email", "email", required=True, attrs='autocomplete="email"', msg="Please enter a valid email address.")}
          {field("phone", "Phone", "tel", opt=True, attrs='autocomplete="tel"')}
        </div>
        <div class="field">
          <label for="office">Office to contact</label>
          <select id="office" name="office" data-label="Office">
            <option>Head office – Patna</option>
            <option>Delhi office</option>
            <option>Not sure</option>
          </select>
        </div>
        {field("message", "Message", "textarea", required=True, msg="Please tell us how we can help.")}
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <button class="btn" type="submit">Prepare message {ARROW}</button>
        <small>Opens your email app with the message filled in, addressed to {INBOX}.</small>
      </div>
    </form>
    <aside class="aside">
      <div class="aside-card">
        <h3>Need a price?</h3>
        <p>Pick products in the catalogue, then use the quote form to share quantities and site location. It helps us respond faster with the right technical offer.</p>
        <a class="btn btn--ghost" href="products.html" style="justify-self:start">Browse products {ARROW}</a>
      </div>
    </aside>
  </div>
</section>"""
    page("contact.html", "Contact",
         "Contact Chemotech International: head office in Patna, Bihar and branch office in Burari, Delhi. Phone +91 98999 82418, info.chemotechinternational@gmail.com.",
         body)


def quote():
    checks = "".join(f'<label><input type="checkbox" name="category" value="{E(c[1])}">{E(c[1])}</label>' for c in CATEGORIES)
    body = f"""
{page_hero("Request Quote", "Request a quote", "Share what you need and where. Our team will review the scope and come back with a technical and commercial offer.", "Quotation")}

<section class="section section--wash">
  <div class="wrap form-layout">
    <form class="form" data-mailto="Quote request" novalidate>
      <fieldset>
        <legend>1 · Your details</legend>
        <div class="row">
          {field("name", "Your name", required=True, attrs='autocomplete="name"', msg="Please enter your name.", full_label="Name")}
          {field("company", "Company / organisation", required=True, attrs='autocomplete="organization"', msg="Please enter your company or organisation.", full_label="Company")}
        </div>
        <div class="row">
          {field("email", "Email", "email", required=True, attrs='autocomplete="email"', msg="Please enter a valid email address.")}
          {field("phone", "Phone", "tel", required=True, attrs='autocomplete="tel"', msg="Please enter a phone number.")}
        </div>
      </fieldset>
      <fieldset>
        <legend>2 · What do you need?</legend>
        <div class="picked" id="picked" hidden>
          <p><b>From the catalogue:</b> these products will be included in your request.</p>
          <ul></ul>
          <a class="text-link" href="products.html">Add more products {ARROW}</a>
        </div>
        <input type="hidden" id="picked-input" data-label="Catalogue products">
        <div class="checks" role="group" aria-label="Categories" data-label="Categories">{checks}</div>
      </fieldset>
      <fieldset>
        <legend>3 · Scope</legend>
        {field("requirement", "Quantities, ratings and details", "textarea", required=True, msg="Please describe what you need.", attrs='placeholder="e.g. 2 × 200 kVA online UPS with 30 min backup; 5 HP VFD panels for pumps; 50 KLD STP (MBBR)"', full_label="Requirement")}
        <div class="row">
          {field("site", "Site location", required=True, msg="Please enter the site location.", attrs='placeholder="City, state, country"', full_label="Site location")}
          <div class="field">
            <label for="timeline">Required by</label>
            <select id="timeline" name="timeline" data-label="Required by">
              <option>Within 1 month</option>
              <option>1 – 3 months</option>
              <option>3 – 6 months</option>
              <option>Budgetary quote only</option>
            </select>
          </div>
        </div>
        <div class="row">
          <div class="field">
            <label for="service">Scope of work</label>
            <select id="service" name="service" data-label="Scope of work">
              <option>Supply only</option>
              <option>Supply &amp; installation</option>
              <option>Turnkey (design to commissioning)</option>
              <option>Service / AMC</option>
            </select>
          </div>
          {field("makes", "Preferred makes", opt=True, attrs='placeholder="e.g. Delta, Kirloskar, L&amp;T"', full_label="Preferred makes")}
        </div>
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <button class="btn" type="submit">Prepare quote email {ARROW}</button>
        <small>Opens your email app with your request filled in. Attach drawings, BOQs or datasheets there before sending.</small>
      </div>
    </form>
    <aside class="aside">
      <div class="aside-card">
        <h3>What happens next</h3>
        <ol>
          <li>We review your requirement and operating conditions.</li>
          <li>An engineer calls if we need site details or drawings.</li>
          <li>You receive a technical and commercial offer.</li>
        </ol>
      </div>
      <div class="aside-card">
        <h3>Prefer to call?</h3>
        <a class="big-phone" href="tel:+919899982418">+91 98999 82418</a>
        <p>Delhi: <a href="tel:+919312282418">+91 93122 82418</a></p>
        <a href="mailto:{INBOX}">{INBOX}</a>
      </div>
      <div class="aside-card">
        <h3>Pick from the catalogue</h3>
        <p>Open any product in our <a href="products.html">catalogue</a> and choose &ldquo;Add to enquiry&rdquo;. Your picks appear in this form.</p>
      </div>
    </aside>
  </div>
</section>"""
    page("quote.html", "Request Quote",
         "Request a quotation from Chemotech International for panels, transformers, DG sets, UPS, VFD, PLC, SCADA, water treatment plants, hygiene stations, pre-fab structures, networking and CCTV.",
         body)


home(); about(); products(); company_profile(); certifications(); contact(); quote()
print(f"built: {N_PRODUCTS} products, {N_VARIANTS} variants, {N_MAKES} makes, {len(SOLUTIONS)} solution photos")
