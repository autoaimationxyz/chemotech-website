# Content audit — latest supplied profiles

Reference material: latest uploaded Company Profile (DOCX and PDF), Work Profile (DOCX and PDF), and Product Master List (DOCX). This is a source comparison, not independent verification of legal registrations or third-party commercial relationships.

- Product descriptions and all 328 variants/make lists match the latest 56-product master. Four source em dashes represent unnamed variants and remain empty strings in the data, displayed using the product family name.
- All 44 named partner makes match the latest profile. Removed the unsupported Delta revenue/turnover figure and revised the Delta feature into a broader technology ecosystem.
- Industries now match the 23 named sectors in the profile, removing the separately duplicated brewery category. Counts use the data rather than hardcoded totals.
- Company type, partners, establishment period, locations, phone numbers, emails, PAN, GSTINs, licences, contractor registrations, MSME and firm registration details were compared against the profiles. GSTINs match exactly: Bihar 10AATFC8340G1ZJ; Delhi 07AATFC8340G1Z6.
- Replaced obsolete company/group/production descriptions with requirement/design, sourcing/supply, installation, commissioning and service/AMC. Removed business hours absent from the latest profiles.
- Public Company Profile and Work Profile PDF files and download links removed as requested. The HTML company/credentials page remains.
- Office cards use equal-height layouts with aligned GST rows; registration identifiers use consistent numeric typography and controlled wrapping.
- Solution images are described as equipment/solution imagery rather than claiming every manufacturer image is a completed Chemotech project.

## Outstanding external access

The environment returns an HTTP proxy 403 for the supplied live site at web.schoolerp.org and for Wikimedia Commons image sourcing. The required hostnames are saved in the environment draft, preserving the package-manager presets:

- web.schoolerp.org
- commons.wikimedia.org
- upload.wikimedia.org

The draft save does not apply live network access. Internet photo selection, licence/attribution records, and live-site comparison remain unfinished until the user saves/publishes the environment configuration. Do not claim every product has an internet-sourced photograph; products without supplied photography still use explicitly labelled conceptual illustrations.

## Further repetition and detail audit

- Detailed office addresses and contact lists now live on Contact; Company links directly to each office instead of repeating the complete cards and phone/email rows.
- Company no longer repeats the entire 56-product inventory. It links to the catalogue; clients, industries and named partner makes remain on Company.
- About consolidates repeated company/strength statements and mission commitments. The workflow, people, quality policy and distinct working principles remain.
- Haryana contractor registration appears once on Certifications, in the contractor section.
- Product support is described as available according to agreed scope, rather than automatically included with every supply.
- Product cards and detail dialogs consistently use “Add to enquiry”. Form actions say “Prepare message” / “Prepare quote email” to describe the existing email-app behavior accurately.
- `missing-photos.csv` identifies the 34 families without supplied photographs. Wikimedia requests still return a proxy 403 through both standard and elevated execution. No unrelated photos have been substituted for those products.
