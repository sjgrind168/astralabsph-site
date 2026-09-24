# AstraLabs PH: Global install-first funnel — execution log
**Owner goal:** Organic discovery -> relevant worldwide visits -> Android installs -> optional Astramate Premium / Keepry Plus purchases. Both apps reported available in 175 Play countries. No paid ads or additional subscriptions.

## Changes applied now
- The official canonical homepage (https://www.astralabsph.com/) reads the existing campaign `?app=astramate` or `?app=keepry` parameter already present in our Buffer Pinterest/TikTok/Facebook root-storefront links.
- A matching visitor now sees **one relevant value proposition and their app's Google Play install button FIRST**. The other app remains accessible. Homepage without app parameter is unchanged, so no loss of general discoverability.
- `src/App.jsx`: app-aware hero CTA and app-card anchors. `src/App.css`: secondary CTA visibility and anchor spacing.
- Existing `trackedPlay()` forwards incoming UTM parameters to the official Play link. It is **NOT** a verified purchase/install analytics integration; do not claim attribution without Console evidence.
- Existing privacy/policy URLs and both app storefront guides preserved. Existing Buffer schedules, approved media and unrelated PIREVO untouched.
- Targeted changes commit(s): `6aaa10fda21bb77cee8caf5fa54d0a587796a86d` (site app-aware hero), `8f6a66e8022ee1f12b9e6ba3783395ec98087af5` (visible CTA styling).
- CI existing `.github/workflows/astralabs-main-storefront-qa.yml` was triggered and passed build/markup checks: https://github.com/sjgrind168/astralabsph-site/actions/runs/36025654434. This confirms repository build, **not yet live production deployment**.

## Funnel logic
1. Organic educational content on existing channels with concrete app-verified benefit and canonical domain root URL plus `app` and UTM params.
2. Homepage presents immediately relevant app and clear free Android install CTA. Other app is accessible without switching or redirecting.
3. Google Play listing is the actual install decision point. No extra checkout/paywall on website; in-app optional purchase must function, via appropriate current app billing pathway.
4. Report separately: impressions/reach (where available), social outbound clicks, site views (only if independently measured), Play listing acquisitions, install first opens, paid purchase attempts and successful sales. **Never equate post scheduling or views with installs.**
5. Preserve 3-day pre-scheduled Buffer content. Future global originals and community outreach must not recycle the same TikTok master, duplicate posts or breach communities' rules.

## Immediate evidence gaps / owner-only access
- Recent Play Console screenshots show few acquisition/first opens and no reported buyers/revenue; **cannot tell self-installs from distinct users**, and "-" is not a zero count.
- Screenshot also shows **"Action required with your payments account"** for both apps. The actual detail notice must be read in authorized Console before interpreting how it affects respective upgrade flows; do not guess.
- Play Console Store performance screen per app: store listing visitors, acquisitions and source/country breakdown for the same date range; only then identify impression-to-listing vs listing-to-install bottlenecks.
- Confirm free -> Premium/Plus in-app billing and entitlement flow in a test user account, without purchasing anything without owner consent. Existing Keepry iOS restore work is separate.
- Live website deployment and actual click behavior in normal and narrow mobile viewport still need independent browser QA after CI.
- No public health/user-specific information or invented install/sales claims in marketing copy.

## Promotion guardrails
- English-first global audience: Astramate maritime students/cadets/deck officers/seafarers; Keepry worldwide record/renewal organizers.
- Astramate calculations are aids that require shipboard-source verification; no guarantee or unsupported tidal/compliance features.
- Keepry: records and dates entered by user; do not imply automatic document OCR, cloud sync, or automatic reminders when not configured.
- New FB = branded genuine-UI poster, Pinterest = vertical save-worthy pin, TikTok = 9:16 MP4 with genuine UI, authentic text/VO, clear root website CTA.
- Social distribution in relevant communities only where explicitly allowed; do not bulk-spam unsolicited groups or claim partnerships/testimonials.
