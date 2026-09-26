# ASTRA SOCIAL FACTORY v1 — build checkpoint — 2026-09-26

Restore-point branch: `astra-social-factory-v1-20260926`

## Production safety
- Existing Facebook/TikTok/Pinterest Buffer writers and recurring schedules are untouched.
- Existing Metricool scheduled posts are untouched.
- Factory publisher is DRY-RUN/HOLD until owner approves the first generated batch.
- No API keys, cookies, passwords, or private n8n credentials are stored here.
- The actual n8n workflow pack is kept outside this public repo for private local use.

## Locked rules
- Six new content units/day: Astramate 1 AI video + 2 images; Keepry 1 AI video + 2 images.
- TikTok and YouTube are video-only.
- No separate content unit may repeat an old topic+angle, hook, title, caption, visual-prompt core, or video-story structure.
- Cross-platform distribution of one approved content_id is allowed, but platform copy/title must be different.
- Generic, incomplete, blurry, unclear or fake-app-UI creative fails QA.
- Google-only media-generation direction: Gemini for copy/prompt planning, Google Flow for AI video scenes, genuine app UI composited after generation.
- All promotion points to https://www.astralabsph.com/

## Google free-video budget
Current design budget per PHT day:
- Google Flow allowance assumed: 50 daily credits, recheck before each production run.
- 4 video generations maximum/day.
- Prefer Veo 3.1 Lite at 10 credits/generation when still current.
- 2 scene generations per video × 2 app videos = 4 generations = 40 credits.
- Keep 10-credit reserve.
- Never spend credits blindly or exceed current verified allowance/cost.

## Current Metricool audit before this build
Brand 7092888, Asia/Manila:
- Sep 26 10:00 Astramate post is already PUBLISHED to Instagram, Threads and YouTube Shorts.
- Sep 26 16:00 Keepry post is PENDING on those three networks.
- Sep 27 and Sep 28 existing scheduled posts remain pending and were not edited.

## First factory test batch
Six new concept IDs:
- ASF26-A-V01 — COLREGS crossing-situation recall drill
- ASF26-A-I01 — IMDG segregation study check
- ASF26-A-I02 — IMSBC bulk-cargo study workflow
- ASF26-K-V01 — professional certificate renewal window
- ASF26-K-I01 — vehicle registration renewal record
- ASF26-K-I02 — service contract / warranty end date

Automated text-similarity check against:
- ASTRA 7-day/42 creative manifest
- finite Facebook daily content bank
- catchier-copy bank

All six pass the hard uniqueness threshold (<0.68); observed maximum similarities were 0.095, 0.095, 0.143, 0.125, 0.200 and 0.132 respectively.

## Next gate
Generate/inspect actual Google media for this first batch. Do not replace Buffer or Metricool schedules until the owner accepts the creative quality.
