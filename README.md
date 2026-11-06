# Chemotech International — website

Static website for Chemotech International (…a Clean and Conditioning company).
Plain HTML, CSS and JavaScript: no framework needed to host it.
Upload the folder contents to any web host.

## Pages

| File | Page |
|---|---|
| `index.html` | Home: animated engineering ecosystem, compact capabilities, selected products and links to company details |
| `about.html` | About Us: story, vision, mission, values, quality policy, team |
| `products.html` | Our Products: interactive catalogue of 56 products / 332 variants / make filters, solutions gallery |
| `company-profile.html` | Company Profile: key information, offices, clients & projects, partners and industries |
| `certifications.html` | Licences & registrations (Delhi, Bihar, BCD Class 3, Haryana, GST, MSME) |
| `contact.html` | Contact: both offices + message form |
| `quote.html` | Request Quote form (pre-filled with products picked in the catalogue) |

## Product catalogue

- Filter by the 8 categories or by make, and search across product names, variants and makes.
- Each product opens a detail panel with photos, every variant / type and the makes supplied.
- "Add to enquiry" collects products in the visitor's browser; the quote form lists them.
- Direct links: `products.html#cat-wp` opens a category, `products.html#p-27` opens a product.
- Category codes: `pd` Power Distribution, `sw` Switchgear & Controls, `cl` Cabling, Lighting & Safety,
  `pb` Power Backup & Energy, `au` Automation & Instrumentation, `wp` Water & Process,
  `bi` Building & ICT, `sv` Services.

## Structure

```
assets/css/style.css        base layout and component styles
assets/css/modern.css       shared responsive theme, product cards, animations
assets/js/main.js           mobile menu, forms, quote pre-fill
assets/js/catalogue.js      product catalogue, product panel, enquiry list, photo lightbox
assets/img/                 logo, emblem, product photos
assets/img/solutions/       36 solution photos from the 2026 company profile
tools/company.json          verified industries and partner makes from the latest profiles
tools/system-graphic.html   interactive, animated engineering ecosystem
assets/css/immersive.css    shared layouts, animation and alignment refinements
assets/css/profile.css      active light theme from the updated profile palette
tools/build.py              generator for all pages (copy, clients, partners, contact details)
tools/products.json         product data (generated from the Product Master List)
tools/solutions.json        solution photos: captions, makes, linked product numbers
tools/import_products_docx.py  imports master-list tables and preserves stable website IDs
tools/parse_master_list.py  legacy PDF text extractor; do not overwrite stable IDs with its raw output
```

## Editing

Pages are generated. Edit the sources, then run:

```
python3 tools/build.py .
```

- **Products** — import the latest DOCX master list, then rebuild:
  ```sh
  python3 tools/import_products_docx.py /path/to/Chemotech_Product_Master_List.docx
  python3 tools/build.py .
  ```
  Use `--check` to verify a supplied document without changing JSON. `no` is the stable website ID used by images, deep links and saved enquiries; `catalogue_no` is the current profile's display number. Do not renumber stable IDs. The former DG Service family (`p-10`) redirects to Diesel Generator Sets (`p-9`), which now includes those services. Flow/Level/Pressure retains `p-38`; the new Water Quality Analysers family uses `p-57` and displays as product 38.
- **Photos** — add the image to `assets/img/solutions/` and an entry to `tools/solutions.json`
  (`products` lists the stable website IDs it belongs to).
- **Hide per-variant makes** — set `SHOW_VARIANT_MAKES = False` in `tools/build.py`.

Edits made directly in the HTML files are overwritten the next time the generator runs.

## Forms

The Contact and Request Quote forms open the visitor's email app with a pre-filled
message to `info.chemotechinternational@gmail.com` (set in `assets/js/main.js`).

## Redesigned product experience

- The homepage features an interactive animated industrial ecosystem, selected technology makes and product discovery. Pause controls and reduced-motion support are included.
- All 56 families retain their descriptions, 332 variants, makes, filtering and enquiry workflow.
- Cards preview available options. Product dialogs add specification summaries and application guidance.
- Specifications are maintained in `SPECIFICATIONS` in `tools/build.py`; model-specific ratings must be confirmed with the engineering team. Do not invent missing ratings.
- All 56 product families currently have photographs. The 34 added Wikimedia images are representative equipment photos; their source and licence links appear in product details. Credits are maintained in `assets/img/products/CREDITS.md`. A labelled illustration remains as a fallback for future families without photography.
- `assets/css/profile.css` applies the updated light palette across all seven pages: white/lavender backgrounds, royal navy `#00008B`, purple `#422772` and leaf green `#9BBB59`. The animated system model uses the same palette.
- The 6 November profiles confirm 23 sectors, 51 named OEM partners, 33 clients, 56 product families and 332 variants. Company/project references, instrumentation, OEM makes, branch contacts and team-experience figures follow those profiles.
- Profile PDFs and their public download links were removed. Office GST rows align at the bottom of equal-height cards.
- The newly supplied photographs are included and checked locally. Independent verification of the live site and external photo-source metadata remains blocked by this environment’s network policy.
- The homepage includes a compact three-stage delivery preview; detailed clients and licences stay on their own pages.
- Bullets, step numbers and text use explicit columns for consistent wrapping and alignment.

## Local preview and checks

No application dependencies or build framework are required:

```sh
python3 tools/build.py .
python3 -m http.server 8080
```

Optional browser regression checks require Playwright and its Chromium browser. Install test tools outside the checkout to keep the static site dependency-free:

```sh
npm install --prefix /tmp/chemotech-checks playwright
/tmp/chemotech-checks/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/chemotech-checks/node_modules node tools/browser-check.cjs
```

Keep the local server running in another terminal. `SITE_URL` can override the default test server address. Checks cover all seven pages at 320, 390, 768, 1024, 1440 and 1920 pixels, catalogue filters, enquiries, product deep links, mobile navigation, dialogs and reduced motion. These checks use Chromium; physical iOS/Android devices and Safari are separate compatibility checks.

## GitHub Pages hosting

The latest website is on `website-redesign`. In repository Settings → Pages, select **Deploy from a branch**, then **website-redesign** and **/ (root)**, and save. The `.nojekyll` file ensures the generated HTML and assets are served directly. A public repository can use GitHub Pages on GitHub Free.

No custom domain or DNS changes are required for the GitHub-provided address. Publishing Pages makes the website publicly accessible. This does not replace the existing schoolerp.org website.
