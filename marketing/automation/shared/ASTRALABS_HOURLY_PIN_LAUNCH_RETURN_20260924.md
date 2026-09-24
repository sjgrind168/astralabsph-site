# AstraLabs PH | One-per-hour Pinterest pilot: live execution handoff
**Time:** 2026-09-24 22:45 PHT.

## User-approved scope
Owner authorized immediate posting of attractive/useful Astramate and Keepry campaign concepts, with catchy descriptions and the official MAIN site included in EVERY post, using existing free Buffer connection and GitHub automation. This pilot has no separate manual approval demand. Do not claim owner watched a specific unshown still. No subscription, no new social account, no Akame modifications.

## Technical/visual integrity
The new ChatGPT-generated portrait posters in the conversation include invented/mock app UI and should NOT be passed off as genuine app screenshots. Accordingly, the live pilot uses SIX EXISTING FIRST-PARTY original stills with genuine AstraMate/Keepry released-app screenshot pixels hosted at `public/marketing/campaigns/seven_day/day1`. Their corresponding portrait and video concept style is preserved by the catchy hook; DO NOT say the generated mock-phone posters were published. TikTok is video-only via the existing writer and is not part of this image-only pilot.

## One-per-hour selected original image and caption schedule
All times **Asia/Manila**, one post per hour on the exact Pinterest `AstraLabs Apps | Astramate & Keepry` board, NOT PIREVO:
| PHT due date/time | App | Original first-party creative | Editorial hook |
|---|---|---|---|
| Sep24 23:45 | Astramate | S26D1AV.png | Cargo weight fits. Does the parcel fit the hold? |
| Sep25 00:45 | Keepry | S26D1KV.png | Passport photo saved. Did you enter the expiry date? |
| Sep25 01:45 | Astramate | S26D1AC.png | Three cargo checks: weight, space and stowage |
| Sep25 02:45 | Keepry | S26D1KC.png | Four steps to organize documents before a trip |
| Sep25 03:45 | Astramate | S26D1AQ.png | Cargo fits by weight. What about volume? |
| Sep25 04:45 | Keepry | S26D1KQ.png | Photo saved. Reminder set? Check both. |

- Copy/media/complete per-platform tracked main website links: [one-time six-post manifest](ASTRALABS_ONE_TIME_HOURLY_PIN_20260924.json).
- Website used in EVERY caption as requested: https://www.astralabsph.com/ .
- This is a **finite six-concept pilot, not an indefinite every-hour spam system**. Existing saved recurring Buffer day schedules remain unchanged, FB six/day three/app via its existing sole writer remains active. Do not infer that six Pinterest posts have already gone live.

## Actual Sep24 Buffer proof, not just green action status
- [Dry-run read-only successful](https://github.com/sjgrind168/astralabsph-site/actions/runs/36014900118) verified manifest, exact Apps board service ID `1143844074049569906`, hosted first-party PNG, root-site caption.
- The first publication attempt received a **Pinterest 500-character body limit rejection**: [error run](https://github.com/sjgrind168/astralabsph-site/actions/runs/36014957847). This was corrected for all six captions; checked every new caption 432–445 chars; added hard fail-closed 500-char validation.
- [Successful Buffer first scheduling run](https://github.com/sjgrind168/astralabsph-site/actions/runs/36015014712): exact original Astramate creative `ASTRALABS_HOURLY_PIN_A_CARGO_20260924`, Buffer scheduled post ID `6ab5376707a561292b16de27`, dueAt `2026-09-24T15:45:00.000Z` = Sep24 23:45 PHT. This is SCHEDULED, not proof that the Pin is native-live.
- [Independent fresh Buffer read-only verification](https://github.com/sjgrind168/astralabsph-site/actions/runs/36015106387) subsequently returned this exact ID in Pinterest SCHEDULED and same dueAt, alongside one untouched historical unrelated draft.
- Fresh read-only audit showed FB 3 queued/app, TikTok zero queued, first-wave videos untouched. No parallel FB writer or new TikTok posts created.

## Execution / remaining slots
- Existing, SINGLE `.github/workflows/astralabs-pinterest-queue.yml` now runs `hourly_six_pins.py` with existing stored `ASTRALABS_BUFFER_API_KEY`. A dedicated extra UTC cron `15 15-20 * * *` runs the finite overnight checks at 23:15, 00:15, 01:15, 02:15, 03:15, 04:15 PHT. Existing normal cron and other channel writers untouched. After Sep25 05:10 PHT the six-pin campaign expires and performs no further writes.
- Each check may add **at most one** unique next-hour post. It requires previous post status SENT with provider native externalLink before queueing next; preserves pre-existing drafts/queue, checks exact Apps board and public genuine-UI PNG, and never backfills an expired slot or repeats ambiguous errors. Thus five remaining slots are PLANNED and CONDITIONAL, not currently confirmed scheduled. GitHub Actions cron timing is best effort; if any first Pin fails to go native-live or a cron is late, this fail-closed pipeline may stop rather than post duplicates.
- In case of provider error or pipeline stall, read provider Sent/Queue/Error for exact post ID first, then resolve issue before attempting a retry; never blindly rerun the first-wave Keepry/TikTok, never touch PIREVO.
