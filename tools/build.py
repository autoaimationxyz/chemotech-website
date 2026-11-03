#!/usr/bin/env python3
"""Generates the static Chemotech International site into the repo root."""
import html, sys, os

OUT = sys.argv[1]
E = html.escape

INBOX = "info.chemotechinternational@gmail.com"
PATNA_MAIL = "chemotech.international@gmail.com"
DELHI_MAIL = "tapan.chemotech@gmail.com"

NAV = [
    ("index.html", "Home"),
    ("about.html", "About Us"),
    ("products.html", "Our Products"),
    ("company-profile.html", "Company Profile"),
    ("certifications.html", "Certifications"),
    ("contact.html", "Contact"),
]

ARROW = '<span class="arrow" aria-hidden="true">&rarr;</span>'

ICONS = {
    "electrical": '<rect x="4" y="3" width="16" height="18"/><path d="M13 6.5 9.5 12h4L11 17.5"/>',
    "power": '<rect x="3" y="7" width="15" height="10"/><path d="M18 10h2.5v4H18"/><path d="M11 8.8 8.6 12h3.6L10 15.2"/>',
    "automation": '<rect x="7" y="7" width="10" height="10"/><rect x="10" y="10" width="4" height="4"/><path d="M9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4"/>',
    "water": '<path d="M12 3c-4 5-6.2 8.2-6.2 11.2a6.2 6.2 0 0 0 12.4 0C18.2 11.2 16 8 12 3z"/><path d="M9 15a3 3 0 0 0 3 3"/>',
    "chemicals": '<path d="M9 3h6M10 3v6.2l-5.3 8.9A2 2 0 0 0 6.4 21h11.2a2 2 0 0 0 1.7-2.9L14 9.2V3"/><path d="M7.4 15h9.2"/>',
    "building": '<path d="M4 21V8.5L12 3l8 5.5V21"/><path d="M2.5 21h19M9.5 21v-5.5h5V21M8 10.5h2M14 10.5h2"/>',
}


def icon(key):
    return (f'<svg class="vicon" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.6" stroke-linecap="square" aria-hidden="true">{ICONS[key]}</svg>')


