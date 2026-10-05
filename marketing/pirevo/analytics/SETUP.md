# PIREVO Business Analytics — one-time Google setup

The GitHub analytics health scheduler is already wired. It runs daily at **07:30 Asia/Manila**. Real business metrics remain private inside Google Analytics and Search Console; this public repository stores no traffic or conversion reports.

## What it will measure

- GA4 users and sessions
- Pinterest traffic
- Google organic traffic
- top landing pages
- PIREVO product-page views
- Amazon outbound `affiliate_click` events
- affiliate clicks per 100 sessions
- Google Search Console clicks, impressions, CTR, position, top queries and top pages
- recent-period vs previous-period movement\n\nThe site collects these metrics in GA4 once the Measurement ID is configured. GitHub Actions validates that the GA4/Search Console APIs remain reachable, but does not persist metric values in this public repository.

It deliberately does **not** call an Amazon outbound click a sale. Revenue/orders/commission remain blank until a trusted downstream sales source is connected.

## Required one-time values

### 1. GA4 web stream / Measurement ID

Create or use a GA4 property for `https://www.astralabsph.com/`.

Copy the public Measurement ID in the form:

`G-XXXXXXXXXX`

Then update:

`public/pirevo/config.js`

so:

`ga4Id:"G-XXXXXXXXXX"`

PIREVO's `business-analytics.js` will then begin collecting page views and business events.

### 2. GA4 Property ID

This is the numeric GA4 property ID, not the `G-` Measurement ID.

Add a GitHub repository variable:

`PIREVO_GA4_PROPERTY_ID`

### 3. Search Console property

Add a GitHub repository variable:

`PIREVO_GSC_SITE_URL`

Use the exact property string Search Console exposes, for example:

`https://www.astralabsph.com/`

or a domain property such as:

`sc-domain:astralabsph.com`

### 4. Google service account

Create a Google Cloud service account with read-only API use.

Enable:
- Google Analytics Data API
- Google Search Console API

Grant the service-account email Viewer/read access to:
- the GA4 property
- the Search Console property

Store the full service-account JSON as the GitHub Actions secret:

`GOOGLE_SERVICE_ACCOUNT_JSON`

## Safety

- No Google key is committed to the repository.
- The browser analytics layer does not send names, emails, payment details or Amazon order contents.
- Google signals and ad-personalization signals are disabled in the PIREVO tracker.
- Global Privacy Control / Do Not Track disables PIREVO's GA4 loader.
- The workflow fails closed into a blocker report when configuration is incomplete.
