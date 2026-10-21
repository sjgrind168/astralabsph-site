# PIREVO International Product and Search Readiness | 2026-10-21

Scope: Existing live AstraLabs PH PIREVO affiliate site. Do not present PIREVO as an Amazon-owned store or local checkout. Amazon's current marketplace listing is the authority on local availability, sale price, seller and delivery.

## Authenticated account evidence recorded earlier on October 21
- Amazon.com Associates US store ID: pirevo-20.
- Global Earning Preferences page: 10 of 10 checked: United States, Canada, UK, Germany, France, Italy, Spain, Netherlands, Poland, Sweden.
- US Link Checker explicitly accepted a direct Apple AirTag example link with tag pirevo-20.
- The separate OneLink tracking-preferences table was empty. Amazon's simplified OneLink FAQ says this is normal with globally-enabled US store IDs.
- No separate linked Japan/Australia international store IDs were visible in Link Stores. No foreign registrations, taxes or payouts were changed.
- IMPORTANT: An active Earning Preferences checkbox is NOT proof the exact product exists in that local catalog, nor a substitute for any separate associates program requirement.

## Country program requirements (current official guidance)
United States: working primary program (US affiliate tag valid).
Canada, United Kingdom, Germany, France, Italy, Spain: simplified OneLink earning setting already checked. Amazon automatically enables US tracking IDs to earn globally with no mass link rewrite required.
Netherlands, Poland, Sweden, Japan, Australia: official standard OneLink guide calls for an independently enrolled Amazon Associates account in the target marketplace, then Account Settings > Link Store IDs, then OneLink default tracking ID selection. Do not infer registration from checked boxes. Owner-only registration/tax/payment steps require owner authorization.
Additional supported separate-account markets potentially include Singapore and Saudi Arabia, but new registrations are not part of the current authorized scope.

Official docs:
https://affiliate-program.amazon.com/help/node/topic/G2L3ZBRGXTS7EMEY
https://affiliate-program.amazon.com/help/node/topic/GC4NVV7K3XNG99X5
https://affiliate-program.amazon.com/help/node/topic/G84KVZ7BTNXHF4UH

## Product validation gate for each market
1. Open the exact PIREVO product detail page and validate model, size, color, and US ASIN.
2. Check the corresponding Amazon US listing, active seller, stock and current dimensions, using licensed official data or the authenticated product page.
3. Open Associates Central OneLink Check Matching Products for the US affiliate link where available.
4. For each target country, check the exact match / close match destination. Never assume identical ASIN across markets.
5. Record target local URL, local product identifier, seller, variant, stock, date/time and evidence link. Mark UNAVAILABLE if a real provider response confirms it; mark UNKNOWN for missing or blocked access.
6. Confirm the local landing destination keeps eligible Associates attribution using the provider's program and linked tracking ID. Never infer a commission from a redirect.
7. Keep the US original link unless an independently validated change is needed; preserve all existing US and Canadian payout and account settings.
8. Refresh volatile country stock and price status before presenting any specific in-stock claim.

## Website implementation and Google Search Console
- The catalog data included 138 products; 134 already had detail pages. Four missing detail pages were excluded from the new directory (see machine-readable manifest).
- Created /pirevo/catalog/ with 134 searchable, server-rendered internal links and 20 complete browseable category pages.
- Fourteen categories with at least three products are indexable; six small categories remain browseable but noindex until sufficient unique editorial depth/product inventory exists.
- Preserved old product and guide URLs.
- Replaced unsupported merchant-style Product JSON-LD on 135 product-selection articles with factual editorial Article structured data. Never synthesize review scores, prices or availability to qualify for Product rich snippets.
- Updated PIREVO homepage with evergreen metadata and category crawl links; updated sitemap.xml plus pirevo/sitemap.xml with 15 new indexable URLs.
- Google Search Console Oct 21 inspection: PIREVO homepage and Apple AirTag PDP both indexed and Google-canonical; the latter had Product snippet rich-result ERROR before the code correction.
- Search Analytics Sep 20 - Oct 18 did not show any PIREVO page impressions; this is distinct from Google deindexing.
- Search Console sitemap aggregate metadata reported 466 submitted, 0 indexed, but individual inspected PIREVO URLs returned indexed; treat that aggregate as lagging/inconsistent, not proof of 0 pages indexed.
- Rankings and rich results are not guaranteed. Confirm status with URL Inspection and equivalent 7/14/30-day performance windows after Google re-crawls.
- Do not enroll affiliate-only curated site as a pretend direct merchant in Google Shopping/Merchant Center.

SEO references:
https://developers.google.com/search/docs/specialty/ecommerce/designing-a-url-structure-for-ecommerce-sites
https://developers.google.com/search/docs/appearance/structured-data/product
https://developers.google.com/search/docs/appearance/reviews-system
https://developers.google.com/search/docs/specialty/ecommerce/how-to-launch-an-ecommerce-website

## Outstanding product-level issues
- Exact variant and marketplace stock verification must be completed progressively for the quality-gated catalog.
- Existing source has some dated ratings and volume claims; keep them source-dated and verify before new promotional creatives.
- Existing Amazon-hosted product images and their licensing/permission source need a separate compliance review before scaling new imagery.
- Verify the four excluded products and their ASINs before creating a product page.
- The browser session for Associates Central later required re-authentication, so no new region matching claims were fabricated.

## Runbook and rollback
- Run python3 tools/generate-pirevo-catalog.py after making approved changes to public/pirevo/store-data.js.
- The script only generates local public PIREVO pages and sitemaps and is intended to be idempotent.
- Verify links, output JSON-LD, source sitemap and deployment before pushing.
- Restore the previous Git commit if live behavior fails. Preserve all unrelated website code and existing Amazon/Google payments.

## October 21 product verification and affiliate policy QA
- All 135 product detail pages, homepage and client templates were cleaned of unsupported Amazon star ratings. No paid Amazon API or customer review access was used. US affiliate destinations with pirevo-20 and disclosures were preserved.
- AirTag second generation browser checks: US B0GJTFXNRX resolves but current browser delivery location is unsupported; CA B0GJTY1QYX in stock when observed; DE B0GQBHTSGR product identity verified but stock not verified; IT B0GJTCB2QM in stock when observed. UK/FR original US ASIN was 404; no confirmed exact local variant. Redirects and commissions have not been verified.
- Image licensing provenance still needs confirmation. Four products lack canonical product detail pages. New country Associates enrollments remain owner-only.

## OneLink and earning account verification after owner authentication (21 Oct 2026)
- Authenticated US store: pirevo-20.
- All ten global earning preferences checked: US CA UK DE FR IT ES NL PL SE.
- Payment Methods shows global earnings enabled, no further payment action required; all the same ten countries assigned to the existing bank method. No payment information was changed.
- US tax status Completed, Canada tax status Completed. Tax interviews and submissions unchanged.
- PIREVO website listed in Associates: https://www.astralabsph.com/pirevo.
- Link Stores shows no independently linked additional foreign store IDs; none were added.
- OneLink Tracking Preferences says no default IDs, which Amazon explicitly says may be ignored for globally enabled US store IDs.
- Official OneLink page /onelink/ returns HTTP 403 Access Denied despite successful other account pages. The Check Matching Products tool is inaccessible; product redirects and commission attribution NOT VERIFIED.
- Associates support form has anti-bot CAPTCHA. No support message was sent.
- No legal agreements, account enrollments, tax forms, payouts, or country settings modified.
