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


## v1.1 Google-only production controls
- Private pack updated to v1.1 and stored outside this public repo.
- Added local owner review dashboard with individual approve/reject and APPROVE ALL.
- Added Google Flow generation queue: 4 still-image prompts + 4 video-scene prompts for today's six content units.
- Added Gemini 3.8 Flash TTS helper for two natural narration WAVs; key is stored in macOS Keychain, never in this repo.
- Hard visual QA: feed images 4:5 at 1080x1350 final; videos 9:16, at least 720x1280, fixed 30 fps, readable subtitles, genuine app UI only.
- Current Google free-only architecture deliberately does NOT call paid Gemini image or Veo APIs. Images/video use the interactive Google Flow free allowance; text/TTS can use the Gemini free API tier.
- Social publication remains HOLD until generated media is visually reviewed and approved.


# RESEARCH CORRECTION — DO NOT DEPLOY THIS BRANCH

Date: 2026-09-26 PHT

This branch is intentionally halted after full feasibility verification.

Verified constraints:
- Google Flow itself offers a free no-subscription product tier with 50 daily Flow credits, including Veo/Omni capabilities in the Flow product UI.
- Google Gemini/Veo API video generation is NOT free-tier. Veo API requires paid usage/billing.
- Gemini image generation APIs (Nano Banana 2 / Nano Banana 2 Lite) are also NOT free-tier, even though image generation inside the Flow product can be available at no charge.
- The current ChatGPT conversation environment has no Google Flow connector/plugin and no authenticated interactive Flow browser control.
- Therefore a fully automated, Google-only, zero-cost, chat-only media-generation pipeline cannot be completed from this conversation environment today.
- n8n templates labeled "Use for free" refer to the workflow template; Google Veo generation still requires billing/API access in the documented setup.
- Existing Buffer/Metricool writers remain untouched by this experimental branch.

Decision:
- DO NOT merge or deploy the Flow automation assumptions from this branch.
- Keep only the useful uniqueness/QA/content-ledger design as reference.
- No further media-generation or schedule changes should occur unless an actually executable zero-cost path is verified first.
