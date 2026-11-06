# Profile/content audit — 6 November 2026

Sources: the newly uploaded Company Profile (DOCX/PDF), Work Profile (DOCX) and Product Master List (DOCX). Source comparison does not independently establish legal registration status or commercial relationships.

## Brand and presentation

The palette is taken directly from document colour records and checked against the rendered company-profile cover: royal navy `#00008B`, purple `#422772`, leaf green `#9BBB59`, green ink `#5E7A2A`, white and pale lavender `#F3F1F8`. Main page surfaces are white/lavender; navy is used for headings, primary controls and the footer. `profile.css` is the active colour layer over the retained responsive layouts. The supplied higher-resolution logo and the animated system model follow the updated palette.

Existing thin SVG arrows, responsive 3:2 product-image frames, first-line bullet/number alignment, email-only top bar, reduced-motion controls and the expanded homepage delivery preview are retained. PDF downloads remain removed. Banking details in the source profiles are not added to public pages.

## Current source data

- 56 product families / 332 variants, compared field-by-field with the DOCX master tables, including descriptions, main makes and per-variant makes.
- 51 named OEM partners, 33 named clients and 23 sectors from the latest company profile.
- Current project groups: Automation/SCADA/WTP instrumentation, Industrial RO/WTP plants, Sugar mills and Dairy ETP plants. Their names, locations and capacities follow the new profile.
- Team experience updated exactly as supplied: Raman 34+, Tapan 29+, Shailendra 19+ (14 years in sales/marketing), Mukund 8+; supporting team 21 / 8 / 8 / 5 years.
- Both office phone lists follow the Company Profile PDF, as selected by the user. General company contacts, addresses, GST, PAN and contractor registrations were compared with the sources. Tax dates are labelled “Registered on”.
- Product maker updates include SBEM, Toshcon, KEC International, Plaza Wires, Recon and the expanded supplier lists. The OEM section includes the latest additions and removes the previous partner-list entry absent from the latest list.

## Product identity and compatibility

Document numbers changed. Stable website IDs are retained by product identity, while `catalogue_no` carries the new display order. This preserves existing product-image mappings, links and saved selections. Diesel generator service/spares are now variants of Diesel Generator Sets: `p-10` redirects to `p-9`, and saved duplicate selections merge. Flow/Level/Pressure uses the former instrumentation ID `p-38`; Water Quality Analysers uses new stable ID `p-57` and displays as profile product 38. The source DOCX importer validates summary and detailed variant counts before writing.

## Images

All 56 families have an image. The 34 supplied representative Commons photographs remain unchanged. Six equipment/control-room photographs were extracted from the updated company profile, increasing the solution gallery to 36. The new Water Quality Analysers image is explicitly described as process-monitoring application context rather than an image of a particular analyser model.

Three existing Commons credit entries still use a generic creator label (products with stable IDs 05, 24 and 25). Their supplied source/licence records are exposed in the product details, but independent creator confirmation remains outstanding because Wikimedia access is blocked in this environment. No creator names or model claims were invented. The source profiles and previous source-image credit document remain the authority for provenance.

## Readability and final contact-reference review

Main reading copy was previously 11–14px in several components and mobile labels reached 8–9px. The revised native-font scale raises body/product reading copy to 16–18px, navigation to 15px and supporting labels to 12–14px. Mission/reason markers, workflow/industry numbers and card text are inset and aligned to first lines. Input controls are at least 16px, and the menu/filter offsets adjust to the larger text.

Office contacts are centralised, with readable lists and optional line breaks before email @ signs. The primary email is the first email common to both PDFs. The user resolved the source discrepancy by selecting the Company Profile's four-number list everywhere: 98999 → 87574 → 99106 → 93122. Both offices use its email order: chemotech.international, info.chemotechinternational, tapan.chemotech (all @gmail.com). The Company PDF's “80 more makes” and client-coverage wording take precedence over the differing DOCX copy for those passages.

The copy-enquiry option validates the form and copies a correctly addressed draft, including selected products. A selectable readonly draft is provided when clipboard access fails. No direct server-side delivery is claimed.


## Approved information architecture update

The user approved the review's page restructuring. Solutions & Services now owns capability explanations, the full delivery process, supporting images, service options and OEM information. Projects & Clients owns the unchanged reference data, capacities, locations, client names and sectors. About keeps the company facts and people; overlapping quality/mission/approach passages are consolidated into concise commitments. Home keeps its substantial overview and links to the detailed owners.

Products now starts with search and filters, with 12 cards initially and progressive access to the full catalogue. Full photos, specifications, variants and makes remain in product details. Existing IDs, saved enquiries and legacy links are preserved. The footer retains all four approved phone numbers but removes the repeated registration block and full category list. Page endings have relevant actions. Forms explicitly explain the email-draft workflow; direct submission remains a future backend integration.

Verification includes eight pages at six viewport widths, desktop/mobile WCAG automated checks, full progressive catalogue access, solution/category journeys, legacy redirects, deep-link focus, saved enquiries and reduced motion. Physical-device and Safari testing are not represented by Chromium checks.


## Post-restructure interaction review

Confirmed and fixed two issues: search/make filters were lost on reload/sharing, and removing selected equipment left a stale prepared enquiry visible while keyboard focus fell back to the document body. Filter URLs now restore search/make/category controls and handle invalid makes. Selection changes invalidate draft feedback, retain useful focus and announce the result. Storage/page-cache events refresh selections across tabs and restored pages. Mobile menu dismissal is consistent on outside clicks and desktop transitions. Focused journey regression tests reproduce the original failures and verify the fixes.


## Promotional number presentation

At the user's request, promotional totals use conservative rounded thresholds: 10+ years in business, 20+ sectors, 56 product families (exact, per the user’s final preference), 300+ variants and 50+ named OEMs. The country total stays exactly 3. Catalogue result/category counts, product specifications, profile-derived team experience, establishment dates, registrations and contacts retain their precise source values.
