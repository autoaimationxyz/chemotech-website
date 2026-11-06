# Chemotech International — website

Static website for Chemotech International (…a Clean and Conditioning company).
Plain HTML, CSS and JavaScript: no framework needed to host it.
Upload the folder contents to any web host.

## Pages

| File | Page |
|---|---|
| `index.html` | Home: animated engineering ecosystem, compact capabilities, selected products and links to company details |
| `about.html` | About: story, people, commitments and company facts |
| `solutions.html` | Solutions & Services: engineering disciplines, application imagery, delivery and OEMs |
| `products.html` | Products: searchable catalogue of 56 families / 332 variants, with progressive results |
| `projects.html` | Projects & Clients: recorded references, locations, capacities and industries |
| `company-profile.html` | Legacy redirect to the new page structure |
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
assets/js/catalogue.js      product catalogue, progressive results, product panel and enquiry list
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
message to the primary email in `tools/company.json` (`contacts.primary_email`). The copy option prepares the same enquiry for pasting into any email service; if clipboard access is unavailable, a selectable draft is shown.

## Redesigned product experience

- The homepage features an interactive animated industrial ecosystem, selected technology makes and product discovery. Pause controls and reduced-motion support are included.
- All 56 families retain their descriptions, 332 variants, makes, filtering and enquiry workflow.
- Cards preview available options. Product dialogs add specification summaries and application guidance.
- Specifications are maintained in `SPECIFICATIONS` in `tools/build.py`; model-specific ratings must be confirmed with the engineering team. Do not invent missing ratings.
- All 56 product families currently have photographs. The 34 added Wikimedia images are representative equipment photos; their source and licence links appear in product details. Credits are maintained in `assets/img/products/CREDITS.md`. A labelled illustration remains as a fallback for future families without photography.
- `assets/css/profile.css` applies the updated light palette across all eight pages: white/lavender backgrounds, royal navy `#00008B`, purple `#422772` and leaf green `#9BBB59`. The animated system model uses the same palette.
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
NODE_PATH=/tmp/chemotech-checks/node_modules node tools/journey-check.cjs
```

Keep the local server running in another terminal. `SITE_URL` can override the default test server address. Checks cover all eight pages at 320, 390, 768, 1024, 1440 and 1920 pixels, catalogue filters, enquiries, product deep links, mobile navigation, dialogs and reduced motion. These checks use Chromium; physical iOS/Android devices and Safari are separate compatibility checks.

## GitHub Pages hosting

The source branch is `website-redesign`; the live GitHub Pages site is published from `gh-pages`. Publish the same commit to both branches with `git push --atomic origin HEAD:refs/heads/website-redesign HEAD:refs/heads/gh-pages`. The `.nojekyll` file ensures the generated HTML and assets are served directly. A public repository can use GitHub Pages on GitHub Free.

No custom domain or DNS changes are required for the GitHub-provided address. Publishing Pages makes the website publicly accessible. This does not replace the existing schoolerp.org website.

## Readability and final usability refinements

The active type scale uses native system fonts, 17px base copy, 16–18px main reading text, 15px navigation, 14px actions and 12–14px supporting labels. Sizes use rem units to follow browser font preferences. Form fields remain at least 16px. Compact layouts use a scrollable mobile menu, larger graphic controls and a dynamically measured catalogue-toolbar offset. Bullet/number rows have inset padding and explicit text columns.

Contact details are centralised in `tools/company.json`. The user selected the Company Profile PDF as the final reference for both offices and the footer. Phone order: 98999 82418, 87574 46605, 99106 80998, 93122 82418. Email order: chemotech.international@gmail.com, info.chemotechinternational@gmail.com, tapan.chemotech@gmail.com.

Workflow and office pictograms, viewport reveals and a short process-line animation provide visual guidance. Reduced-motion preferences disable animation. The email forms do not submit to a server; users must send the prepared/copied draft from their own email service.


## Page structure and visitor journeys

- `index.html`: capability overview, selected systems and concise evidence.
- `solutions.html`: four engineering disciplines, relevant equipment/application images, delivery process, service scope and complete OEM list.
- `products.html`: compact searchable catalogue. The first 12 cards are shown initially, with 12 more per activation; filtering always searches all 56 families and 332 variants. Without JavaScript all cards remain available.
- `projects.html`: recorded project references (locations/capacities), clients and industries. Equipment/application imagery is not presented as project photography.
- `about.html`: company background, people, concise commitments and legal company facts.
- `certifications.html`: Licences & Registrations; a supporting page linked from About, Solutions and the footer.
- `contact.html`: office contacts/maps and short general enquiry, with jump links.
- `quote.html`: selected products, project scope and quotation enquiry.

`company-profile.html` redirects to Projects, retaining client/presence anchors and routing the old OEM anchor to Solutions. Product IDs, category links, legacy DG redirects and saved enquiry migration are preserved. The former product-gallery anchor routes to Solutions. Contact and quote forms clearly require the visitor to send the prepared/copied email; no submission backend or third-party form endpoint is configured.


## Post-restructure interaction refinements

Catalogue searches and make filters are encoded in `q` and `make` URL parameters; categories retain the existing hash links. Shared/reloaded filtered product links restore the controls. Reset clears the filter parameters. Invalid make values fall back to the complete make list.

Enquiry selections update across tabs and when returning through the browser's page cache. Removing a selected product returns keyboard focus to the next removal action or the catalogue link, announces the change and hides an outdated prepared draft. Mobile menus dismiss on outside clicks and reset when switching to desktop layout. `tools/journey-check.cjs` covers these interactions.
