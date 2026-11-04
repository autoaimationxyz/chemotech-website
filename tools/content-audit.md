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

## External verification limits

The environment returns an HTTP proxy 403 for the supplied live site at web.schoolerp.org and for Wikimedia Commons image sourcing. The required hostnames are saved in the environment draft, preserving the package-manager presets:

- web.schoolerp.org
- commons.wikimedia.org
- upload.wikimedia.org

The draft save does not apply live network access. The user subsequently supplied 34 representative Wikimedia photographs with credit records, covering every product family. These local files and source links are checked; independent verification of the live site and source metadata remains blocked. Three supplied credit records use the generic author label “Wikimedia Commons contributor” and still need confirmation from the original source pages.

## Further repetition and detail audit

- Detailed office addresses and contact lists now live on Contact; Company links directly to each office instead of repeating the complete cards and phone/email rows.
- Company no longer repeats the entire 56-product inventory. It links to the catalogue; clients, industries and named partner makes remain on Company.
- About consolidates repeated company/strength statements and mission commitments. The workflow, people, quality policy and distinct working principles remain.
- Haryana contractor registration appears once on Certifications, in the contractor section.
- Product support is described as available according to agreed scope, rather than automatically included with every supply.
- Product cards and detail dialogs consistently use “Add to enquiry”. Form actions say “Prepare message” / “Prepare quote email” to describe the existing email-app behavior accurately.
- `missing-photos.csv` now records the 34 supplied representative photo additions; no product family is missing a photograph.

## Homepage expansion, image and alignment review

- Fast-forwarded to the user’s photo commit `4f1c8ba`, preserving all 34 image binaries and existing credit records.
- Every image file decodes, all 56 catalogue families have images, and the 34 added image records link to their recorded Commons source. Licence links are exposed where the supplied record includes one. Images describe product types rather than promising the displayed brand/model.
- Added a three-stage delivery preview to Home, increasing rendered page length by approximately 20% while keeping detailed client/registration lists on their dedicated pages.
- About mission/reason bullets, quality-policy numbers, workflow labels, product service numbers, industry numbers and quote-process text use explicit marker/text columns aligned to the first line.
- Fixed singular variant labels (“1 type”). Updated stale documentation that still claimed 34 product photos were missing.
