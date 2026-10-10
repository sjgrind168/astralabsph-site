# AstraLabs PH · Social Analytics Pipeline SOP

**Owner:** AstraLabs PH reporting. **Timezone:** Asia/Manila. **Updated:** 2026-10-10.

## One writer for Socials user interface
`public/analytics/dashboard-v2.js` controls filters, authentication and report fetching.
Its `paintSocial()` **only** delegates to `window.ASTRA_SOCIAL_NATIVE.render(state, helpers)`.
`public/analytics/social-native.js` is the **sole writer** of all social cards, labels,
source coverage, chart, table rows and channel details. Never render the same UI from
a second script. Filters call `paintSocial()` once; `renderAll()` calls it once after every refresh.

## Sources of truth and storage
* Verified provider connections live in private `public.astralabs_social_connections`. OAuth connection **does not mean** metrics were imported.
* Per-platform, per-metric, source-dated snapshots live in private `public.astralabs_social_snapshots`, unique on `(network, account_handle, metric, period_start, period_end)`.
* Verified daily series live in private `public.astralabs_social_daily`, unique on `(network, day, metric)`.
* The only authenticated dashboard read is `public.astralabs_social_metrics_snapshot(p_token)`. Do not ship sensitive data as static JSON.
* Latest report snapshots must preserve source name, reporting start/end, metric unit, evidence scope and capture time.
* Metricool brand 7092888 has six connected networks. It may provide real analytics for existing accounts, but after new OAuth connections its initial single-day zero rows are **not** proof of zero historical views.
* Native Facebook/Meta Business Suite, Pinterest Business Analytics and TikTok creator profiles may provide authenticated/manual backfills when Metricool does not return historical series. Indicate their source explicitly.

## Non-negotiable accounting rules
1. Treat NULL/missing data as **—**, never as confirmed zero. Zero is only valid when the source returned an actual zero for a precisely documented scope and period.
2. **TikTok `visible_video_views_total` is cumulative lifetime plays for visible videos**, not views gained in 7/30 days. TikTok `visible_videos` counts current public cards, not posts published in the website date range.
3. **Pinterest `native_views` is impressions** in the native Created Pins time window; `board_pin_inventory` is a current count, not published Pins during that period. Native outbound clicks are not verified site visits or Amazon orders.
4. **Facebook `native_views` is Meta's dated Views total**, not unique viewers. `viewers`, `page_visits`, `interactions` and `new_followers` each have their own definitions. Daily Views must sum to the documented aggregate for the same exact dates before import.
5. `followers` is an account count (LAST value when using Metricool), not a summable daily event; `published_posts` should be the SUM of actually published period posts only. Do not treat scheduled drafts as published.
6. **Never sum** mixed-period native views or lifetime plays into a claimed unique audience total. Cross-platform follower sums, when displayed, must be clearly qualified as duplicated account totals.
7. Website date selector affects **first-party website referrals**, not the original provider's native reporting window. Distinguish Facebook Page visits from PIREVO website sessions, retailer outbound clicks, Amazon Associates ordered/shipped units and commissions.
8. Do not overwrite a previously verified 28/30-day source with a newly connected platform's unlabeled one-day zero. Retrieve a full, matching source window and prove source completeness.
9. Persist changes idempotently using the existing unique keys and `ON CONFLICT ... DO UPDATE`; verify `period_start`, `period_end`, unit and source name. Do not duplicate counts from overlapping snapshots.
10. On login expiry, missing permission, provider timeout or incomplete output, retain previous data with its original source dates, report the blocker, and do not stamp a successful fresh import.

## Daily importer procedure
1. At scheduled sync, query Metricool brand connection status. Preserve OAuth only through official supported connectors; never save credentials in code.
2. Request the **full comparable provider window** for each connected network, with documented SUM/LAST aggregation semantics.
3. If no trustworthy provider history, inspect an authorized native report. Import only independently verified numbers and exact periods. If neither source available, leave the prior dated snapshot intact.
4. Upsert snapshots and optional daily series; ensure daily totals reconcile with provider totals. Read back the affected records and check that previously verified metrics have not disappeared.
5. Confirm the protected RPC returns the intended records without making private data public. Make a note of source age and pending gaps.
6. Check downstream conversion metrics separately. Zero PIREVO referral sessions does not imply zero social profile visits; zero Amazon outbound does not prove there were no native views.
7. Do not publish or change social content while running analytics sync. The Buffer and Metricool publishing workflows are independent.

## Release / incident checks
* Run `node --check public/analytics/social-native.js` and `node --check public/analytics/dashboard-v2.js`.
* Run `node tests/social-analytics-invariants.cjs`.
* In a temporary QA browser state, switch: TikTok → Facebook → Pinterest → All → Facebook → TikTok. Verify exact label, value, chart and one active filter throughout. Refresh while selected; no previous-channel labels may remain.
* For Facebook with dated daily records, render the daily bar chart; for TikTok lacking true daily history, **show the missing-series explanation rather than fake bars**.
* Verify mobile 390px without horizontal overflow and preserve the private access gate.
* After changes, check GitHub commit, Vercel production **READY**, deployed asset versions and active URL `https://www.astralabsph.com/analytics/?tab=socials`.
* When a repeated display bug occurs, fix the **single authoritative renderer and automated test**, not another overriding patch.