# --------------------------------------------------------------------------
# Product master data (Product Master List, November 2026)
# --------------------------------------------------------------------------
VERTICALS = [
    {
        "id": "electrical", "n": 1, "cls": "v1",
        "name": "Electrical Works & Power Distribution",
        "short": "HT / LT, MCC and synchronising panels, substations, transformers, DG sets, switchgear, cabling, lighting, earthing and fire detection systems.",
        "intro": "Complete electrical scope for plants and buildings, from the HT incomer and substation down to switchgear, cabling, lighting and life-safety systems.",
        "subs": [
            ("HT & LT Panels", ["HT Panel", "LT Panel", ("MCC Panel", "Motor control centre"), "MF Panel", ("Synchronising Panel", "DG / source synchronising"), "Electrical Distribution Panels", ("Control & Machine Control Panels", "Automation / machine control"), "Feeder Pillars"]),
            ("Substations, Transformers & Generation", ["Unitised Substations", ("Transformers", "Oil & dry type; power & distribution"), ("CT / PT – Cast Resin", "Current & potential transformers"), ("Diesel Generating Sets", "Incl. electrical integration")]),
            ("Switchgear & Protection", [("MCCB", "Moulded case circuit breakers"), ("MCB", "Miniature circuit breakers"), ("ELCB / RCCB", "Earth leakage protection"), "Distribution Boards (DBs)", "HRC Fuses", "Contactors", "Timers & Relays", "APFC Relays"]),
            ("Control, Indication & Metering", ["Selector Switches", "Rotary & Toggle Switches", "Push Buttons", "Indicating Lamps / LED Indicating Lights", "Terminal Blocks", ("Voltmeters & Ammeters", "Analogue panel meters"), ("Digital Meters", "Multifunction / energy meters")]),
            ("Cables, Wires & Accessories", [("Industrial Cabling – HT & LT Power Cables", "Supply, laying & termination"), ("PVC Insulated Copper Wires", "650 / 1100 V grade"), "Telephone Wires", "Telephone Tag Blocks", "PVC Conduits", "PVC Conduit Accessories", "Cable Glands", "Cable Lugs"]),
            ("Wiring Accessories", [("Modular Switches & Sockets", "Light & power accessories"), "Ceiling Roses & Allied Accessories", ("Laminated Sheets", "For switchboards / panels")]),
            ("Lighting & Fans", ["LED Light Fixtures", "Fluorescent Light Fixtures", "Street Lighting Solutions", "Lighting Poles", "Ceiling Fans", "Exhaust Fans"]),
            ("Earthing, Lightning & Surge Protection", [("Earthing", "Conventional pipe / plate"), "Chemical Earthing", "Lightning Protection System", "Surge Protection System"]),
            ("Fire Detection & Alarm (FDA)", ["Main FDA Panel", "Manual Call Points", "Response Indicators", "Smoke Detectors", "Heat Detectors", ("Public Address System", "Amplifier, hooter / speaker, mic, console")]),
            ("Vertical Transport", ["Lifts"]),
        ],
    },
    {
        "id": "power", "n": 2, "cls": "v2",
        "name": "Power Backup, Quality & Energy",
        "short": "Online UPS and batteries, servo stabilisers, harmonic filters, APFC and VAR solutions, solar power, EV charging and energy management.",
        "intro": "Clean, continuous power for critical loads: backup, voltage regulation, power-quality correction, renewables and e-mobility.",
        "subs": [
            ("UPS & Batteries", [("Online UPS Systems", "1 kVA – 4000 kVA, Delta"), "Lithium-ion Batteries", ("VRLA Batteries", "For UPS & FDA systems")]),
            ("Voltage Regulation", ["Servo Voltage Stabilisers"]),
            ("Power Quality & Power Factor", [("Active Harmonic Filter", "AHF / PQC"), "Harmonic Filters", ("APFC Panels", "Automatic power factor correction"), ("VAR Generators", "Power factor controller")]),
            ("Renewable Energy & e-Mobility", ["Solar Power Systems", ("EV Chargers – AC", "Wall-mount, Delta"), ("EV Chargers – DC", "Fast chargers, Delta")]),
            ("Energy Management", ["Energy / Power Management Systems (EMS)"]),
        ],
    },
    {
        "id": "automation", "n": 3, "cls": "v3",
        "name": "Automation & Instrumentation",
        "short": "VFDs, servo drives, PLC, HMI, SCADA, robotics and field instruments, plus automatic dam-gate control.",
        "intro": "Drives, controllers and instruments that run the process, integrated into PLC / HMI / SCADA systems, including third-party equipment.",
        "subs": [
            ("Drives & Motion", [("Variable Frequency Drives", "VFD, incl. pump / fan control, Delta"), "Servo Motors", "Servo Drives", ("Actuator Motors", "For actuated valves / dampers")]),
            ("Control Systems", [("PLC", "Programmable logic controllers, Delta"), ("HMI", "Human–machine interface, Delta"), ("SMPS", "Switched-mode power supplies"), ("SCADA System", "Monitoring, alarms, trends & reports"), ("Plant & Machine Automation", "Incl. third-party integration"), "Industrial Robotics"]),
            ("Instrumentation", ["Sensors", "Water Sensors", "Pressure Transmitters", "Temperature Controllers", "Flow Meters", ("BOD / COD Analysers", "Water quality analysis")]),
            ("Special Automation Systems", [("Automatic Dam Gate Control System", "PLC / SCADA with VFD-driven gates")]),
        ],
    },
    {
        "id": "water", "n": 4, "cls": "v4",
        "name": "Water, Steam & Process Utilities",
        "short": "WTP, ETP, STP, RO, softening and filtration, steam distribution, PRV / PRS, condensate recovery, valves, SS piping and tanks.",
        "intro": "Treatment plants and process utilities that keep water, steam and compressed air moving reliably through the plant.",
        "subs": [
            ("Water & Wastewater Treatment", ["Water Treatment Plant (WTP)", "Effluent Treatment Plant (ETP)", "Sewage Treatment Plant (STP)", "RO Systems", "Softening Plants", "Filtration & Clarification Equipment", "Pumping Systems", "Water Conditioning Equipment"]),
            ("Steam Utilities", ["Steam Distribution Pipelines", ("PRV / PRS", "Pressure reducing valves / stations"), "Condensate Recovery Systems", "Steam Traps"]),
            ("Valves", ["Control Valves / Actuated Valves", "Butterfly Valves", "SS Valves"]),
            ("Piping, Tanks & Fabrication", ["SS Pipelines & Fittings", "SS Fabrication", "SS Tanks", "Compressed-Air Pipelines", ("Process Piping", "For water & process plants")]),
        ],
    },
    {
        "id": "chemicals", "n": 5, "cls": "v5",
        "name": "Process Chemicals & Hygiene",
        "short": "Cleaning, hygiene and CIP chemicals, water-treatment chemicals, conveyor lubrication, DE filter-aid powder and hygiene stations.",
        "intro": "Chemicals and hygiene equipment for food, beverage, brewery and process plants, supplied with application support.",
        "subs": [
            ("Cleaning & Process Chemicals", [("Cleaning & Hygiene Chemicals", "For industrial applications"), ("CIP Chemicals", "Clean-in-place"), "Water Treatment Chemicals", "Diatomaceous Earth (DE) – Filter Aid Powder"]),
            ("Lubrication & Hygiene Equipment", ["Conveyor Lubrication Chemicals", "Conveyor Lubrication Systems", "Hygiene Stations"]),
        ],
    },
    {
        "id": "building", "n": 6, "cls": "v6",
        "name": "Building & Infrastructure Solutions",
        "short": "BMS, basement ventilation, LED screens and video walls, pre-fab puff panel structures, plastic pallets and palletisers.",
        "intro": "Systems and structures for smart buildings, warehouses and plant infrastructure.",
        "subs": [
            ("Building Systems", [("Building Management System (BMS)", "Delta"), "Basement Ventilation", ("LED Screen / Video Wall", "Delta")]),
            ("Pre-Fab Structures & Material Handling", [("Pre-Fab Structures – Puff / FUF Panel", "Buildings, clean rooms, godowns, cold storage"), "Plastic Pallets", "Palletisers"]),
        ],
    },
]

for v in VERTICALS:
    v["count"] = sum(len(items) for _, items in v["subs"])
TOTAL_PRODUCTS = sum(v["count"] for v in VERTICALS)
TOTAL_SUBS = sum(len(v["subs"]) for v in VERTICALS)
assert TOTAL_PRODUCTS == 117 and TOTAL_SUBS == 27, (TOTAL_PRODUCTS, TOTAL_SUBS)

