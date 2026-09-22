# AstraLabs PH | Buffer ↔ GitHub posting-time synchronization status
**September 22, 2026, approximately 20:48 PHT.** Existing marketing project only. Owner asks to fix actual Buffer posting times across Facebook, TikTok, Pinterest and keep same source-of-truth in GitHub. This record deliberately distinguishes what has really changed from what still needs an authenticated Buffer browser save.

## Current observed provider facts from owner's 20:40 PHT screenshot and report

- Owner confirms Keepry first-wave video IS now live on TikTok. The TikTok Buffer channel @astralabsph screenshot shows Sent **4**, Queue **0**, weekly posting goal **2/5**, and a toast **Post was deleted** after owner removed obsolete pending item. These are owner-provided UI observations, not a fresh independent native Keepry permalink or verified exact Buffer post ID. Do not recreate or retry either original Keepry or old errored Astramate first-wave item.
- Existing TikTok Buffer recurring posting slots remain evidently different from the six times in GitHub: empty Queue visually offers Sep 25 22:00, Sep 26 17:25, Sep 27 09:13, Sep 28 09:01, Sep 29 07:01. Empty + New slots are NOT actual queued posts. Posting goal 2/5 is a tracker, not a queue count.
- Owner says Pinterest has **no published post**. The GitHub Pinterest workflow is a SAFE HOLD with write flag FALSE and zero independently approved ORIGINAL 2:3 Pins, and it must never touch PIREVO Finds. Pinterest Buffer posting-time UI and actual exact app board metadata are not freshly verified.
- Facebook existing writer remains ON and its generated customScheduled PHT dates use canonical slots; last observed API writer failure was HTTP 429. The owner has not provided fresh Facebook Buffer recurring posting time UI or real FB sent/queue inventory.

## Verified fixes committed to GitHub

1. Permanently RETIRED the old 19:30-PHT **daily** first-wave Keepry TikTok release workflow by removing its cron and publishing step; it now has a manual-only **NO-PUBLISH** message. Existing release source file and historical logs remain intact. [Final validated workflow](../../.github/workflows/astralabs-keepry-existing-video-now.yml) (repository-root link below) and commit fa151d6fbd944dec86d2282e07aec01ef5e53bbc. No repeat or duplicate Keepry media on later dates.
2. Removed the Facebook writer's arbitrary late-night recovery timestamps: it can now create posts only in the originally agreed three fixed slots for each app per PHT day, using a customScheduled dueAt. No queued/sent Buffer records were edited. [FB scheduler commit](https://github.com/sjgrind168/astralabsph-site/commit/780de2d1bd35f041011c8c5ae01d96a617816e83).
3. Recorded real owner-observed TikTok live/Queue 0, Pinterest no-live and **Buffer UI slot sync is NOT VERIFIED** in [daily config](ASTRALABS_THREE_CHANNEL_DAILY_CONFIG_20260922.json) and [control registry](../control/channels.json). GitHub schedule does not mutate the Buffer account's recurring Posting Schedule.
4. Fixed an invalid YAML shell colon after retiring the obsolete workflow; its last resulting state is valid YAML and cannot perform social mutations on manual dispatch. Updated an existing stale historical first-wave TikTok quality check to accept the actual bare-root caption while retaining root-only rule for ALL new promotions.
5. [Conformance run 35729127476](https://github.com/sjgrind168/astralabsph-site/actions/runs/35729127476) passed **9 unit tests** verifying the six FB agreed times equal canonical GitHub config, absence of arbitrary FB late-night slots, zero automatic original Keepry repeats, all three 3/app/day targets, root-CTA/approval guards and no Buffer writes with empty new media inventory. [Marketing quality gate run 35729189280](https://github.com/sjgrind168/astralabsph-site/actions/runs/35729189280) passed after historical TikTok QA correction. [Marketing Control Center run 35729292548](https://github.com/sjgrind168/astralabsph-site/actions/runs/35729292548) passed read-only status. TikTok/Pinterest new-writer runs 35729231267/35729231380 pass SAFE HOLD; none demonstrate new social publication.

## Exact target recurring Posting Schedule to set in actual Buffer UI, per connected channel

All **Monday–Sunday**, timezone **Asia/Manila** (Manila). Each of the three channels needs six daily slots in chronological order, because both apps share the same platform channel; old default auto-generated slots must be removed, not treated as future posts.

| Buffer channel | Six recurring daily slots, PHT (ASTRA/A = Astramate, K = Keepry) |
| --- | --- |
| Facebook AstraLabs PH | 09:30 A, 10:40 K, 14:10 A, 15:40 K, 19:10 A, 20:40 K |
| TikTok @astralabsph | 09:45 A, 10:55 K, 14:25 A, 15:55 K, 19:25 A, 20:55 K |
| Pinterest @astralabsph, exact AstraLabs Apps board for Pin assignment | 10:00 A, 11:10 K, 14:40 A, 16:10 K, 19:40 A, 21:10 K |

**Critical provider/API limitation:** The current Buffer GraphQL API supports addToQueue or a per-post customScheduled dueAt; its migration guide states recurring schedules formerly set in the legacy REST API are handled differently and gives no current GraphQL mutation to update a channel's recurring posting slots. Existing connected Chat has GitHub but NO authorized Browser/Computer Use or Buffer scheduling plugin. Thus a GitHub commit CANNOT save the actual Buffer Settings; no such browser save has been claimed or executed. Official Buffer instructions: https://support.buffer.com/en-us/articles/setting-up-your-timezones-and-posting-schedules-P4iSag90Fl and https://developers.buffer.com/guides/rest-migration.html .

### Direct authenticated provider completion: owner or ChatGPT Work Cloud Browser
- Open each connected Buffer channel, click its gear, set Timezone Manila, and in Posting Schedule remove unrelated autogenerated slot times; add exactly the channel's **six** target times to EVERY day Mon–Sun. Save and navigate away/back, screenshot Settings for each of the three channels; do not Copy Schedule across channels because their times are intentionally staggered.
- Inspect existing Queue/Sending/Sent/Draft/custom-dated items before making changes; do not delete or recreate posts. Per Buffer official help, recurring schedule edits move generic queued items into changed slots, but Custom scheduled existing posts are NOT moved. Do not edit/post/retry the already-published first-wave Keepry or Astramate items.
- Only after each actual Buffer screenshot matches this runbook, update provider_sync.buffer_posting_times_verified to true with separately recorded per-channel verification timestamps. Do not mark verified from blank placeholder slots or a GitHub green job.
- Pinterest posting is a SEPARATE blocker from slots: its new approved original 2:3 art ledger is empty and publisher is held. Completing posting-time Settings alone will not magically create six daily Pinterest Pins.

No purchases, cloned Buffer accounts, new unrelated website, deleted original video/old screenshots, or modified protected Mac folder.
