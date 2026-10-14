# PIREVO PINTEREST CREATIVE SOP v3.0 — HARD LOCK
Effective: 2026-10-14 Asia/Manila. Owner directive. Applies to every AstraLabs PH AI agent, ChatGPT, AKAME, local renderer, GitHub Actions, Buffer/Metricool queue and Pinterest native operator who creates or republishes a PIREVO Pin.

## Canonical visual reference and priority
APPROVED: `PIREVO_Drawer_Reset_Pin_2026-10-14.png` (1024 x 1536). Owner-provided visual sign-off on 2026-10-14. The finished published creative must match this **full-bleed premium editorial** quality, not a templated approximation.
REJECTED: owner's Pinterest screenshot on 2026-10-14 showing legacy Halloween/kitchen/products in framed centered white cards. These are now flagged REMAKE_CANDIDATE.
Priority: product truth + affiliate compliance + full-screen creative + human thumbnail QA > arbitrary daily publishing quota. US market primary, Canada secondary when verified. Free tools only.

## ABSOLUTE BANS: BLOCK PRODUCTION
- No product photo shrunk into white/cream framed rounded cards, tiles or bordered modules.
- No solid-color 40-55% title panels, repeated generic color bands or cookie-cutter half-photo/half-text grids.
- No artificial black/white product shot hovering inside decorative card; do not mistake image aspect ratio 2:3 for full-bleed quality.
- No duplicated Canva/HTML/Pillow legacy template, tiny central photo, dead space, big orange blobs or heavy CTA pill replacing product imagery.
- No image-not-loading text-only fallback; fail generation immediately instead.
- No generated asset re-encoded/reframed into a downgraded stock catalog template before Pinterest upload.
- No unsupported product claim, modified official product design, counterfeit-looking branding, unreadable headline, black preview or placeholder.
- No duplicate/near-duplicate Pins, unverifiable publish claims, direct-to-Amazon Pinterest links or URLs lacking the proper `pirevo-20` Amazon tag.
- No upload/publishing before visual comparison with the approved Drawer Reset image and native feed thumbnail.

## Required creative — FAIL CLOSED
1. Full-bleed 2:3 photo or high-quality generated lifestyle scene across the entire portrait, ideally 1000 x 1500+; 1024 x 1536 accepted. Hero environment fills ≥90% of canvas. The headline overlays the scene through natural shadow/gradient, not a separate panel.
2. Dominant, immediately recognizable product problem/use-case; exact branded product design stays faithful when depicting a specific SKU. If conceptual scene, mark `Illustrative lifestyle scene; check linked product`.
3. Premium art direction: realistic lighting, intentional depth, tactile material, believable scene. Separate compositions per Pin, not ten logo/color swaps.
4. Short truthful main headline (ideally 3-9 words) readable at actual Pinterest phone-feed thumbnail (~200 px wide). Text within safe margins. Subheadline optional and short.
5. Minimal PIREVO footer/signature and unobtrusive CTA over image. No giant rectangular CTA modules.
6. Creative source lawful: own footage/photos, appropriately licensed media or transparently labeled generated asset. Track source, rights and material AI modification.
7. Pins link to first-party matching `www.astralabsph.com/pirevo/products/{exact-slug}/` or approved guides. Product listed in current store-data.js; Amazon tag `pirevo-20` present and exact ASIN selected; correct product variant; no fake live price/review/rank.
8. English US/Canada keywords, relevant board, unique UTM `utm_content`, useful title and description with affiliate disclosure. Pinterest AI disclosure as required.
9. Design approval is **not** the same as technical size validation. Both manual visual QA at full resolution + feed thumbnail AND machine verification must pass.

## Production enforcement architecture
- `marketing/pirevo/validate_pinterest_v3.py`: validates an exact approved asset + frozen SHA-256, aspect/size, repeated image similarity, photo coverage heuristics, catalog ASIN, destination URL, UTM, board, disclosure, licensing, AI marking, reviewer and thumbnail approval. It rejects legacy template paths.
- `marketing/pirevo/approved_pins_v3.json`: explicit asset-level approval ledger. No default-approved entries; approval is granted per finished image only after QA. A script-generated entry or blank approval is never accepted.
- `marketing/pirevo/tests/test_pinterest_v3.py`: synthetic bad template regression tests and positive photo example tests.
- **LEGACY QUARANTINE:** old wave1/wave2/halloween wave3/christmas wave4 renderers and the legacy Buffer queue writer are stopped at executable entry. Their workflows no longer auto-schedule content. Keep old source/assets only for audit and remake.
- Any replacement scheduled pipeline must explicitly call the validator **before** enqueueing/posting. Until a complete route is wired and verified, use direct native Pinterest publication after manual and programmatic QA; do not bypass validator if it is available.
- CI on every future marketing/PIREVO change must run the pin policy check. CI passing a manifest is never proof of Pinterest publication.

## Required per-Pin QA record
`pin_id, product_slug, asin, local_image_path, image_sha256, source_rights, full_bleed_approved, no_card_layout, thumbnail_readable, title_verified, reviewer, reviewed_at_utc, product_variant_verified, affiliate_tag_verified, landing_verified, ai_disclosure_checked, pinterest_board, utm_destination, quality_gate_passed, publication_status`.
Only `PUBLISHED` after authenticated Pinterest confirms a real permanent Pin URL and time. The actor must record that source, not infer a success from a draft, upload, or queue.

## Remake audit and recovery plan
- 76 historical script-created product Pins across wave1=30, wave2=10, Halloween3=16, Christmas4=20 are **legacy source assets**, not 76 confirmed live published Pins.
- Reconcile live Pinterest @astralabsph pins by Pin URL, image screenshot/thumbnail, board, destination and source file. Categorize KEEP_PREMIUM, REMAKE_OLD_CARD, DRAFT_ISSUE, UNKNOWN, RETIRED_SEASONAL.
- On REMAKE: retain old Pin URL in audit; create **new, materially distinct, genuinely full-bleed** scene from its real product/brand, correct SKU and exact landing destination. Change enough that it is not a duplicate replacement spam Pin. Publish to board with validated links. Do not delete old published Pins in bulk or claim new sales without data.
- Prioritize evergreen US/Canada buyer intent (kitchen, organization, beauty, gifting) then current seasonal content (2026 Halloween before expiry, then Christmas). Don't waste time remaking expired Halloween imagery after season ends.
- Work in batches of 5-10 unique concepts, using individually generated premium visual sources; QA each exact exported image against approved reference. In any session, publish only what the browser can verify safely.
- Record tally separately: original assets inventoried, live published audited, flagged, remade generated, QA passed, new Pins actually published (permalink proof).

## Accountability and agent continuity
Every assigned agent MUST READ this v3 SOP and latest private Akashic project record before PIREVO media work. No creative improvisation outside permitted layout. Any exception/quality failure stops the release and is logged with cause/owner/time; fix before continuing, not later. Never substitute false completion for missing file uploads, inaccessible Pinterest or missing thumbnail QA.
Source-of-truth: private Akashic `pirevo` project and versioned `pirevo-pinterest-creative-hard-lock-v3` record. Public repository holds no passwords or secrets.