INDUSTRIES = ["Ayurvedic", "Breweries", "Cement", "Chemicals", "Distilleries", "Pharmaceuticals",
              "Hospital & Hospitality", "FMCG", "All Types of Government Projects", "Food & Beverages",
              "Nonwoven & Wovensac", "OEM", "Paper", "Plastics", "Steel", "Spinning",
              "Soft Drinks & Brewery", "Textiles", "Tobacco", "Sugar"]
assert len(INDUSTRIES) == 20

SERVICES = ["Engineering & technical solution design", "Equipment selection & supply", "System integration",
            "Installation", "Testing & commissioning", "Troubleshooting",
            "Preventive maintenance & O&M support", "After-sales service & plant improvement"]


# --------------------------------------------------------------------------
# Layout
# --------------------------------------------------------------------------
def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        links.append(f'<a href="{href}"{cur}>{label}</a>')
    links.append(f'<a class="btn" href="quote.html"{" aria-current=\"page\"" if active == "quote.html" else ""}>Request Quote</a>')
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<div class="topbar">
  <div class="wrap">
    <div class="topbar__group">
      <span class="topbar__countries">INDIA · NEPAL · BHUTAN</span>
      <span class="topbar__hide-sm">Patna · Delhi</span>
    </div>
    <div class="topbar__group">
      <a href="tel:+919899982418">+91 98999 82418</a>
      <a href="mailto:{INBOX}">{INBOX}</a>
      <span class="topbar__hide-sm">Mon – Sat: 9 AM – 7 PM</span>
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
    vlinks = "".join(f'<li><a href="products.html#{v["id"]}">{E(v["name"])}</a></li>' for v in VERTICALS)
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="logo-tile"><img src="assets/img/chemotech-logo.png" width="880" height="135" alt="Chemotech International" loading="lazy"></div>
        <p class="tagline">…a Clean and Conditioning company</p>
        <p>Integrated electrical, power, automation, water and process-utility solutions for industry and government projects since 2014–15.</p>
      </div>
      <div>
        <h4>Our products</h4>
        <ul>{vlinks}</ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul>
          <li><a href="about.html">About Us</a></li>
          <li><a href="company-profile.html">Company Profile</a></li>
          <li><a href="certifications.html">Certifications</a></li>
          <li><a href="contact.html">Contact</a></li>
          <li><a href="quote.html">Request Quote</a></li>
        </ul>
      </div>
      <div>
        <h4>Reach us</h4>
        <ul>
          <li><a href="tel:+919899982418">+91 98999 82418</a></li>
          <li><a href="tel:+919910680998">+91 99106 80998</a></li>
          <li><a href="tel:+918757446605">+91 87574 46605</a></li>
          <li><a href="tel:+919312282418">+91 93122 82418</a> <span class="muted">(Delhi)</span></li>
          <li><a href="mailto:{INBOX}">{INBOX}</a></li>
          <li>Mon – Sat: 9 AM – 7 PM</li>
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


def page(filename, title, description, body, active=None):
    active = active or filename
    full_title = "Chemotech International" if filename == "index.html" else f"{title} · Chemotech International"
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{full_title}</title>
<meta name="description" content="{E(description)}">
<meta name="theme-color" content="#000080">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{E(description)}">
<meta property="og:type" content="website">
<meta property="og:image" content="assets/img/chemotech-logo.png">
<link rel="icon" type="image/png" href="favicon.png">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="assets/js/main.js"></script>
</body>
</html>
"""
    with open(os.path.join(OUT, filename), "w") as f:
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
      <a class="btn btn--line-light" href="contact.html">Contact us</a>
    </div>
  </div>
</section>"""


