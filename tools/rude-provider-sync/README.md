# RUDE direct Google Play / Apple App Store Connect metrics pipeline

**Deployment:** Scheduled GitHub Action + provider-scoped read-only credentials -> authenticated Supabase Edge ingestion (`rude-provider-ingest`) -> restricted tables (`rude_store_metric_facts`, `rude_provider_sync_status`) -> authenticated RUDE bridge -> SwiftUI seven-metric cards.

**Safety:** All provider credentials must be stored in GitHub Actions **Repository secrets**. No provider keys or personal finance data in GitHub source, device binary, public webpages, or Akashic. The GitHub Action's `RUDE_PROVIDER_INGEST_TOKEN` uses a dedicated SHA-256 verifier in a restricted table, not the database service-role key. Wrong or absent key is HTTP 401. Idempotent `(provider,app,category,metric,unit,dates,report id)` updates; no synthetic zero metrics; preserve old imported KPIs. Reports are delayed, not live transaction feeds.

## Provider secrets needed before the first real sync

| GitHub Repository secret | How to obtain | Scope |
|---|---|---|
| `APPLE_ASC_ISSUER_ID` | App Store Connect Users and Access → Integrations → App Store Connect API → Team Keys | API issuer ID |
| `APPLE_ASC_KEY_ID` | Same Team Keys page | Key ID |
| `APPLE_ASC_P8_B64` | Base64 of the Apple Team `.p8` private key | **Sales and Reports**. Finance role is separately needed for final financial reports. |
| `APPLE_ASC_VENDOR_NUMBER` | Payments and Financial Reports, Vendor Number | Sales/Trends API filters |
| `GOOGLE_PLAY_SA_JSON_B64` | Base64 of an authorized Google Cloud service-account JSON | Google Play Console View app information global; View financial data global for GCS. Enable Play Developer Reporting API. |
| `GOOGLE_PLAY_REPORT_BUCKET` | Play Console → Download reports → Copy Cloud Storage URI (`pubsite_prod_rev_…`) | Cloud Storage read-only |

`RUDE_PROVIDER_INGEST_TOKEN` already provisioned securely in GitHub and server SHA-256 verifier. **Never paste Apple `.p8` or service-account JSON into a chat or a committed source file.**

## Seven reporting categories and exact status

1. Purchases per app: **Implemented parser** Apple daily Sales & Trends SUMMARY (paid units, refunded units), Google GCS estimated sales (charged orders, refund events).
2. Gross sales: **Implemented** separate transaction/customer currencies; no conversion or naive summation.
3. Developer proceeds: **Implemented for Apple** sales-report estimated per-unit proceeds. Google's GCS final earnings accounting requires vendor report reconciliation before publication.
4. Downloads/acquisitions: **Pending** Apple Analytics Reports `ONGOING` Downloads and Google acquisition GCS parsing (no authenticated source samples yet).
5. Payout: **Pending provider verified account-level payout**; requires Apple Finance role/financial reports and Google payout reconciliation. Never allocate account payout per app without documented provider source.
6. Crashes: **Implemented Google** Developer Reporting crashRate endpoint; Apple crashes require opt-in usage Analytics Report creation and privacy threshold.
7. Performance: **Implemented Google** ANR rate and slow-start rate; Apple Analytics Performance Reports require initial account Admin ONGOING report requests. Raw Google rate decimals are labeled `SOURCE_DECIMAL`, not guessed percent scaling.

**Apple Analytics Reports:** An Admin must create initial `ONGOING` report requests for Downloads, Purchases, Crashes and Performance. First reports may take 24–48 hours, with thresholded usage data. Sales and Reports keys can later download the generated reports. This pipeline intentionally leaves those additional categories pending until their schemas and access have been verified. <https://developer.apple.com/help/app-store-connect-analytics/overview/analytics-reports-api>

**Google:** GCS financial exports are posted with a delay and may be revised. Daily vitals API query uses [startTime,endTime) and only inserts actual published rows. <https://support.google.com/googleplay/android-developer/answer/6135870> | <https://developers.google.com/play/developer/reporting/reference/rest>

## Testing and activation

- Run `python3 -m unittest discover -s tools/rude-provider-sync -p 'test_*.py' -v` locally.
- The workflow may run without provider secrets: it prints `SKIPPED`, inserts **nothing**, and should not be described as direct sync operational.
- After configuring provider secrets in GitHub Repository Settings → Secrets and variables → Actions, manually dispatch **RUDE Official Provider Metrics**. Verify a real provider report was retrieved, protected ingestion accepted real facts, and RUDE displays a source date plus true status.
- **No account-key approval or paid API service is implied** by repository setup. Run only with owner-provisioned, least-privilege credentials. Do not send keys through messages.

## Troubleshooting

- **401** ingest = credential mismatch. Rotate GitHub repository secret and restricted DB verifier; never print tokens.
- **403** vendor = provider user/service-account permissions absent; not a zero-report.
- **404/204** Apple daily report = not yet published; skip, do not erase historical report.
- **No rows** = no published report or privacy threshold. Distinguish from legitimate confirmed zero.
- **Different periods/currencies** = separate rows, never mix or sum blindly.
