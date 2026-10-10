# PIREVO Amazon affiliate attribution guard

**Verified manually on October 10, 2026**

* Amazon.com Associates Central **Store ID:** `pirevo-20`
* Registered website in Associates: `https://www.astralabsph.com/pirevo`
* The storefront `public/pirevo/config.js` and `public/pirevo/store-data.js` both configure the same Store ID.
* All **134** catalog Amazon product URLs contain the correct tag exactly once and match their ASINs and HTTPS amazon.com domain.
* Official Amazon Associates **Link Checker** returned **Success: valid tag or sub-tag for your Associate ID** for four sample catalog URLs (Churboro spice jars, LOVEVOOK satchel, COSRX essence, ZPISF Halloween decorations). This is manual sampling, not 134 separate Link Checker responses.
* Native Associates Central account-wide report last 30 days had 16 clicks, and October-to-date had 6 clicks, zero ordered items and zero shipped items (as checked Oct 10). These are account-level numbers and do not prove the exact source of each click.
* PIREVO's owned original KDP book links intentionally use untagged Amazon destinations (not affiliate products). The test explicitly documents and excepts the two known KDP ASINs.

## Automatic regression audit

Run `node tests/pirevo-affiliate-links.cjs` locally. A GitHub Actions workflow runs this guard on changes to PIREVO source files, PRs and on manual dispatch.

**Important scope limit:** Static validation cannot establish that an Amazon customer completed an eligible purchase, that a shopping session was not superseded by another Associates link, that the correct marketplace account is active, or that the referred order was shipped. Do **not** generate automated referral clicks/purchases to test attribution. Use Associates Central **Orders Report**, **Tracking ID Summary**, **Earnings Report** and the official **Link Checker** when necessary.

## Monitoring checklist

1. Keep a stable, verified tracking ID in all direct item URLs. Never replace it with an arbitrary tracking tag, and never copy someone else's Amazon Special Link.
2. Keep the canonical PIREVO domain registered under **Edit Your Website, Mobile App, and Alexa Skill List** in Associates Central.
3. Guide links use `guide.js` and `pirevo/config.js` to generate tagged search/product URLs; detail pages use `p.amazon` from the validated store data.
4. No auto-forwarding/URL cloaking between PIREVO product buttons and Amazon. Shoppers should intentionally click the labeled Amazon button.
5. Each affiliate landing page and social promotion needs clear compliant affiliate disclosure; confirm social profiles/sites are registered with Associates as required.
6. Amazon referral shopping sessions are ordinarily 24 hours from the click, with the specified in-cart extension; another Associate's link can displace the attribution.
7. Never treat first-party `affiliate_click` events, Pinterest outbound clicks, or customer screenshots of purchases as official Amazon confirmed orders. Use Associates Central account-level/Tracking ID reports for verified orders and shipped-item commissions.
8. Respect Amazon Associates rules against self-purchases, purchases by friends/family arranged through your links, automated clicks, inaccurate product claims and unauthorized rating/image use.
9. Amazon's own Link Checker tests self-constructed URLs, not arbitrary SiteStripe/Amazon-generated links. **Do not spam Link Checker at scale.**
10. For zero sales despite visits, compare **actual account-side click counts** and tracking IDs over matched dates before diagnosing buyer conversion or possible attribution.