# --------------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------------
HERO_SVG = """<svg viewBox="0 0 640 420" role="img" aria-labelledby="sch-t sch-d">
  <title id="sch-t">Plant scope schematic</title>
  <desc id="sch-d">A single-line diagram: HT incomer and transformer feed an LT panel, which powers a UPS for critical loads, a VFD driving a pump motor that feeds a water treatment plant, and EV chargers. Solar PV feeds the bus. A PLC and SCADA system supervises the drive and the treatment plant.</desc>
  <!-- HT incomer -->
  <text class="sch-label" x="78" y="34">HT INCOMER</text>
  <path class="sch-line" d="M60 18v66"/>
  <path class="sch-flow" d="M60 18v66"/>
  <!-- transformer -->
  <circle class="sch-box" cx="60" cy="100" r="17"/>
  <circle class="sch-box" cx="60" cy="124" r="17" style="fill:none"/>
  <text class="sch-label" x="88" y="116">TRANSFORMER</text>
  <path class="sch-line" d="M60 141v53"/>
  <path class="sch-flow" d="M60 141v53"/>
  <!-- breaker -->
  <rect class="sch-box" x="52" y="160" width="16" height="16"/>
  <!-- solar -->
  <path class="sch-box sch-box--green" d="M498 70h70l-14 34h-70z"/>
  <path d="M519 70l-14 34M540 70l-14 34M492 87h69" stroke="#9bbb59" stroke-width="1.5" fill="none"/>
  <text class="sch-label sch-label--green" x="488" y="58">SOLAR PV</text>
  <path class="sch-line" d="M526 104v90"/>
  <path class="sch-flow" d="M526 104v90"/>
  <!-- LT bus -->
  <text class="sch-label sch-label--in" x="86" y="186">LT / MCC PANEL · 415 V</text>
  <path class="sch-bus" d="M36 200h580"/>
  <!-- feeder 1: UPS -->
  <path class="sch-line" d="M120 200v52"/>
  <path class="sch-flow" d="M120 200v52"/>
  <rect class="sch-box" x="92" y="252" width="56" height="36"/>
  <text class="sch-label sch-label--in" x="104" y="275">UPS</text>
  <path class="sch-line" d="M120 288v40"/>
  <rect class="sch-box sch-box--green" x="84" y="328" width="72" height="28"/>
  <text class="sch-label" x="92" y="346" style="font-size:9px">CRITICAL</text>
  <!-- feeder 2: VFD + motor + pump -->
  <path class="sch-line" d="M250 200v44"/>
  <path class="sch-flow" d="M250 200v44"/>
  <rect class="sch-box" x="222" y="244" width="56" height="36"/>
  <text class="sch-label sch-label--in" x="236" y="267">VFD</text>
  <path class="sch-line" d="M250 280v34"/>
  <circle class="sch-box" cx="250" cy="334" r="20"/>
  <text class="sch-label sch-label--in" x="243" y="339">M</text>
  <path class="sch-line" d="M270 334h18"/>
  <circle class="sch-box sch-box--green" cx="306" cy="334" r="18"/>
  <path d="M297 324l20 10-20 10z" fill="#9bbb59"/>
  <text class="sch-label" x="286" y="372">PUMP</text>
  <!-- water pipe to WTP -->
  <path class="sch-pipe" d="M324 334h70"/>
  <path class="sch-flow sch-flow--water" d="M324 334h70"/>
  <rect class="sch-box sch-box--green" x="394" y="286" width="64" height="96" rx="14"/>
  <path d="M402 330h48" stroke="#9bbb59" stroke-width="1.5" stroke-dasharray="4 4"/>
  <text class="sch-label sch-label--in" x="409" y="316">WTP</text>
  <path class="sch-pipe" d="M458 360h150"/>
  <path class="sch-flow sch-flow--water" d="M458 360h150"/>
  <text class="sch-label sch-label--green" x="488" y="392">TREATED WATER</text>
  <!-- feeder 3: EV -->
  <path class="sch-line" d="M580 200v52"/>
  <path class="sch-flow" d="M580 200v52"/>
  <rect class="sch-box" x="556" y="252" width="48" height="36"/>
  <text class="sch-label sch-label--in" x="569" y="275">EV</text>
  <!-- control layer -->
  <rect class="sch-box" x="330" y="226" width="118" height="34" style="stroke:#b8a6e6"/>
  <text class="sch-label sch-label--in" x="340" y="248">PLC · SCADA</text>
  <circle class="sch-pulse" cx="436" cy="236" r="4"/>
  <path class="sch-ctrl" d="M330 252h-52"/>
  <path class="sch-ctrl" d="M426 260v26"/>
  <path class="sch-ctrl" d="M389 226V140h137"/>
  <text class="sch-label" x="334" y="132" style="fill:#b8a6e6">CONTROL · MONITORING</text>
</svg>"""


