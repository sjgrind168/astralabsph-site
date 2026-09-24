# AstraLabs PH | 3-day automation READY
**Verified:** 2026-09-24 23:56 PHT

Owner requested the refined 3-day AstraMate + Keepry campaign be made fully automatic through the existing GitHub + Buffer setup, with useful copy and the main site in every promotional post.

## What is now active
- **Facebook:** existing single writer remains the only FB publisher. It is enabled and refills **up to 3 distinct posts/app/day** on the established 09:30 / 14:10 / 19:10 Astramate and 10:40 / 15:40 / 20:40 Keepry cadence. It preserves existing scheduled items and Buffer Free queue capacity. Fresh audit shows Sep25 already has 3 scheduled Astramate + 3 scheduled Keepry.
- **TikTok:** existing single TikTok writer is enabled. The full owner-approved three-day MP4 set is now pre-staged in Buffer.
- **Pinterest:** existing single Pinterest writer is enabled on **AstraLabs Apps | Astramate & Keepry** only, service ID `1143844074049569906`. Full Day2/Day3 refined still-image set is pre-staged. The Day1 Astramate/Keepry concepts were deduped because the overnight owner-authorized Pinterest pilot already used those exact first-party media masters. PIREVO remains untouched.
- Official website in the campaign captions: **https://www.astralabsph.com/**.

## Final fresh Buffer proof
Read-only verification: https://github.com/sjgrind168/astralabsph-site/actions/runs/36023807760

### Facebook Sep25
- Astramate scheduled: 09:30, 14:10, 19:10 PHT.
- Keepry scheduled: 10:40, 15:40, 20:40 PHT.
- Existing daily cron will refill Sep26 then Sep27 automatically as queue capacity opens. No second FB writer was added.

### TikTok — all 3 days PRE-SCHEDULED
- Sep25 09:45 Astramate S26D1AV — Buffer `6ab5463b1af2d8014e2e253c`
- Sep25 10:55 Keepry S26D1KV — Buffer `6ab5463cc81dcef240741921`
- Sep26 14:25 Astramate S26D1AC — Buffer `6ab547a0c81dcef240744dbe`
- Sep26 15:55 Keepry S26D1KC — Buffer `6ab547a1d45dbd98f4194120`
- Sep27 19:25 Astramate S26D1AQ — Buffer `6ab547f1d45dbd98f4194c9a`
- Sep27 20:55 Keepry S26D1KQ — Buffer `6ab547f2fe8f81bcea815216`

All six are first-party hosted MP4s under `/marketing/campaigns/seven_day/day1/`; no already-live first-wave TikTok was reposted.

### Pinterest
Day1 was intentionally deduped against the already-started owner-authorized overnight Pin pilot:
- Astramate S26D1AV sent: Buffer `6ab5376707a561292b16de27`
- Keepry S26D1KV scheduled: Buffer `6ab545f167bd3aad31fb9fab`

Refined Day2 + Day3 are PRE-SCHEDULED:
- Sep26 14:40 Astramate S26D1AC — Buffer `6ab547a1ed952d22bace2a53`
- Sep26 16:10 Keepry S26D1KC — Buffer `6ab547a2c81dcef240744e18`
- Sep27 19:40 Astramate S26D1AQ — Buffer `6ab547f1fe8f81bcea8151c5`
- Sep27 21:10 Keepry S26D1KQ — Buffer `6ab547f2ed952d22bace3417`

One unrelated historical Pinterest draft remains preserved.

## Reliability changes made
- Enabled owner-approved TikTok and Pinterest releases through existing writers.
- Populated the approved release ledger for the six genuine first-party concepts.
- Expanded TikTok/Pinterest pre-staging from next-day only to the full finite three-day window, while retaining exact dueAt times, media verification, full-history dedupe, per-day caps, queue caps and fail-closed behavior.
- Regression QA passed after the change.
- A temporary coding error during that change produced two failed runs before any new write; it was corrected immediately. Subsequent regression, TikTok and Pinterest runs all passed and the final read-only Buffer audit confirmed the exact scheduled IDs above.
- No paid service, no new social account, no parallel writer, no PIREVO modification, no duplicate first-wave TikTok post.

## Source-of-truth files
- `marketing/automation/shared/ASTRALABS_THREE_CHANNEL_APPROVED_RELEASES_20260922.json`
- `marketing/automation/shared/three_channel_daily.py`
- `.github/workflows/astralabs-tiktok-video.yml`
- `.github/workflows/astralabs-pinterest-queue.yml`
- `.github/workflows/astralabs-daily-two-per-app.yml`

## Operational state
**READY / AUTOMATED.** TikTok is fully pre-scheduled for Sep25-Sep27. Pinterest Day2-Day3 is fully pre-scheduled and Day1 is covered by the already-running deduped pilot. Facebook Sep25 is fully queued and its existing cron will refill Sep26-Sep27 automatically as the Buffer Free queue opens.

Do not claim a scheduled post is native-live until Buffer returns SENT + native permalink.
