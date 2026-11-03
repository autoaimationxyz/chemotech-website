# Chemotech International — website

Static website for Chemotech International (…a Clean and Conditioning company).
Plain HTML, CSS and JavaScript: no framework needed to host it.
Upload the folder contents to any web host.

## Pages

| File | Page |
|---|---|
| `index.html` | Home: verticals, solution photos, Delta partnership, clients, industries, licences |
| `about.html` | About Us: story, vision, mission, values, quality policy, team |
| `products.html` | Our Products: interactive catalogue of 56 products / 328 variants / 150+ makes, solutions gallery |
| `company-profile.html` | Company Profile: key information, offices, clients & projects, partners, industries, downloads |
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
assets/css/style.css        design system (brand colours, one Helvetica/sans-serif stack)
assets/js/main.js           mobile menu, forms, quote pre-fill
assets/js/catalogue.js      product catalogue, product panel, enquiry list, photo lightbox
assets/img/                 logo, emblem, product photos
assets/img/solutions/       30 solution photos from the 2026 company profile
assets/docs/                downloadable Company Profile and Work Profile PDFs
tools/build.py              generator for all pages (copy, clients, partners, contact details)
tools/products.json         product data (generated from the Product Master List)
tools/solutions.json        solution photos: captions, makes, linked product numbers
tools/parse_master_list.py  converts the Product Master List PDF into tools/products.json
```

## Editing

Pages are generated. Edit the sources, then run:

```
python3 tools/build.py .
```

- **Products** — update the Product Master List PDF, then:
  ```
  pdftotext -layout Chemotech_Product_Master_List.pdf master.txt
  python3 tools/parse_master_list.py master.txt tools/products.json
  python3 tools/build.py .
  ```
- **Photos** — add the image to `assets/img/solutions/` and an entry to `tools/solutions.json`
  (`products` lists the product numbers it belongs to).
- **Hide per-variant makes** — set `SHOW_VARIANT_MAKES = False` in `tools/build.py`.

Edits made directly in the HTML files are overwritten the next time the generator runs.

## Forms

The Contact and Request Quote forms open the visitor's email app with a pre-filled
message to `info.chemotechinternational@gmail.com` (set in `assets/js/main.js`).