def home():
    facts = [("2014–15", "Established"), ("3", "Countries: India · Nepal · Bhutan"), ("20", "Industry sectors served"),
             ("6", "Business verticals"), (str(TOTAL_PRODUCTS), "Products &amp; systems"), ("2", "Electrical contractor licences")]
    facts_html = "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in facts)

    vpanels = "".join(f"""<a class="vpanel {v['cls']}" href="products.html#{v['id']}">
        <div class="vpanel__top"><span class="vcode">V{v['n']}</span><span class="vpanel__count">{len(v['subs'])} categories · {v['count']} products</span></div>
        {icon(v['id'])}
        <div class="stack" style="gap:10px"><h3>{E(v['name'])}</h3><p>{E(v['short'])}</p></div>
        <span class="text-link">View products {ARROW}</span>
      </a>""" for v in VERTICALS)

    steps = [("Study", "Understand the process requirement and operating conditions."),
             ("Engineer", "Develop the right technical solution and select the equipment."),
             ("Coordinate", "Align electrical, instrumentation, automation and process requirements."),
             ("Supply &amp; integrate", "Equipment, panels, instruments and associated systems."),
             ("Commission", "Support installation, testing and commissioning."),
             ("Support", "Troubleshooting, preventive maintenance and ongoing service.")]
    steps_html = "".join(f'<li><div class="node"><b>{i:02d}</b></div><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps, 1))

    inds = "".join(f'<li{" class=\"is-key\"" if "Government" in n else ""}><span>{i:02d}</span>{E(n)}</li>' for i, n in enumerate(INDUSTRIES, 1))

    gallery = [("delta-vfd", "Variable frequency drive"), ("delta-plc", "PLC"), ("delta-hmi", "HMI"),
               ("delta-ups", "Online UPS"), ("ev-charger-dc", "EV charger DC"), ("ev-charger-ac", "EV charger AC")]
    gal = "".join(f'<figure><div class="ph"><img src="assets/img/{f}.jpg" alt="Delta {c}" loading="lazy"></div><figcaption>{c}</figcaption></figure>' for f, c in gallery)

    body = f"""
<section class="hero on-navy">
  <div class="wrap">
    <div class="hero__copy">
      <p class="hero__tagline">…a Clean and Conditioning company</p>
      <h1>Power, automation and water systems, <em>engineered as one.</em></h1>
      <p>Chemotech International designs, supplies, integrates, commissions and maintains electrical, automation and process-utility systems for industry, infrastructure and government projects across India, Nepal and Bhutan.</p>
      <div class="btn-row">
        <a class="btn btn--green" href="quote.html">Request a quote {ARROW}</a>
        <a class="btn btn--line-light" href="products.html">Explore products</a>
      </div>
    </div>
    <figure class="hero__diagram" style="margin:0">
      {HERO_SVG}
      <figcaption class="hero__diagram-caption"><span><b>Fig. 1</b> · Typical plant scope</span><span>Power · Control · Water</span></figcaption>
    </figure>
  </div>
</section>

<section class="facts" aria-label="At a glance">
  <div class="wrap"><ul>{facts_html}</ul></div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">What we do</span>
        <h2>Six verticals. One accountable team.</h2>
        <p>Most plants need power, control and utilities to work together. We cover all three, so you deal with one team from equipment selection to after-sales service.</p>
      </div>
      <a class="btn btn--ghost" href="products.html">Full product list {ARROW}</a>
    </div>
    <div class="verticals">{vpanels}</div>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap partner">
    <div class="stack" style="gap:20px">
      <span class="tag">Business partner</span>
      <img class="partner__logo" src="assets/img/delta-logo.jpg" width="511" height="127" alt="Delta Electronics" loading="lazy">
      <h2 style="font-size:var(--fs-2xl)">The Delta range, supplied and supported locally</h2>
      <p class="muted">We are a business partner of Delta, the Taiwan-based manufacturer with a global turnover of about US$ 8 billion. We supply, programme and service the complete range: drives, PLCs, HMIs, robotics, online UPS, EV chargers, BMS / EMS and LED video walls.</p>
      <div class="partner__stats">
        <div><b>1 – 4000 kVA</b><span>Online UPS range</span></div>
        <div><b>~US$ 8 Bn</b><span>Delta global turnover</span></div>
        <div><b>AC &amp; DC</b><span>EV charging</span></div>
      </div>
    </div>
    <div class="gallery">{gal}</div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">How we work</span>
      <h2>From process study to plant support</h2>
      <p>Engineering, supply, system integration, installation, commissioning, maintenance and after-sales support, handled by the same team.</p>
    </div>
    <ol class="steps">{steps_html}</ol>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">Our presence</span>
        <h2>Industries we supply and serve</h2>
        <div class="presence"><span>India</span><span>Nepal</span><span>Bhutan</span></div>
      </div>
      <a class="text-link" href="company-profile.html#presence">Company profile {ARROW}</a>
    </div>
    <ul class="industries">{inds}</ul>
  </div>
</section>

<section class="section section--tight">
  <div class="wrap">
    <div class="section-head section-head--split" style="margin-bottom:28px">
      <div class="stack" style="gap:14px">
        <span class="tag">Licensed &amp; registered</span>
        <h2>Approved to execute in Bihar and Delhi</h2>
      </div>
      <a class="text-link" href="certifications.html">All certifications {ARROW}</a>
    </div>
    <ul class="licences">
      <li><small>Delhi</small><b>Electrical Contractor Licence</b><span>Govt. of NCT of Delhi · valid till 2050</span></li>
      <li><small>Bihar</small><b>Electrical Contractor Licence</b><span>Electrical Licensing Board, Patna · valid till 2030</span></li>
      <li><small>Bihar</small><b>BCD Class 3 Contractor</b><span>Building Construction Department · valid till 2031</span></li>
      <li><small>Business</small><b>MSME Udyam (Micro)</b><span>GST registered in Bihar &amp; Delhi</span></li>
    </ul>
  </div>
</section>
{cta()}"""
    page("index.html", "Home",
         "Chemotech International: electrical works, power backup, automation, SCADA, water treatment, process chemicals and building solutions for industry across India, Nepal and Bhutan. Delta business partner.",
         body)


# --------------------------------------------------------------------------
# ABOUT
# --------------------------------------------------------------------------
def about():
    chain = ["Concept Development", "Raw Material Purchase", "Production", "Management", "Direct Marketing"]
    chain_html = "".join(f"<li><small>Step {i}</small><b>{c}</b></li>" for i, c in enumerate(chain, 1))

    mission = ["Keep a work culture that drives results and engagement.", "Serve our customers' needs.",
               "Respect what our customers want.", "Provide solutions tailored to each customer's needs.",
               "Follow a customer-driven strategy that keeps improving satisfaction."]
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

    reasons = ["Single-point coordination across process, electrical and automation requirements.",
               "Practical engineering focused on reliability, maintainability and ease of operation.",
               "A wide product portfolio for industrial utilities and process applications.",
               "Integration of third-party equipment with PLC / HMI / SCADA based controls.",
               "Service-oriented support for commissioning, troubleshooting and plant improvement.",
               "Licensed electrical contractor in Bihar and Delhi; BCD Bihar Class 3 registered."]

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
      <p>We keep a professional and ethical work environment that encourages creativity and teamwork. Our experience lets us deliver cost-effective, well-directed and carefully thought-through work without compromising on quality.</p>
      <p>We combine a range of talents and services under one roof. As a relatively small group of professionals, we stay focused on our clients and can handle most of their needs. Specialising in core production services is how we deliver consistently high quality.</p>
      <p>We care about the quality of our work, and we believe that is why clients have trusted us with more challenging assignments over the years. Our consultative approach is guided by the client's objectives and has proven effective. Our best projects are collaborative: our team and the client listen closely to each other and arrive at practical, result-oriented solutions.</p>
      <p><strong>We stay steady under pressure and are strong enough to lead your vision.</strong> From concept development, raw material purchase and production to management and direct marketing, every stage is handled seamlessly.</p>
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
      <span class="tag">Vision for Chemotech group companies</span>
      <h2>Vision, mission &amp; values</h2>
    </div>
    <div class="vision"><h3>Our vision</h3><p>To serve every customer with a clear understanding of their work, which drives our passion for innovative power solutions.</p></div>
    <div class="split mt-lg">
      <div class="stack" style="gap:14px">
        <h3 style="font-size:var(--fs-xl)">Our mission</h3>
        <p class="muted">Consistently exceed customer satisfaction. To do this, we commit to:</p>
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
      <span class="tag">Chemotech group</span>
      <h2>What makes the group dependable</h2>
    </div>
    <ul class="strengths">
      <li><b>Team</b><div>An intelligent, devoted team of highly qualified, motivated and experienced professionals is the company's main strength.</div></li>
      <li><b>Design</b><div>We design the equipment to ensure a cost-effective solution.</div></li>
      <li><b>Execution</b><div>We execute turnkey projects in the shortest possible time with a fully professional approach, leaving clients satisfied.<div class="chips"><span>Quality-conscious approach</span><span>Safety, health &amp; environment conscious</span></div></div></li>
      <li><b>Repeat orders</b><div>Many satisfied clients come back to us for the same and other projects. The Chemotech team has earned their respect.</div></li>
    </ul>
    <div class="mt-lg">
      <h3 style="font-size:var(--fs-xl);margin-bottom:20px">Why work with us</h3>
      <ul class="reasons">{"".join(f"<li>{r}</li>" for r in reasons)}</ul>
    </div>
  </div>
</section>
{cta()}"""
    page("about.html", "About Us",
         "About Chemotech International: our story, vision, mission, values, quality policy and the team behind our electrical, automation and water projects.",
         body)


# --------------------------------------------------------------------------
# PRODUCTS
# --------------------------------------------------------------------------
def products():
    index = "".join(f'<a class="{v["cls"]}" href="#{v["id"]}"><span>V{v["n"]}</span>{E(v["name"])}</a>' for v in VERTICALS)

    sections = []
    for v in VERTICALS:
        subs = []
        for si, (sname, items) in enumerate(v["subs"], 1):
            lis = []
            for ii, it in enumerate(items, 1):
                name, note = (it if isinstance(it, tuple) else (it, ""))
                code = f'{v["n"]}.{si}.{ii}'
                lis.append(f'<li><code>{code}</code>{E(name)}{f" <small>{E(note)}</small>" if note else ""}</li>')
            subs.append(f'<div class="subcat"><h3><span>{v["n"]}.{si}</span>{E(sname)}</h3><ul class="items">{"".join(lis)}</ul></div>')
        sections.append(f"""<section class="vsection {v['cls']}" id="{v['id']}" aria-labelledby="{v['id']}-h">
      <header class="vhead"><span class="num">{v['n']:02d}</span><h2 id="{v['id']}-h">{E(v['name'])}</h2><span class="meta">{len(v['subs'])} categories · {v['count']} products</span></header>
      <p class="vintro">{E(v['intro'])}</p>
      {''.join(subs)}
    </section>""")

    show = [
        ("show--wide", "v3", "scada-tata-steel", "", "Automation · SCADA", "SCADA system", "Centralised monitoring, alarms, trends and reporting. Shown: bentonite slurry preparation and dosing plant SCADA for Tata Steel."),
        ("", "v4", None, "duo", "Water treatment", "Complete water treatment for industries", "Filtration, softening and conditioning plants designed and commissioned for process and utility water."),
        ("show--half", "v3", "dam-gate-control", "contain", "Special automation", "Automatic dam gate control", "Master and backup PLCs, fibre-optic ring, VFD-driven gates, water level sensors and SCADA with email / SMS alerts."),
        ("show--half", "v6", "delta-bms", "contain", "Building systems · Delta", "Building management solution", "Energy management, HVAC control, connected lighting, surveillance, access control and EV charging for smart buildings."),
        ("", "v2", "delta-ups", "contain", "Power backup · Delta", "Uninterrupted power supply", "Online UPS systems from 1 kVA to 4000 kVA with lithium-ion or VRLA batteries."),
        ("", "v2", "servo-stabilizer", "contain", "Voltage regulation", "Servo voltage stabiliser", "Stable supply voltage for sensitive machines and plant loads."),
        ("", "v2", None, "ev", "e-Mobility · Delta", "EV chargers, AC &amp; DC", "Wall-mount AC chargers and DC fast chargers for fleets, campuses and public sites."),
        ("show--half", "v6", "fuf-panel", "", "Pre-fab structures", "Puff / FUF panel structures", "Buildings, clean rooms, godowns and cold storage, delivered quickly."),
        ("show--half", "v6", "video-wall", "", "Building systems · Delta", "LED screen / video wall", "Large-format LED displays for control rooms, lobbies and public spaces."),
    ]
    cards = []
    for size, cls, img, mode, small, title, text in show:
        if mode == "duo":
            media = '<div class="media duo"><img src="assets/img/wtp-filtration.jpg" alt="Industrial pressure sand filters" loading="lazy"><img src="assets/img/wtp-softener.jpg" alt="FRP softener vessels" loading="lazy"></div>'
        elif mode == "ev":
            media = '<div class="media duo contain"><img src="assets/img/ev-charger-dc.jpg" alt="Delta DC fast charger" loading="lazy" style="object-fit:contain;padding:10px"><img src="assets/img/ev-charger-ac.jpg" alt="Delta AC wall charger" loading="lazy" style="object-fit:contain;padding:10px"></div>'
        else:
            media = f'<div class="media {mode}"><img src="assets/img/{img}.jpg" alt="{title}" loading="lazy"></div>'
        cards.append(f'<article class="show {size} {cls}">{media}<div class="body"><small>{small}</small><h3>{title}</h3><p>{text}</p></div></article>')

    services = "".join(f"<li><span>{i:02d}</span>{E(s)}</li>" for i, s in enumerate(SERVICES, 1))

    body = f"""
{page_hero("Our Products", "Every product and system we supply, install and service", f"{TOTAL_PRODUCTS} products in {TOTAL_SUBS} categories, organised into six business verticals. Each carries a reference code you can quote in your enquiry.", "Product catalogue")}

<section class="section">
  <div class="wrap catalogue">
    <aside class="cat-index" aria-label="Product verticals">
      <div class="search">
        <label for="product-search">Find a product</label>
        <input id="product-search" type="search" placeholder="e.g. VFD, STP, earthing" autocomplete="off">
        <output id="search-count" for="product-search" aria-live="polite"></output>
      </div>
      <nav>{index}</nav>
      <a class="btn" href="quote.html">Request a quote {ARROW}</a>
    </aside>
    <div style="min-width:0">
      {''.join(sections)}
      <p class="no-results" id="no-results" hidden>No products match that search. Try a shorter term, or <a href="contact.html">ask us directly</a>: we also source items outside this list.</p>
    </div>
  </div>
</section>

<section class="section on-navy" style="background:var(--navy)">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Included with every vertical</span>
      <h2 style="color:var(--on-navy)">Services we provide with each product</h2>
    </div>
    <ol class="services">{services}</ol>
  </div>
</section>

<section class="section section--wash" id="solutions">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Our solutions &amp; business partners</span>
      <h2>Featured solutions</h2>
      <p>A selection of systems we have engineered, supplied and commissioned, including the Delta range we represent.</p>
    </div>
    <div class="showcase">{''.join(cards)}</div>
  </div>
</section>
{cta()}"""
    page("products.html", "Our Products",
         f"Chemotech International product catalogue: {TOTAL_PRODUCTS} products across electrical works, power backup, automation & SCADA, water & steam utilities, process chemicals and building solutions.",
         body)


# --------------------------------------------------------------------------
# COMPANY PROFILE
# --------------------------------------------------------------------------
def office_cards():
    return f"""<div class="offices">
      <article class="office">
        <span class="tag">Head office · Bihar</span>
        <h3>Patna</h3>
        <address>Pratiksha Bhawan, Maurya Vihar Colony,<br>Near Bihar Urology Centre, Transport Nagar,<br>Patna, Bihar – 800026</address>
        <dl>
          <dt>Phone</dt><dd><a href="tel:+919899982418">+91 98999 82418</a><br><a href="tel:+919910680998">+91 99106 80998</a><br><a href="tel:+918757446605">+91 87574 46605</a></dd>
          <dt>Email</dt><dd><a href="mailto:{PATNA_MAIL}">{PATNA_MAIL}</a></dd>
        </dl>
        <div class="gstin">GSTIN<span>10AATFC8340G1ZJ</span></div>
      </article>
      <article class="office">
        <span class="tag">Branch office · Delhi</span>
        <h3>Delhi</h3>
        <address>Maya Garden, Ground Floor, Kh. No. 44/18 &amp; 44/19,<br>Gate No. 02, Inderprastha (IP) Colony, Block-C,<br>Village Burari, North Delhi – 110084</address>
        <dl>
          <dt>Phone</dt><dd><a href="tel:+919312282418">+91 93122 82418</a></dd>
          <dt>Email</dt><dd><a href="mailto:{DELHI_MAIL}">{DELHI_MAIL}</a></dd>
        </dl>
        <div class="gstin">GSTIN<span>07AATFC8340G1Z6</span></div>
      </article>
    </div>"""


def company_profile():
    inds = "".join(f'<li{" class=\"is-key\"" if "Government" in n else ""}><span>{i:02d}</span>{E(n)}</li>' for i, n in enumerate(INDUSTRIES, 1))
    cap_rows = "".join(
        f'<tr><th scope="row"><a href="products.html#{v["id"]}" style="color:inherit">{E(v["name"])}</a></th><td>{" · ".join(E(s) for s, _ in v["subs"])}</td><td class="mono">{v["count"]}</td></tr>'
        for v in VERTICALS)

    body = f"""
{page_hero("Company Profile", "Chemotech International at a glance", "Key facts, offices, registrations and the industries we serve. Download the full profiles for your vendor file.", "Company profile")}

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
          <tr><th scope="row">Phone</th><td><b>Patna:</b> +91 98999 82418 · 99106 80998 · 87574 46605<br><b>Delhi:</b> +91 93122 82418</td></tr>
          <tr><th scope="row">Email</th><td style="overflow-wrap:anywhere">{INBOX}<br>{PATNA_MAIL}<br>{DELHI_MAIL}</td></tr>
          <tr><th scope="row">Auditor</th><td>Mr. Ajit Choudhary, CA</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Offices &amp; GST registrations</span>
      <h2>Where to find us</h2>
    </div>
    {office_cards()}
  </div>
</section>

<section class="section" id="presence">
  <div class="wrap">
    <div class="section-head section-head--split">
      <div class="stack" style="gap:14px">
        <span class="tag">Our presence</span>
        <h2>We supply and serve these industries</h2>
        <div class="presence"><span>India</span><span>Nepal</span><span>Bhutan</span></div>
      </div>
    </div>
    <ul class="industries">{inds}</ul>
  </div>
</section>

<section class="section section--wash">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Capabilities at a glance</span>
      <h2>Six verticals, {TOTAL_SUBS} categories, {TOTAL_PRODUCTS} products</h2>
    </div>
    <div class="table-wrap">
      <table class="data">
        <thead><tr><th scope="col">Work area</th><th scope="col">Key solutions</th><th scope="col">Products</th></tr></thead>
        <tbody>{cap_rows}</tbody>
      </table>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="tag">Downloads</span>
      <h2>Company documents</h2>
      <p>PDF copies for procurement and vendor registration.</p>
    </div>
    <div class="downloads">
      <a class="download" href="assets/docs/Chemotech-International-Company-Profile.pdf" target="_blank" rel="noopener">
        <span class="doc">PDF</span><span><b>Company Profile</b><span>18 pages · licences, team, products, solutions</span></span><span class="arrow">&darr;</span>
      </a>
      <a class="download" href="assets/docs/Chemotech-International-Work-Profile.pdf" target="_blank" rel="noopener">
        <span class="doc">PDF</span><span><b>Work Profile</b><span>4 pages · core work, detailed scope, registrations</span></span><span class="arrow">&darr;</span>
      </a>
    </div>
  </div>
</section>
{cta()}"""
    page("company-profile.html", "Company Profile",
         "Chemotech International company profile: key information, offices in Patna and Delhi, GST registrations, industries served across India, Nepal and Bhutan, and downloadable profiles.",
         body)


# --------------------------------------------------------------------------
# CERTIFICATIONS
# --------------------------------------------------------------------------
def certifications():
    body = f"""
{page_hero("Certifications", "Licensed electrical contractor in Bihar and Delhi", "Government licences and registrations that let us execute electrical and building works directly, with valid GST registrations in both states.", "Licences &amp; registrations")}

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
          <dt>Valid</dt><dd><div class="validity"><span>16/06/2025 – 15/06/2050</span></div></dd>
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
      <span class="tag">Contractor registration</span>
      <h2>Building Construction Department, Bihar</h2>
    </div>
    <div class="reg-banner" style="background:var(--paper)">
      <div><h3>Building Construction Department, Govt. of Bihar</h3><p>Registration No. <b>3260569</b> · Valid 08/07/2026 – 07/07/2031</p></div>
      <span class="class">Class 3</span>
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
         "Chemotech International licences and registrations: Delhi and Bihar electrical contractor licences, BCD Bihar Class 3, GST, PAN, Udyam MSME and firm registration.",
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
{page_hero("Contact", "Talk to our engineers", "Reach our head office in Patna or our Delhi office. We reply to enquiries on working days, Monday to Saturday, 9 AM to 7 PM.", "Contact us")}

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
        <button class="btn" type="submit">Send message {ARROW}</button>
        <small>Opens your email app with the message filled in, addressed to {INBOX}.</small>
      </div>
    </form>
    <aside class="aside">
      <div class="aside-card">
        <h3>General enquiries</h3>
        <a class="big-phone" href="tel:+919899982418">+91 98999 82418</a>
        <a href="mailto:{INBOX}">{INBOX}</a>
        <p>Mon – Sat: 9 AM – 7 PM</p>
      </div>
      <div class="aside-card">
        <h3>Need a price?</h3>
        <p>Use the quote form to share your scope, quantities and site location. It helps us respond faster with the right technical offer.</p>
        <a class="btn btn--ghost" href="quote.html" style="justify-self:start">Request a quote {ARROW}</a>
      </div>
    </aside>
  </div>
</section>"""
    page("contact.html", "Contact",
         "Contact Chemotech International: head office in Patna, Bihar and branch office in Burari, Delhi. Phone +91 98999 82418, info.chemotechinternational@gmail.com.",
         body)


def quote():
    checks = "".join(f'<label><input type="checkbox" name="vertical" value="{E(v["name"])}">{E(v["name"])}</label>' for v in VERTICALS)
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
      <fieldset class="checks-wrap" data-label="Verticals">
        <legend>2 · What do you need?</legend>
        <div class="checks">{checks}</div>
      </fieldset>
      <fieldset>
        <legend>3 · Scope</legend>
        {field("requirement", "Products or systems required", "textarea", required=True, msg="Please describe what you need.", attrs='placeholder="e.g. 2 × 200 kVA online UPS with 30 min backup; 5 HP VFD panels for pumps; 50 KLD STP"', full_label="Requirement")}
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
          {field("ref", "Product codes", opt=True, attrs='placeholder="e.g. 2.1.1, 3.1.1"', full_label="Product codes")}
        </div>
      </fieldset>
      {status_box()}
      <div class="form-foot">
        <button class="btn" type="submit">Send quote request {ARROW}</button>
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
        <h3>Find product codes</h3>
        <p>Every item in our <a href="products.html">product catalogue</a> has a reference code, such as 3.1.1 for variable frequency drives.</p>
      </div>
    </aside>
  </div>
</section>"""
    page("quote.html", "Request Quote",
         "Request a quotation from Chemotech International for electrical panels, UPS, VFD, PLC, SCADA, water treatment plants, process chemicals and building systems.",
         body)


home(); about(); products(); company_profile(); certifications(); contact(); quote()
print("built", TOTAL_PRODUCTS, "products,", TOTAL_SUBS, "sub-categories")
