# AstraLabs Marketing Control Center

## Browser web app (no Terminal or Xcode needed)

- **Live read-only dashboard:** https://astralabs-marketing-control-o52cw9.v2.appdeploy.ai/
- It displays the existing public GitHub 42-creative plan, channel registry, public workflow run states, SOP/handoff links and clearly unconnected performance-source cards. The web app is a separate deployed viewer and is NOT a new social publisher or owner-authenticated private analytics console.
- **Public-safe:** It reads only public repository metadata. Do not input secrets, account tokens, personal performance exports or customer data. A protected owner-only backend and verified connector permissions are prerequisites for any editing, publishing, or private metrics.
- No Mac clone, Apple developer tools or Xcode license acceptance is needed to use the dashboard. The source Mac folder and existing platform workflows remain untouched by this web app.
**Single operator entrypoint.** This is an incremental internal control plane in the existing GitHub repo, not a new publicly accessible social login dashboard or another advertising app. All authorized external publishing remains in the existing platform-specific workflows.

## Open one place before every marketing change
1. Read `channels.json` for one active writer/route per channel, ownership and exact blockers. It is the **canonical channel registry** and contains no credentials.
2. Read the existing **single 42-creative** source: `../shared/ASTRALABS_7DAY_42_CREATIVE_MANIFEST_20260923.json`. Do not copy or regenerate competing calendars; edit the authoritative plan only after a fresh Work/Chat reconciliation.
3. Read `../shared/ASTRALABS_GLOBAL_GROWTH_SOP_20260922.md` to review actual claims, original app visuals, legitimate free production rights, root-only storefront URL and conversion metrics.
4. Run the read-only GitHub workflow `.github/workflows/astralabs-marketing-control.yml` to get a fresh seven-day inventory and channel-gate report as a downloadable job artifact and GitHub run summary. **The artifact reports editorial preparedness, not Buffer inventory or live social publication.**
5. Before external write: inspect the specific channel's current native and Buffer queue, queued/sent/draft/error status and exact account/board, reconcile existing slots, confirm media license, final rendered asset, truthful copy, unique campaign ID and native proof. One authorized writer per channel. Never blindly retry after HTTP 429 or an ambiguous post creation.

## Logical folders, without renaming or deleting owner's main source folder
```text
~/Documents/AstraLabs_Marketing_Automation/       # preserved owner's source, not accessible to browser Chat by assumption
GitHub sjgrind168/astralabsph-site/
  marketing/automation/
    control/channels.json                         # one channel registry, no secrets
    control/build_status.py                       # read-only summary from existing 42-record manifest
    control/out/                               # ephemeral CI report, never customer data
    shared/ASTRALABS_7DAY_42_CREATIVE_MANIFEST_20260923.json
    shared/ASTRALABS_GLOBAL_GROWTH_SOP_20260922.md
    shared/ASTRALABS_WORK_RETURN_HANDOFF_20260922.md
    facebook/scripts/                           # only existing FB writer controls real posts
    pinterest/scripts/                          # exact board gate; no PIREVO Finds
    tiktok/scripts/                             # approved 30fps real media/AI disclosure
  public/marketing/                             # public rights-cleared media only, no user documents
  .github/workflows/                             # individual cloud runners and human-readable QA
```

## Operations and growth boundaries
- **No new paid application or duplicate queue orchestration yet.** New UI can be added later to the protected owner-facing workspace when publisher connectors, approval workflow and useful analytics are proven. Never expose social controls, API tokens, daily sales information or hidden drafts through the public premium storefront.
- **Buffer primary:** existing three channels Facebook, Pinterest and TikTok. A second Buffer organization/account would need owner authorization, distinct genuine channels, separate authenticated API keys, and policy/limit verification. A channel cannot be linked to two Buffer accounts simultaneously. Prefer free native YouTube Studio and Meta Business Suite rather than making a second identity just to increase Free allowance.
- **YouTube:** native Studio scheduling on the authentic owner account after fixing browser access; public YouTube API uploads from unverified projects can be private-only pending audit. Never claim a fully authorized uploader until a native public scheduled Short is proven.
- **Instagram:** owner has no verified dedicated AstraLabs profile; establish authentic account and Meta login once, then schedule via native Meta tools if eligible. No Instagram publication before owner authorization.
- **Reddit:** prepare helpful posts for manually rule-checked communities, disclose connection to AstraLabs and include the root site only where permitted. No unattended mass-post bot.
- **LinkedIn:** optional verified Page, practical professional stories and insights, not a duplicate Facebook ad wall.
- **Daily volume:** user's goal is 3 original pieces per app per PHT day in 7-day 42-creative plan. The present FB workflow still implements 2/app/day; this control center does NOT silently change that. Convert only after original assets and approved captions are ready, all old queues reconciled, and platform slot capacity permits.
- **Budget:** PHP0 additional fees without explicit owner approval. GitHub Actions standard runners on public repositories are free subject to service use limits, but provider APIs and account access still have their own quotas and policies.

## Publication states
`PLANNED` -> `RENDERED` -> `CLAIM_AND_RIGHTS_QA` -> `APPROVED` -> `QUEUED` -> `LIVE_VERIFIED`. Hold on insufficient app proof, product errors, source licensing uncertainty, an occupied channel, provider rate limiting, stale credentials, or missing native permalink. GitHub build PASS only confirms the plan and config, never a real social post.

## Owner / Work handoff checklist
Only ask the owner for external account ownership/login, approved commercial-use media rights, true app screenshots with dummy data, or an explicit monetization spend/creative approval. Work may use its cloud browser, but **Mac local Documents access must be proven**, not assumed: prior Work session saw a Linux runtime and could not see owner's Mac. A bounded Work session should return account names, provider IDs (never secrets), exact blocker/status, evidence of scheduled/live content and updated handoff. Resume from it in Chat without restarting existing engineering or deleting anything.
