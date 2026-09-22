# AstraLabs PH | Day 1 actual media staged; Buffer release gate

**2026-09-23 PHT. Continue existing marketing project, no restart.** Work previously verified Buffer recurring schedules for all 3 channels. This document records actual six original Day1 video files AND twelve native stills, not merely an editorial plan. Stage date is NOT an assertion that new social posts are queued or native live.

## Actual results and rights QA

- Commercial marketing audio avoids the earlier REJECTED HeyGen Free narration. Used existing GitHub Actions free Kokoro-ONNX model/voice and our first-party mathematical original instrumental music, then exported videos using FFmpeg with measured sentence-length subtitles. No new paid plan, no duplicate first-wave videos, no Work credits consumed.

- Initial Day1 asset build [35765099121](https://github.com/sjgrind168/astralabsph-site/actions/runs/35765099121) produced six original 9:16 MP4s + six original 2:3 Pins + six original 4:5 FB graphics. Visual QA found initial oversized subtitles covering actual app screenshots. REJECTED those initial MP4s.

- Fixed subtitle size and reserved lower-screen band, then rendered six NEW corrected MP4s in [35765793325](https://github.com/sjgrind168/astralabsph-site/actions/runs/35765793325), where 6 MP4 + 12 authentic original stills and checksums were saved as GitHub Actions artifact 10712192542. That workflow's final hosting step failed from concurrent binary Git conflict, NOT from render or QA failure. Instead of retrying render and risking a second simultaneous push, a dedicated exact-SHA artifact-stage job [35766503075](https://github.com/sjgrind168/astralabsph-site/actions/runs/35766503075) verified all six MP4 checksums and successfully committed ONLY corrected six MP4s to latest `main`: [commit c8aef6e](https://github.com/sjgrind168/astralabsph-site/commit/c8aef6e).

- Independently fetched HEAD for six corrected MP4 official-site URLs, all `HTTP 200`, `Content-Type video/mp4`; verified each corrected source file H264 video 720x1280, constant 30fps with AAC audio. Twelve original image files are also versioned at `public/marketing/campaigns/seven_day/day1/`. Still-image proof ZIP comes from real original user-supplied released-app screenshot pixels with non-UI original illustrations; previous hallucinated image_gen fake app screenshots remain explicitly excluded.

- Caption size issue is now fixed in mid-video contact frame, but **final human audiovisual and product/rights approval is still required before social publication**. Tech checks and picture samples are not an invented human listening certification. No Buffer write was attempted as part of this build.

## Six original, distinct Day 1 ideas, each with 3 native assets

- **S26D1AV Cargo weight fits, does parcel fit hold?:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AV.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AV.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AV_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

- **S26D1AC Three independent checks for cargo estimates:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AC.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AC.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AC_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

- **S26D1AQ Weight okay, space tight: discussion:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AQ.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AQ.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1AQ_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

- **S26D1KV Passport photo saved, expiry verified?:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KV.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KV.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KV_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

- **S26D1KC Four-step pre-trip document routine:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KC.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KC.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KC_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

- **S26D1KQ Does saving a document photo set a reminder?:** [corrected original MP4](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KQ.mp4), [Pinterest genuine-UI 1000×1500 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KQ.png), [Facebook genuine-UI 1080×1350 PNG](https://www.astralabsph.com/marketing/campaigns/seven_day/day1/S26D1KQ_facebook.png). Platform captions were packaged privately for user review. No duplicate of Sep22 already-live Keepry/Astramate first-wave clips.

## Stop/go for automated Buffer publishing

- `marketing/automation/shared/ASTRALABS_THREE_CHANNEL_APPROVED_RELEASES_20260922.json` is still `releases: []`: **do not fake reviewer/rights receipt or flip new TikTok/Pinterest write flags** from a technical-only build. Once owner/authorized reviewer has watched actual finished clips and accepted exact captions/graphics/rights, add only individually approved validated entries; then pass actual provider history/queue checks before enabling any release.

- Latest observed existing SINGLE Facebook publishing writer [35757093960](https://github.com/sjgrind168/astralabsph-site/actions/runs/35757093960) still failed `Buffer HTTP 429`; do not blindly retry or assert API throughput is restored. Prior Work snapshot showed 8 legitimate Sep23 FB posts, 4/app including custom exceptions, preserved by one-day overfill guard. Current Buffer FB queue is NOT freshly queried; do not duplicate/delete.

- TikTok already-live first-wave Keepry/Astramate videos remain untouched, and old Keepry release cron retired. Exact internal Keepry Buffer Sent post-ID matching remains unverified. The TikTok new writer still has write flag FALSE.

- Pinterest exact AstraLabs Apps board **name** was authenticated UI-verified in Work, but exact board API service ID and a successful native first Pin proof are NOT verified. The PIREVO Finds draft is out of scope and must not be touched. Pinterest new writer remains FALSE.

- Six Day1 original core ideas provide 18 native placements **once approved and distributed**; no auto-post action here. The other 36 core ideas over days 2–7 have full unique scripts/visual briefs but not finished/hosted media yet, so one-day media supply is not seven-day operation. Do not advertise a complete seven-day buffer.

- Native social claims require actual Buffer scheduled IDs and platform live permalinks (not successful GitHub Action HOLD statuses or file hosting). Avoid posting expired scheduled times or filling Buffer Free 10-item cap blindly.

## User review/download

The generated review archive in the current Chat is `AstraLabs_Day1_6_Original_Posts_Voiced_Videos_Pins_FB_Review_Pack.zip`, containing exactly 6 corrected MP4 files, 6 Pins, 6 FB originals, 18 copy files, and a manifest with fixed URL and hash per video; no earlier rejected output included. Request just one asset-approval response after samples, not manual scheduling edits or repeated instructions.
