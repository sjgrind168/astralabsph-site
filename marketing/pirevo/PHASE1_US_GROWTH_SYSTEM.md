# PIREVO Phase 1 — U.S. Organic Acquisition System

Status: implemented 2026-09-27
Market: United States
Budget: $0 paid media
Primary funnel: Pinterest / Google / short-form video → PIREVO → Amazon.com

## Channel order
1. Pinterest — search-like discovery, evergreen pin lifespan, visual buying intent.
2. Google SEO — ten original problem-first guides with crawlable URLs and schema hooks.
3. TikTok / Reels / YouTube Shorts — reuse each guide as short problem/solution content.

## Publishing rule
Use U.S. English, U.S. shopping language and Amazon.com. Do not fake U.S. residence or use VPN location tricks. Schedule by the audience timezone, preferably America/New_York, so DST is handled automatically instead of hard-coding Manila offsets.

## Initial content pillars
- Home & organization
- Desk & tech
- Travel
- Kitchen
- Dorm & campus
- Pets
- Car & road trips
- Gifts
- Seasonal home

## 30-day zero-cost cadence
- Pinterest: 2 fresh pins/day, rotating guides. Never publish the same creative/URL combination back-to-back.
- Short-form: 3 videos/week, 20–30 seconds, one problem + 3 useful criteria + PIREVO CTA.
- SEO: refresh 2 guides/week after observing outbound clicks and search impressions.

## U.S. posting windows to test
Use the platform scheduler in America/New_York time:
- 7:00–9:00 AM ET
- 7:00–10:00 PM ET
Test rather than assuming a universal best time. Keep creative/keyword performance as the primary signal.

## Short-form template
Hook: “Before you buy another [category], check these three things.”
Body: show the friction/problem, then three buying criteria from the related PIREVO guide.
CTA: “I put the full checklist on PIREVO. Link in profile.”

## Amazon activation gate
Current config intentionally keeps affiliateEnabled=false and amazonAssociateTag empty. Standard Amazon.com search links are used without an Associate tag.
After Amazon approval: add the tracking tag in public/pirevo/config.js and set affiliateEnabled=true. The Amazon disclosure then appears automatically on buying guides.

## Measurement
Optional GA4 is built in but disabled. Add a GA4 measurement ID in config.js only after the property is ready. Amazon outbound clicks are already instrumented as affiliate_click events when GA4 is active.

## Guardrails
- Never claim hands-on testing unless it actually happened.
- Never hard-code “live” Amazon prices.
- Verify size, compatibility, safety, shipping and retailer terms at the product page.
- Avoid copied retailer images/descriptions unless usage rights and Amazon program rules clearly allow them.
- Keep every guide useful even before affiliate links are active.
