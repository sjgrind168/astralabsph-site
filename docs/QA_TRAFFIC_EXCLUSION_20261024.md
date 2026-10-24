# QA traffic exclusion: AstraLabs + PIREVO

## Why
On October 24, 2026, an authorized browser inspection of a PIREVO product page was independently correlated with three first-party analytics events within the same second. `navigator.webdriver` was `false`, so a webdriver-only filter cannot prevent that contamination.

## Operator procedure (only for controlled test tabs)
1. Open a **new dedicated browser tab** directly at `https://www.astralabsph.com/pirevo/?__astra_qa=1` or `https://www.astralabsph.com/?__astra_qa=1` **after this change is deployed**.
2. Keep QA navigation within that tab. `sessionStorage.__astralabs_qa_no_track=1` persists through same-tab page navigation, including PIREVO product pages and the main app landing pages.
3. Confirm network traffic sends no POST to `pirevo_events` or `astralabs_site_events`, and that no GA4 event is emitted by the PIREVO analytics script.
4. Use a separate fresh browser tab without this flag to test consented ordinary tracking. Do not put `__astra_qa=1` into public Pins, affiliate links, social posts or canonical URLs.
5. Close the dedicated QA tab when finished. For repeated checks, always explicitly opt out **before** loading the first production page.

## Limits and release gates
- This is a **voluntary, session-only** suppression flag, not bot detection or proof that remaining sessions are humans. Untagged prior events remain intact and must not be bulk-deleted or reclassified.
- This flag suppresses analytics only, not affiliate navigation or any purchase action. It must never be used as an access-control or security mechanism.
- Respect GPC and DNT. Verify ordinary visitors still produce expected first-party events; no dashboard totals or financial facts are modified by this patch.
- Run `node --test tests/qa-traffic-optout.test.cjs`, syntax checks, full build and hosted regression QA before merge. Rebase against the pending Keepry attribution PR to avoid losing that fix.
