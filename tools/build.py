#!/usr/bin/env python3
"""Generates the static Chemotech International site.

Usage:  python3 tools/build.py .

Content sources (edit these, then re-run):
  tools/products.json   56 products / 332 variants / makes (from the Product Master List,
                        refresh with tools/import_products_docx.py)
  tools/solutions.json  solution photos, captions, makes and linked product numbers
  this file             page copy, clients, partners, registrations, contact details
"""
import hashlib, html, json, os, re, sys
from pathlib import Path

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
E = html.escape

# Set to False to hide per-variant makes on the public site (main makes still show).
SHOW_VARIANT_MAKES = True


NAV = [
    ("index.html", "Home"),
    ("solutions.html", "Solutions"),
    ("products.html", "Products"),
    ("projects.html", "Projects"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

def arrow_svg(direction="right"):
    paths = {"right": "M4 12h16m-6-6 6 6-6 6", "up-right": "M6 18 18 6M6 6h12v12", "down": "M12 4v16m-6-6 6 6 6-6"}
    return f'<svg class="arrow arrow--{direction}" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="{paths[direction]}"/></svg>'


ARROW = arrow_svg()
ARROW_UP_RIGHT = arrow_svg("up-right")
ARROW_DOWN = arrow_svg("down")

ICONS = {
    "electrical": '<rect x="4" y="3" width="16" height="18"/><path d="M13 6.5 9.5 12h4L11 17.5"/>',
    "switch": '<rect x="5" y="3" width="14" height="18"/><circle cx="12" cy="9" r="2.6"/><path d="M12 11.6V17M9 17h6"/>',
    "cable": '<path d="M3 6h7a3.5 3.5 0 0 1 0 7H7a3.5 3.5 0 0 0 0 7h14"/><circle cx="3" cy="6" r="1"/>',
    "power": '<rect x="3" y="7" width="15" height="10"/><path d="M18 10h2.5v4H18"/><path d="M11 8.8 8.6 12h3.6L10 15.2"/>',
    "automation": '<rect x="7" y="7" width="10" height="10"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>',
    "water": '<path d="M12 3c-4 5-6.2 8.2-6.2 11.2a6.2 6.2 0 0 0 12.4 0C18.2 11.2 16 8 12 3z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "chemicals": '<path d="M9 3h6M10 3v6.2l-5.3 8.9A2 2 0 0 0 6.4 21h11.2a2 2 0 0 0 1.7-2.9L14 9.2V3"/><path d="M7.4 15h9.2"/>',
    "location": '<path d="M20 10c0 6-8 11-8 11S4 16 4 10a8 8 0 1 1 16 0z"/><circle cx="12" cy="10" r="2.5"/>',
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
PRODUCTS = json.loads(Path(HERE, "products.json").read_text(encoding="utf-8"))
SOLUTIONS = json.loads(Path(HERE, "solutions.json").read_text(encoding="utf-8"))
COMPANY = json.loads(Path(HERE, "company.json").read_text(encoding="utf-8"))
INBOX = COMPANY["contacts"]["primary_email"]

# 8 product categories, as colour-keyed in the 2026 company profile (product numbers in order)
CATEGORIES = [
    ("pd", "Power Distribution", range(1, 10), "electrical", "HT and LT panels, MCC, synchronising and APFC panels, transformers, substations and multi-brand DG sets."),
    ("sw", "Switchgear & Controls", range(11, 17), "switch", "Breakers, earth-leakage protection, DBs, changeovers, contactors, relays, indication and metering."),
    ("cl", "Cabling, Lighting & Safety", range(17, 27), "cable", "Power and control cables, wires, accessories, LED and street lighting, fans, earthing, fire alarm and PA."),
    ("pb", "Power Backup & Energy", range(27, 34), "power", "Online UPS and data-centre power, batteries, stabilisers, harmonic filters, EMS, solar and EV charging."),
    ("au", "Automation & Instrumentation", [34, 35, 36, 37, 38, 57], "automation", "Motors, drives, PLC / HMI / SCADA, plant automation, flow / level / pressure instruments and water quality analysers."),
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

# Representative product photos from Wikimedia Commons (credits: assets/img/products/CREDITS.md)
COMMONS_PHOTOS = {
    1: ('assets/img/products/01-ht-panels.jpg', 'HT Panels', 'Representative photo · Zen 38 · CC BY-SA 3.0 · Wikimedia Commons'),
    2: ('assets/img/products/02-lt-pcc-distribution-panels.jpg', 'LT / PCC & Distribution Panels', 'Representative photo · Kgbo · CC BY-SA 4.0 · Wikimedia Commons'),
    3: ('assets/img/products/03-mcc-motor-control-panels.jpg', 'MCC & Motor Control Panels', 'Representative photo · Wtshymanski · CC BY-SA 3.0 · Wikimedia Commons'),
    4: ('assets/img/products/04-synchronising-amf-panels.jpg', 'Synchronising & AMF Panels', 'Representative photo · Andy Dingley · CC BY-SA 3.0 · Wikimedia Commons'),
    5: ('assets/img/products/05-apfc-capacitor-panels.jpg', 'APFC & Capacitor Panels', 'Representative photo · Wikimedia Commons contributor · CC BY-SA 3.0 · Wikimedia Commons'),
    6: ('assets/img/products/06-feeder-pillars-street-light-panels.jpg', 'Feeder Pillars & Street-Light Panels', 'Representative photo · Андрей Романенко · CC BY-SA 4.0 · Wikimedia Commons'),
    8: ('assets/img/products/08-compact-unitised-substations.jpg', 'Compact / Unitised Substations', 'Representative photo · AndrewHarvey4 · CC0 · Wikimedia Commons'),
    11: ('assets/img/products/11-circuit-breakers.jpg', 'Circuit Breakers', 'Representative photo · Balurbala · CC BY-SA 3.0 · Wikimedia Commons'),
    12: ('assets/img/products/12-earth-leakage-protection.jpg', 'Earth-Leakage Protection', 'Representative photo · Jimbob82 · Public domain · Wikimedia Commons'),
    13: ('assets/img/products/13-distribution-boards.jpg', 'Distribution Boards', 'Representative photo · Dmitry G · CC BY-SA 3.0 · Wikimedia Commons'),
    14: ('assets/img/products/14-isolators-changeover-ats.jpg', 'Isolators, Changeover & ATS', 'Representative photo · StcudorPrewoP · CC BY-SA 3.0 · Wikimedia Commons'),
    15: ('assets/img/products/15-contactors-starters-relays.jpg', 'Contactors, Starters & Relays', 'Representative photo · Kae · CC BY-SA 3.0 · Wikimedia Commons'),
    16: ('assets/img/products/16-control-indication-metering.jpg', 'Control, Indication & Metering', 'Representative photo · Quist161 · CC BY-SA 4.0 · Wikimedia Commons'),
    17: ('assets/img/products/17-ht-lt-power-control-cables.jpg', 'HT & LT Power & Control Cables', 'Representative photo · Hannes Grobe · CC BY-SA 3.0 · Wikimedia Commons'),
    18: ('assets/img/products/18-wires-special-cables.jpg', 'Wires & Special Cables', 'Representative photo · Cjp24 · CC BY-SA 4.0 · Wikimedia Commons'),
    19: ('assets/img/products/19-cable-accessories-containment.jpg', 'Cable Accessories & Containment', 'Representative photo · Santeri Viinamäki · CC BY-SA 4.0 · Wikimedia Commons'),
    20: ('assets/img/products/20-wiring-accessories.jpg', 'Wiring Accessories', 'Representative photo · Santeri Viinamäki · CC BY-SA 4.0 · Wikimedia Commons'),
    21: ('assets/img/products/21-indoor-industrial-led-lighting.jpg', 'Indoor & Industrial LED Lighting', 'Representative photo · Flametechcontrolgear · CC0 · Wikimedia Commons'),
    22: ('assets/img/products/22-street-area-solar-lighting.jpg', 'Street, Area & Solar Lighting', 'Representative photo · Jacek Halicki · CC BY-SA 4.0 · Wikimedia Commons'),
    23: ('assets/img/products/23-fans.jpg', 'Fans', 'Representative photo · Muthukumaran Esakkiappan · CC BY-SA 4.0 · Wikimedia Commons'),
    24: ('assets/img/products/24-earthing-lightning-protection.jpg', 'Earthing & Lightning Protection', 'Representative photo · Wikimedia Commons contributor · CC BY-SA 3.0 · Wikimedia Commons'),
    25: ('assets/img/products/25-fire-detection-alarm.jpg', 'Fire Detection & Alarm', 'Representative photo · Wikimedia Commons contributor · CC BY-SA 4.0 · Wikimedia Commons'),
    26: ('assets/img/products/26-public-address-sound-systems.jpg', 'Public Address & Sound Systems', 'Representative photo · Misternomer · CC BY 3.0 · Wikimedia Commons'),
    30: ('assets/img/products/30-harmonic-filters-pf-correction.jpg', 'Harmonic Filters & PF Correction', 'Representative photo · Holger Urban · CC BY-SA 4.0 · Wikimedia Commons'),
    31: ('assets/img/products/31-energy-management-system.jpg', 'Energy Management System', 'Representative photo · Rasik Tirodkar · CC BY-SA 4.0 · Wikimedia Commons'),
    34: ('assets/img/products/34-electrical-motors-actuators.jpg', 'Electrical Motors & Actuators', 'Representative photo · ZngZng · CC BY-SA 3.0 · Wikimedia Commons'),
    45: ('assets/img/products/45-process-chemicals-lubrication.jpg', 'Process Chemicals & Lubrication', 'Representative photo · LaurelBloch · CC BY-SA 4.0 · Wikimedia Commons'),
    48: ('assets/img/products/48-lifts.jpg', 'Lifts', 'Representative photo · P1898 · CC BY 4.0 · Wikimedia Commons'),
    49: ('assets/img/products/49-air-conditioning-ventilation.jpg', 'Air-Conditioning & Ventilation', 'Representative photo · Dinkun Chen · CC BY-SA 4.0 · Wikimedia Commons'),
    52: ('assets/img/products/52-structured-cabling-networking-lan.jpg', 'Structured Cabling & Networking (LAN)', 'Representative photo · Dsimic · CC BY-SA 4.0 · Wikimedia Commons'),
    53: ('assets/img/products/53-cctv-security.jpg', 'CCTV & Security', 'Representative photo · MichalPL · CC BY-SA 4.0 · Wikimedia Commons'),
    54: ('assets/img/products/54-it-communication.jpg', 'IT & Communication', 'Representative photo · -stk · CC BY-SA 4.0 · Wikimedia Commons'),
    55: ('assets/img/products/55-electrical-installation-contracting.jpg', 'Electrical Installation & Contracting', 'Representative photo · Team Massachusetts 4D Home · CC BY 2.0 · Wikimedia Commons'),
    56: ('assets/img/products/56-testing-commissioning-o-m-amc.jpg', 'Testing, Commissioning, O&M & AMC', 'Representative photo · MTA Capital Construction Mega Projects · CC BY 2.0 · Wikimedia Commons'),
}

# Keep the supplied source and licence links available beside representative photos.
COMMONS_CREDITS = {}
with open(os.path.join(HERE, "../assets/img/products/CREDITS.md"), encoding="utf-8") as credit_file:
    for line in credit_file:
        credit = re.match(r"- \*\*(\d+) .*?\*\*.*?\]\((https://commons\.wikimedia\.org/.*?)\) by (.*?), (.*)$", line)
        if credit:
            licence_link = re.search(r"(https://creativecommons\.org/[^\s)]+)", credit[4])
            COMMONS_CREDITS[int(credit[1])] = {"source": credit[2], "license_url": licence_link[1] if licence_link else ""}

for p in PRODUCTS:
    p["cat"] = CAT_BY_NO[p["no"]]
    imgs = [dict(src=s["img"], title=s["title"], sub=s["sub"], make=s["make"]) for s in SOLUTIONS if p["no"] in s["products"]]
    imgs += [dict(src=a, title=b, sub=c, make=d) for a, b, c, d in EXTRA_IMAGES.get(p["no"], [])]
    if not imgs and p["no"] in COMMONS_PHOTOS:
        src, title, sub = COMMONS_PHOTOS[p["no"]]
        imgs = [dict(src=src, title=title, sub=sub, make="", **COMMONS_CREDITS.get(p["no"], {}))]
    p["images"] = imgs
    if not SHOW_VARIANT_MAKES:
        for v in p["variants"]:
            v["makes"] = []

N_PRODUCTS = len(PRODUCTS)
N_VARIANTS = sum(len(p["variants"]) for p in PRODUCTS)
N_MAKES = len({m for p in PRODUCTS for v in p["variants"] for m in v["makes"]} | {m for p in PRODUCTS for m in p["main_makes"]})
assert (N_PRODUCTS, N_VARIANTS) == (56, 332)

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

CLIENTS = COMPANY["clients"]
PARTNERS = COMPANY["partners"]

SERVICES = ["Engineering & technical solution design", "Equipment selection & supply", "System integration",
            "Installation", "Testing & commissioning", "Troubleshooting",
            "Preventive maintenance & O&M support", "After-sales service & plant improvement"]

def phone_links(numbers):
    return [("+" + re.sub(r"\D", "", number), number) for number in numbers]


PHONES_PATNA = phone_links(COMPANY["contacts"]["offices"]["patna"]["phones"])
PHONES_DELHI = phone_links(COMPANY["contacts"]["offices"]["delhi"]["phones"])
PHONES_GENERAL = phone_links(COMPANY["contacts"]["general_phones"])


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
      <img src="assets/img/chemotech-logo.png" width="1820" height="300" alt="Chemotech International – a Clean and Conditioning Company">
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
    phones = "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_GENERAL)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="logo-tile"><img src="assets/img/chemotech-logo.png" width="1820" height="300" alt="Chemotech International" loading="lazy"></div>
        <p class="tagline">…a Clean and Conditioning company</p>
        <p>Integrated electrical, power, automation, water, process, building and ICT solutions for industry and government projects since 2014–15.</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul><li><a href="solutions.html">Solutions &amp; Services</a></li><li><a href="products.html">Product catalogue</a></li><li><a href="projects.html">Projects &amp; Clients</a></li></ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul><li><a href="about.html">About Chemotech</a></li><li><a href="certifications.html">Licences &amp; Registrations</a></li><li><a href="contact.html">Contact &amp; offices</a></li><li><a href="quote.html">Request a Quote</a></li></ul>
      </div>
      <div>
        <h4>Reach us</h4>
        <ul>
          {phones}
          <li><a href="mailto:{INBOX}">{INBOX}</a></li>

        </ul>
      </div>
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
    with open(os.path.join(HERE, "../assets/css/profile.css"), "rb") as profile_theme:
        profile_version = hashlib.sha256(profile_theme.read()).hexdigest()[:12]
    main_version = hashlib.sha256(Path(HERE, "../assets/js/main.js").read_bytes()).hexdigest()[:12]
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{E(description)}">
<meta name="theme-color" content="#00008B">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{E(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/img/chemotech-logo.png">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/modern.css">
<link rel="stylesheet" href="assets/css/immersive.css?v={theme_version}">
<link rel="stylesheet" href="assets/css/profile.css?v={profile_version}">
</head>
<body>
{header(filename)}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/js/main.js?v={main_version}"></script>
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


def cta(title="Let’s plan the right solution for your site.", action="Request a quote", target="quote.html", secondary="products.html", secondary_label="Browse products"):
    return f"""<section class="cta on-navy">
  <div class="wrap">
    <div>
      <h2>{E(title)}</h2>
      <p>Call <a href="tel:+919899982418">+91 98999 82418</a> or write to <a href="mailto:{INBOX}">{INBOX}</a></p>
    </div>
    <div class="btn-row">
      <a class="btn btn--green" href="{target}">{E(action)} {ARROW}</a>
      <a class="btn btn--line-light" href="{secondary}">{E(secondary_label)}</a>
    </div>
  </div>
</section>"""


def industries_list():
    return "".join(f'<li{" class=\"is-key\"" if "Government" in n else ""}><span class="list-number" aria-hidden="true">{i:02d}</span><span class="list-copy">{E(n)}</span></li>' for i, n in enumerate(INDUSTRIES, 1))


def office_cards():
    pp = '<ul class="contact-methods">' + "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_PATNA) + '</ul>'
    dp = '<ul class="contact-methods">' + "".join(f'<li><a href="tel:{a}">{b}</a></li>' for a, b in PHONES_DELHI) + '</ul>'
    def email_links(office):
        return '<ul class="contact-methods">' + ''.join('<li><a href="mailto:' + E(email) + '">' + E(email).replace('@', '<wbr>@') + '</a></li>' for email in COMPANY["contacts"]["offices"][office]["emails"]) + '</ul>'
    ep, ed = email_links("patna"), email_links("delhi")
    return f"""<div class="offices">
      <article class="office" id="office-patna">
        <span class="tag">Head office · Bihar</span>
        <div class="office-heading">{icon("location")}<h3>Patna</h3></div>
        <address>Pratiksha Bhawan, Maurya Vihar Colony,<br>Near Bihar Urology Centre, Transport Nagar,<br>Patna, Bihar – 800026</address>
        <dl>
          <dt>Phone</dt><dd>{pp}</dd>
          <dt>Email</dt><dd>{ep}</dd>
        </dl>
        <div class="gstin"><span class="gstin__label">GSTIN · Bihar</span><span class="gstin__number">10AATFC8340G1ZJ</span></div>
      </article>
      <article class="office" id="office-delhi">
        <span class="tag">Branch office · Delhi</span>
        <div class="office-heading">{icon("location")}<h3>Delhi</h3></div>
        <address>Maya Garden, Ground Floor, Kh. No. 44/18 &amp; 44/19,<br>Gate No. 02, Inderprastha (IP) Colony, Block-C,<br>Village Burari, North Delhi – 110084</address>
        <dl>
          <dt>Phone</dt><dd>{dp}</dd>
          <dt>Email</dt><dd>{ed}</dd>
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
    38: [("Measurements", "Flow / level / pressure"), ("Flow options", "Electromagnetic / ultrasonic"), ("Level options", "Radar / ultrasonic")],
    57: [("Measurements", "Chlorine / turbidity / pH / ORP / conductivity"), ("Wastewater analysis", "BOD / COD"), ("Applications", "Water supply & wastewater")],
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
    return Path(HERE, "system-graphic.html").read_text(encoding="utf-8")


def ecosystem_band():
    names = ["Delta", "Eaton", "Kirloskar", "Paikane", "Krykard", "SBEM", "Toshcon Instruments", "KEC International"]
    brands = ''.join(f'<span>{E(n)}</span>' for n in names if n in PARTNERS)
    return f'<section class="ecosystem-band" aria-label="Selected OEM partners"><div class="wrap"><p>OEM technology.<br><b>Local accountability.</b></p><div class="ecosystem-makes">{brands}</div><a href="solutions.html#partners" aria-label="See all OEM partners">{ARROW_UP_RIGHT}</a></div></section>'


def solution_gateways():
    groups = [("pd", "01", "Power that keeps you moving.", "From HT distribution to backup generation. Connect reliable equipment with complete electrical execution.", "silent-dg-set"), ("au", "02", "Intelligence in every process.", "Drives, controls and instrumentation that bring your machines, people and plant together.", "scada-system"), ("wp", "03", "A better flow of resources.", "Water treatment, wastewater, steam and process utilities. Designed around your operating conditions.", "wtp-on-site"), ("bi", "04", "Infrastructure for what’s next.", "Building systems, clean rooms, ICT and security. Connected spaces built for real working environments.", "cold-clean-rooms")]
    return ''.join(f'''<a class="solution-gateway" href="#cat-{cid}" data-gateway="{cid}"><img src="{sol(slug)['img']}" alt="{E(sol(slug)['title'])}" loading="lazy"><div><span>{num} / {E(CAT[cid][1])}</span><h3>{E(title)}</h3><p>{E(desc)}</p><b>Explore the capability {ARROW_UP_RIGHT}</b></div></a>''' for cid, num, title, desc, slug in groups)


def home():
    facts = [("10+", "Years in business"), ("3", "Countries: India · Nepal · Bhutan"), ("20+", "Industry sectors served"),
             (str(N_PRODUCTS), "Product families"), ("300+", "Variants &amp; types"), ("50+", "Named OEM partners")]
    facts_html = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in facts)

    capabilities = [
        ("electrical", "Power & energy", "pd", "Electrical distribution, backup power, renewables and power quality, connected around your site."),
        ("automation", "Automation & control", "au", "Drives, instrumentation and PLC / HMI / SCADA integration for smarter plant operations."),
        ("water", "Water & process", "wp", "Water treatment, process utilities, chemicals and hygiene systems, from selection to service."),
        ("building", "Buildings & infrastructure", "bi", "Building systems, clean rooms, ICT and security for connected working environments."),
    ]
    vpanels = "".join(f'''<a class="vpanel" href="solutions.html#{cat}">{icon(ic)}<h3>{E(name)}</h3><p>{E(text)}</p><span class="text-link">Explore solutions {ARROW}</span></a>''' for ic, name, cat, text in capabilities)

    body = f"""
<section class="hero on-navy">
  <div class="wrap">
    <div class="hero__copy">
      <span class="tag">Integrated engineering · Since 2014–15</span>
      <h1>Complex systems.<br>One <em>clear vision.</em></h1>
      <p>We connect power, automation, water and infrastructure. From engineering and integration to commissioning and long-term support, your entire project moves with one team.</p>
      <div class="btn-row">
        <a class="btn btn--green" href="solutions.html">Discover our solutions {ARROW}</a>
        <a class="btn btn--line-light" href="contact.html">Talk to our team {ARROW_UP_RIGHT}</a>
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
      <a class="text-link" href="solutions.html">Explore all capabilities {ARROW}</a>
    </div>
    <div class="verticals verticals--4">{vpanels}</div>
  </div>
</section>

<section class="section section--wash featured-section">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px"><span class="tag">Selected systems</span><h2>Solutions in focus.</h2><p>A starting point for your next project. Explore our full portfolio for every product family and variant.</p></div>
      <a class="text-link" href="products.html">Explore {N_PRODUCTS} product families {ARROW}</a>
    </div>
    <div class="featured-grid home-featured-grid">{featured_products((27, 39))}</div>
  </div>
</section>

<section class="section home-delivery">
  <div class="wrap delivery-layout">
    <figure class="delivery-visual"><img src="assets/img/solutions/wtp-on-site.jpg" alt="Process installation with treatment vessels, piping and electrical controls" loading="lazy" width="1000" height="750"><figcaption><span>CONNECTED EXECUTION</span><b>From individual systems<br>to a coordinated facility.</b></figcaption></figure>
    <div class="delivery-copy">
      <span class="tag">How your project takes shape</span>
      <h2>Clarity at every stage.<br>Continuity beyond handover.</h2>
      <p>We coordinate equipment, controls and utilities around your site requirements, with an agreed scope from the first discussion through ongoing service.</p>
      <ol class="delivery-steps">
        <li><span class="list-number" aria-hidden="true">01</span><div><h3>Understand &amp; engineer</h3><p>Study operating conditions, align specifications and select equipment that fits the process.</p></div></li>
        <li><span class="list-number" aria-hidden="true">02</span><div><h3>Supply &amp; integrate</h3><p>Coordinate sourcing and installation across electrical, automation and process requirements.</p></div></li>
        <li><span class="list-number" aria-hidden="true">03</span><div><h3>Commission &amp; support</h3><p>Test the installation, support handover and plan maintenance around the agreed service scope.</p></div></li>
      </ol>
      <a class="text-link" href="solutions.html#delivery">Discover our approach {ARROW}</a>
    </div>
  </div>
</section>

<nav class="home-explore" aria-label="Explore Chemotech">
  <div class="wrap">
    <a href="about.html"><span>Our people &amp; approach</span><b>Meet Chemotech {ARROW_UP_RIGHT}</b></a>
    <a href="projects.html#clients"><span>Clients &amp; project references</span><b>Explore our experience {ARROW_UP_RIGHT}</b></a>
    <a href="certifications.html"><span>Licences &amp; registrations</span><b>View our credentials {ARROW_UP_RIGHT}</b></a>
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
    values = [("Passion", "We stay curious and accountable to our customers' needs."),
              ("Teamwork", "Strong cooperation across disciplines and departments."),
              ("Efficiency", "Practical, cost-effective engineering and service."),
              ("Innovation", "We explore better equipment, methods and ideas for each application."),
              ("Profitability", "Customer loyalty that sustains long-term growth."),
              ("Integrity", "Business success and service quality built on ethical conduct.")]
    key_people = [
        ("34+", "Raman Kumar Jha", "", "Operations &amp; Project Handling",
         "Mechanical Engineer with more than 34 years in marketing and after-sales support for electro-mechanical equipment: diesel generating sets, industrial motors, power and distribution transformers and electrical panels."),
        ("29+", "Tapan Kumar Jha", "Partner", "Sales &amp; Marketing",
         "Science graduate with more than 29 years in marketing and project execution."),
        ("19+", "Shailendra Kumar Jha", "Partner", "Sales &amp; Marketing",
         "Graduate with more than 19 years in engineering material purchase and project execution, and 14 years in sales and marketing of industrial equipment, consumables and chemicals."),
        ("8+", "Mukund Jha", "", "Marketing &amp; Project Handling",
         "Mechanical Engineering graduate with more than 8 years in industrial water treatment and steam distribution projects."),
    ]
    people_html = "".join(f"""<article class="person">
        <div class="person__yrs"><b>{y}</b><span>years</span></div>
        <div><h3>{n}{f' <small>{p}</small>' if p else ''}</h3><p class="role">{r}</p><p>{d}</p></div>
      </article>""" for y, n, p, r, d in key_people)
    crew = [("21", "Murari Prashad", "Graduate", "Sales &amp; Marketing"),
            ("8", "Ajitanshu Anand", "B.Tech – Electrical &amp; Electronics", "Design, Programming, Sales &amp; Support"),
            ("8", "Manish Kumar", "Graduate", "Sales &amp; Services"),
            ("5", "Gunjan Kumar Mandal", "B.Tech – Electrical Engineering", "Service &amp; Support")]
    crew_html = "".join(f'<li><b class="yrs">{y}<small> yrs</small></b><h3>{n}</h3><span>{q}</span><span class="role">{r}</span></li>' for y, n, q, r in crew)
    body = f"""
{page_hero("About Us", "People with decades of plant experience", "We understand how production works, what quality means on the shop floor, and how to present a solution that fits. That is how we have earned the trust of organisations of repute.", "About Chemotech")}

<section class="section" id="approach">
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
</section>
<section class="section section--wash" id="vision"><div class="wrap">
  <div class="section-head"><span class="tag">Our commitments</span><h2>Practical engineering. Lasting relationships.</h2><p>We listen to operating needs, recommend suitable equipment and remain accountable through the agreed scope of work.</p></div>
  <ul class="values">{"".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in values if a in ["Teamwork", "Efficiency", "Innovation", "Integrity"])}</ul>
</div></section>

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

<section class="section" id="company-details"><div class="wrap split"><div class="stack"><span class="tag">Company information</span><h2>Established in 2014–15. Based in Patna and Delhi.</h2><p>A partnership firm serving industrial, institutional and government projects across India, Nepal and Bhutan.</p><a class="text-link" href="certifications.html">Licences &amp; registrations {ARROW}</a></div><dl class="company-facts"><dt>Legal name</dt><dd>Chemotech International</dd><dt>Company type</dt><dd>Partnership</dd><dt>Partners</dt><dd>Tapan Kumar Jha · Shailendra Kumar Jha</dd><dt>Company PAN</dt><dd>AATFC8340G</dd></dl></div></section>
{cta("Meet the team behind your next project.", "Talk to our team", "contact.html")}"""
    page("about.html", "About Us",
         "About Chemotech International: our story, values, company information and the team behind our electrical, automation, water and building projects.",
         body)


# --------------------------------------------------------------------------
# PRODUCTS (interactive catalogue)
# --------------------------------------------------------------------------
def solutions():
    groups = [
        ("pd", "Power & energy", "electrical", ["pd", "sw", "cl", "pb"], "Coordinate distribution, backup power and power quality around the loads your facility depends on.", "Panels and transformers; DG sets and UPS; solar, EV charging and energy management.", ["Define loads, ratings and backup requirements", "Select compatible equipment and protection", "Plan installation, testing and service"]),
        ("au", "Automation & control", "automation", ["au"], "Connect field instruments, drives and control systems for the operating needs of your plant.", "Motors and VFDs; PLC, HMI and SCADA; flow, level, pressure and water-quality instrumentation.", ["Review the process and control requirements", "Coordinate instruments, panels and programming", "Support commissioning and troubleshooting"]),
        ("wp", "Water & process", "water", ["wp"], "Bring treatment equipment, utilities and process support together around the required application and capacity.", "WTP, RO, DM and UF systems; ETP and STP; steam distribution, piping, chemicals and hygiene.", ["Discuss water quality, capacity and site conditions", "Select treatment stages and supporting utilities", "Agree commissioning, maintenance and O&M scope"]),
        ("bi", "Buildings & infrastructure", "building", ["bi"], "Coordinate the systems that support safe, connected and practical working environments.", "Building management, HVAC, lifts, clean rooms and pre-fab structures; networking, CCTV and IT.", ["Review occupancy, services and infrastructure needs", "Select building systems and connected equipment", "Coordinate installation and ongoing support"]),
    ]
    sections = []
    for cid, title, ic, cats, description, equipment, steps in groups:
        photos = [photo for photo in SOLUTIONS if photo["products"] and CAT_BY_NO.get(photo["products"][0]) in cats]
        def photo_card(photo):
            return f'<a class="application-photo" href="products.html#p-{photo["products"][0]}"><img src="{E(photo["img"])}" alt="{E(photo["title"])}" loading="lazy" width="1000" height="750"><span><b>{E(photo["title"])}</b><small>{E(photo["make"]) if photo["make"] else "Application context"} · View related equipment</small></span></a>'
        gallery = ''.join(photo_card(photo) for photo in photos[:2])
        more = '<details class="photo-details"><summary>More equipment &amp; application images</summary><div class="application-gallery">' + ''.join(photo_card(photo) for photo in photos[2:]) + '</div></details>' if len(photos)>2 else ''
        links = ''.join(f'<a class="text-link" href="products.html#cat-{cat}">{E(CAT[cat][1])} {ARROW}</a>' for cat in cats)
        sections.append(f'<section class="section solution-section" id="{cid}"><div class="wrap"><div class="solution-layout"><div class="stack">{icon(ic)}<h2>{E(title)}</h2><p class="lead">{E(description)}</p><p>{E(equipment)}</p><ul class="checklist">'+''.join(f'<li><span class="list-copy">{E(step)}</span></li>' for step in steps)+f'</ul><div class="solution-equipment-links">{links}</div></div><div><div class="application-gallery">{gallery}</div>{more}</div></div></div></section>')
    services = ''.join(f'<li>{icon("service")}<span>{E(service)}</span></li>' for service in SERVICES)
    partners = ''.join(f'<li>{E(name)}</li>' for name in PARTNERS)
    body = f"""
{page_hero("Solutions & Services", "Engineering around the way your site works.", "Explore four connected disciplines, with equipment selection, installation, commissioning and support matched to your agreed scope.", "Solutions & services")}
<nav class="section-nav wrap" aria-label="Solution disciplines"><a href="#pd">Power &amp; energy</a><a href="#au">Automation</a><a href="#wp">Water &amp; process</a><a href="#bi">Buildings</a><a href="#delivery">Delivery &amp; service</a></nav>
{"".join(sections)}
<section class="section section--wash" id="delivery"><div class="wrap"><div class="section-head"><span class="tag">From requirement to service</span><h2>One coordinated delivery process.</h2><p>We agree the responsibilities and deliverables for your project before execution.</p></div><ol class="chain">{"".join(f'<li><div class="chain-head"><small>Step {i}</small>{icon(ic)}</div><b>{E(label)}</b></li>' for i,(ic,label) in enumerate([("automation","Requirement & design"),("electrical","Sourcing & supply"),("service","Installation"),("switch","Testing & commissioning"),("service","Service & AMC")],1))}</ol><h3 class="service-heading">Choose the support your project needs</h3><ul class="service-options">{services}</ul><p class="note">Supply-only, installation, turnkey and service scopes are available by agreement. <a href="certifications.html">View our licences and registrations.</a></p></div></section>
<section class="section" id="partners"><div class="wrap"><div class="section-head"><span class="tag">Equipment sourcing</span><h2>Established makes. Application-led selection.</h2><p>We work with 50+ named OEMs across our portfolio. Final makes, ratings and model availability are confirmed against your requirements.</p></div><details class="oem-details"><summary>View the full OEM list</summary><ul class="names names--partners">{partners}</ul><p class="more-band">+ 80 more makes <span>across the disciplines we serve</span></p></details></div></section>
{cta("Let’s define the right scope together.", "Discuss your requirements", "contact.html")}"""
    page("solutions.html", "Solutions & Services", "Power, automation, water, process and building engineering: equipment selection, supply, installation, commissioning and maintenance from Chemotech International.", body)


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
        cards.append(f"""<article class="pcard c-{p['cat']}" data-no="{p['no']}" id="product-{p['no']}">
        <button class="pcard__open" type="button" aria-haspopup="dialog">
          <div class="pcard__media">{media}</div>
          <div class="pcard__body">
            <div class="pcard__meta"><span>{E(c[1])}</span><span>{len(p["variants"])} {"type" if len(p["variants"]) == 1 else "types"}</span></div>
            <h3>{E(p['name'])}</h3>
            <p>{E(p['desc'])}</p>
            <span class="pcard__discover">Specifications &amp; all variants {ARROW_UP_RIGHT}</span>
          </div>
        </button>
        <div class="pcard__foot">
          <button class="add-btn" type="button" data-add="{p['no']}" aria-pressed="false"><span class="ic-off">+ Add to enquiry</span><span class="ic-on">&check; Added</span></button></div>
      </article>""")

    data = {
        "redirects": {"10": 9},
        "categories": [{"id": c[0], "name": c[1], "blurb": c[4], "icon": icon(c[3], "")} for c in CATEGORIES],
        "products": [{"no": p["no"], "catalogue_no": p["catalogue_no"], "name": p["name"], "cat": p["cat"], "desc": p["desc"], "note": p["note"],
                      "main": p["main_makes"], "variants": p["variants"], "images": p["images"], "specs": product_specs(p), "application": APPLICATIONS[p["cat"]], "illustration": product_illustration(p) if not p["images"] else ""} for p in PRODUCTS],

    }
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    body = f"""
<section class="catalogue-hero"><div class="wrap"><div class="crumbs"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>Products</span></div><h1>Find the equipment for your project.</h1><p>{N_PRODUCTS} product families · 300+ variants. Search by equipment, specification or make.</p><a class="text-link" href="solutions.html">Need help defining the system? Explore solutions {ARROW}</a></div></section>
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
      <span class="cat-count" id="cat-count" aria-live="polite"><b>{N_PRODUCTS}</b> matching products</span>
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
    <p class="catalogue-guidance">Explore specifications and types in each product. Photos illustrate product families; final makes, ratings and model availability are confirmed against your project requirements.</p>
    <div class="pgrid" id="product-grid">{"".join(cards)}</div>
    <div class="catalogue-more"><button class="btn btn--ghost" id="show-more" type="button" aria-controls="product-grid" hidden>Show more products</button><p id="catalogue-progress" aria-live="polite"></p></div>
    <div class="empty-state" id="cat-empty" hidden>
      <b>No products match these filters</b>
      <p>Try a shorter search, another make, or all categories. If you can't find the item, share your requirement with our team.</p>
      <div class="btn-row"><button class="btn btn--ghost" type="button" data-reset>Clear filters</button><a class="btn" href="contact.html">Ask us</a></div>
    </div>
  </div>
</section>

{cta("Have your equipment shortlist ready?", "Build your enquiry", "quote.html", "contact.html", "Ask a question")}

<div class="tray" id="tray" hidden>
  <div class="tray__in">
    <span class="tray__count"><b id="tray-count">0</b><span class="tray__long" id="tray-label">products in your enquiry</span><span class="tray__short">in enquiry</span></span>
    <div class="tray__list" id="tray-list" tabindex="0" role="region" aria-label="Products in your enquiry"></div>
    <div class="tray__actions"><button class="link-btn" type="button" id="tray-clear">Clear</button><a class="btn btn--green" href="quote.html">Request quote {ARROW}</a></div>
  </div>
</div>
<dialog class="pdialog" id="pdialog" aria-label="Product details"></dialog>
<script type="application/json" id="catalogue-data">{data_json}</script>"""
    page("products.html", "Our Products",
         f"Chemotech International product catalogue: {N_PRODUCTS} products and {N_VARIANTS} variants across power distribution, switchgear, cabling, power backup, automation, water & process, building & ICT and services.",
         body, '<script src="assets/js/catalogue.js?v=' + hashlib.sha256(Path(HERE, "../assets/js/catalogue.js").read_bytes()).hexdigest()[:12] + '"></script>')


# --------------------------------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------------------------------
def projects():
    clients = "".join(f"<li>{E(c)}</li>" for c in CLIENTS)
    project_cards = "".join('<article class="ref"><h3>' + E(title) + '</h3><ul>' + ''.join('<li><span><b>' + E(name) + '</b><small>' + E(location) + '</small></span>' + ('<span class="cap">' + E(capacity) + '</span>' if capacity else '') + '</li>' for name, location, capacity in entries) + '</ul></article>' for title, entries in COMPANY["projects"].items())

    body = f"""
{page_hero("Projects & Clients", "Experience across plants, utilities and infrastructure.", "Explore documented project references by application, location and capacity, alongside the organisations we serve.", "Projects & clients")}
<nav class="section-nav wrap" aria-label="Project sections"><a href="#references">Project references</a><a href="#clients">Clients</a><a href="#presence">Industries served</a></nav>
<section class="section" id="references"><div class="wrap"><div class="section-head"><span class="tag">Selected experience</span><h2>Project references by application</h2><p>Locations and capacities follow our company profile. Each reference describes the recorded application; detailed scope can be discussed with our team.</p></div><div class="refs">{project_cards}</div></div></section>
<section class="section" id="clients">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our clients</span>
      <h2>Organisations we serve</h2>
      <p>Government bodies, PSUs, industries, institutions, hospitals and infrastructure projects across India, Nepal and Bhutan.</p>
    </div>
    <ul class="names">{clients}</ul>

  </div>
</section>

<section class="section section--wash" id="presence">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">Our presence</span>
        <h2>Serving 20+ industry sectors</h2>
        <div class="presence"><span>India</span><span>Nepal</span><span>Bhutan</span></div>
      </div>
    </div>
    <ul class="industries">{industries_list()}</ul>
  </div>
</section>

{cta("Planning a similar application?", "Discuss your project", "contact.html")}"""
    page("projects.html", "Projects & Clients", "Chemotech project references, clients, locations, capacities and industries served across India, Nepal and Bhutan.", body)
    legacy = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0;url=projects.html"><title>Company information · Chemotech International</title><script>var h=location.hash;location.replace((h==="#partners"?"solutions.html#partners":h==="#company-details"?"about.html#company-details":"projects.html"+h));</script></head><body><p>Continue to <a href="projects.html">Projects &amp; Clients</a> or <a href="about.html#company-details">company information</a>.</p></body></html>'
    Path(OUT, "company-profile.html").write_text(legacy, encoding="utf-8")


# --------------------------------------------------------------------------
# CERTIFICATIONS
# --------------------------------------------------------------------------
def certifications():
    body = f"""
{page_hero("Licences & Registrations", "Licensed and registered to execute", "Electrical contractor licences in Bihar and Delhi, BCD Bihar Class 3 and Haryana Engineering Works Portal registration, with valid GST registrations in both states.", "Licences &amp; registrations")}

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
    <div class="table-wrap" tabindex="0" role="region" aria-label="Registration details table">
      <table class="data">
        <thead><tr><th scope="col">Registration</th><th scope="col">Number</th><th scope="col">Registered on</th></tr></thead>
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
{cta("Check the credentials for your scope.", "Discuss your requirements", "contact.html")}"""
    page("certifications.html", "Licences & Registrations",
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
<nav class="section-nav wrap" aria-label="Contact options"><a href="#enquiry">Write an enquiry</a><a href="#office-patna">Patna office</a><a href="#office-delhi">Delhi office</a></nav>

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
    <form class="form" id="enquiry" data-mailto="Website enquiry" data-recipient="{INBOX}" novalidate>
      <fieldset>
        <legend>Prepare your enquiry</legend><p class="form-explainer">This form prepares a draft. Send it from your email app, or copy the message into your email service.</p>
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
            <option>Not sure</option>
            <option>Head office – Patna</option>
            <option>Delhi office</option>
          </select>
        </div>
        {field("message", "Message", "textarea", required=True, msg="Please tell us how we can help.")}
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <div class="btn-row form-actions"><button class="btn" type="submit">Prepare message {ARROW}</button><button class="btn btn--ghost" type="button" data-copy-message>Copy message</button></div>
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
         f"Contact Chemotech International: head office in Patna, Bihar and branch office in Burari, Delhi. Phone +91 98999 82418, {INBOX}.",
         body)


def quote():
    checks = "".join(f'<label><input type="checkbox" name="category" value="{E(c[1])}">{E(c[1])}</label>' for c in CATEGORIES)
    body = f"""
{page_hero("Request Quote", "Request a quote", "Share your equipment, scope and site details. Prepare an email enquiry for our team to review and discuss with you.", "Quotation")}

<script type="application/json" id="product-index">{json.dumps({str(p["no"]): {"name": p["name"], "catalogue_no": p["catalogue_no"]} for p in PRODUCTS}, ensure_ascii=False).replace("</", "<\\/")}</script>
<section class="section section--wash">
  <div class="wrap form-layout">
    <form class="form" data-mailto="Quote request" data-recipient="{INBOX}" novalidate>
      <fieldset>
        <legend>1 · Your details</legend><p class="form-explainer">Prepare your enquiry here, then send it from your email app. You can also copy the draft into your email service.</p>
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
        </div>
        <p id="picked-notice" class="selection-notice" role="status" aria-live="polite"></p>
        <a class="text-link quote-catalogue-link" id="quote-catalogue-link" href="products.html">Browse products to add to your enquiry {ARROW}</a>
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
              <option>Not sure yet</option>
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
              <option>Please advise on scope</option>
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
        <div class="btn-row form-actions"><button class="btn" type="submit">Prepare quote email {ARROW}</button><button class="btn btn--ghost" type="button" data-copy-message>Copy enquiry</button></div>
        <small>Opens your email app with your request filled in. Attach drawings, BOQs or datasheets there before sending.</small>
      </div>
    </form>
    <aside class="aside">
      <div class="aside-card">
        <h3>What happens next</h3>
        <ol>
          <li><span class="list-copy">We review your requirement and operating conditions.</span></li>
          <li><span class="list-copy">Our team may contact you for site details or drawings.</span></li>
          <li><span class="list-copy">You receive a technical and commercial offer.</span></li>
        </ol>
      </div>
      <div class="aside-card">
        <h3>Prefer to call?</h3>
        <a class="big-phone" href="tel:+919899982418">+91 98999 82418</a>
        <a class="text-link" href="contact.html">All office contacts {ARROW}</a>
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


home(); about(); solutions(); products(); projects(); certifications(); contact(); quote()
print(f"built: {N_PRODUCTS} products, {N_VARIANTS} variants, {N_MAKES} makes, {len(SOLUTIONS)} solution photos")
