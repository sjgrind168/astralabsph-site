#!/usr/bin/env python3
"""
PIREVO Business Analytics
Daily cloud report for:
- GA4 traffic + acquisition + landing pages + affiliate-click events
- Google Search Console queries/pages
- PIREVO analytics setup health

This script never fabricates traffic, conversions, orders, revenue, or commissions.
If credentials/configuration are incomplete, it writes a blocker report and exits cleanly.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "marketing" / "pirevo" / "analytics"
CONFIG = ROOT / "public" / "pirevo" / "config.js"
TZ = ZoneInfo("Asia/Manila")

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

def now_local():
    return datetime.now(TZ)

def read_measurement_id():
    try:
        text = CONFIG.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    m = re.search(r'ga4Id\s*:\s*["\']([^"\']*)["\']', text)
    return (m.group(1).strip() if m else "")

def pct(a, b):
    if not b:
        return None
    return round((a / b) * 100.0, 2)

def delta_pct(cur, prev):
    if prev in (None, 0):
        return None
    return round(((cur - prev) / prev) * 100.0, 2)

def rows_to_dicts(resp):
    headers = [h.name for h in resp.dimension_headers] + [h.name for h in resp.metric_headers]
    rows = []
    for row in resp.rows:
        vals = [x.value for x in row.dimension_values] + [x.value for x in row.metric_values]
        item = dict(zip(headers, vals))
        for k, v in list(item.items()):
            if k in {"sessions","totalUsers","activeUsers","engagedSessions","eventCount","screenPageViews"}:
                try: item[k] = int(float(v))
                except Exception: pass
            elif k in {"engagementRate","averageSessionDuration"}:
                try: item[k] = float(v)
                except Exception: pass
        rows.append(item)
    return rows

def ga4_report(client, property_id, start, end, dimensions, metrics, dimension_filter=None, limit=100):
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, RunReportRequest
    )
    req = RunReportRequest(
        property=f"properties/{property_id}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        dimensions=[Dimension(name=x) for x in dimensions],
        metrics=[Metric(name=x) for x in metrics],
        limit=limit,
    )
    if dimension_filter is not None:
        req.dimension_filter = dimension_filter
    return client.run_report(req)

def ga4_summary(credentials, property_id, start, end):
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import Filter, FilterExpression

    client = BetaAnalyticsDataClient(credentials=credentials)

    overview = ga4_report(
        client, property_id, start, end, [],
        ["sessions","totalUsers","activeUsers","engagedSessions","screenPageViews","eventCount"],
        limit=1
    )
    overview_rows = rows_to_dicts(overview)
    overview_data = overview_rows[0] if overview_rows else {}

    sources = rows_to_dicts(ga4_report(
        client, property_id, start, end,
        ["sessionSource","sessionMedium","sessionCampaignName"],
        ["sessions","totalUsers","engagedSessions"],
        limit=50
    ))

    landing = rows_to_dicts(ga4_report(
        client, property_id, start, end,
        ["landingPagePlusQueryString"],
        ["sessions","totalUsers","engagedSessions","screenPageViews"],
        limit=50
    ))

    events = rows_to_dicts(ga4_report(
        client, property_id, start, end,
        ["eventName"],
        ["eventCount"],
        limit=100
    ))
    event_map = {r.get("eventName",""): r.get("eventCount",0) for r in events}

    affiliate_filter = FilterExpression(
        filter=Filter(
            field_name="eventName",
            string_filter=Filter.StringFilter(
                match_type=Filter.StringFilter.MatchType.EXACT,
                value="affiliate_click"
            )
        )
    )
    affiliate_by_page = rows_to_dicts(ga4_report(
        client, property_id, start, end,
        ["pagePath"],
        ["eventCount"],
        dimension_filter=affiliate_filter,
        limit=100
    ))

    pinterest_sessions = sum(
        int(r.get("sessions",0) or 0)
        for r in sources
        if "pinterest" in str(r.get("sessionSource","")).lower()
    )
    google_organic_sessions = sum(
        int(r.get("sessions",0) or 0)
        for r in sources
        if "google" in str(r.get("sessionSource","")).lower()
        and str(r.get("sessionMedium","")).lower() == "organic"
    )

    affiliate_clicks = int(event_map.get("affiliate_click",0) or 0)
    product_views = int(event_map.get("view_item",0) or 0)
    sessions = int(overview_data.get("sessions",0) or 0)

    return {
        "overview": overview_data,
        "traffic_sources": sources[:30],
        "top_landing_pages": landing[:30],
        "events": event_map,
        "affiliate_clicks_by_page": affiliate_by_page[:50],
        "derived": {
            "pinterest_sessions": pinterest_sessions,
            "google_organic_sessions": google_organic_sessions,
            "product_views": product_views,
            "affiliate_clicks": affiliate_clicks,
            "affiliate_clicks_per_100_sessions": pct(affiliate_clicks, sessions),
        },
    }

def gsc_query(service, site_url, start, end, dimension):
    body = {
        "startDate": start,
        "endDate": end,
        "dimensions": [dimension],
        "rowLimit": 50,
        "dataState": "final",
    }
    data = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
    out = []
    for r in data.get("rows", []):
        out.append({
            dimension: (r.get("keys") or [""])[0],
            "clicks": r.get("clicks",0),
            "impressions": r.get("impressions",0),
            "ctr": round(float(r.get("ctr",0))*100, 2),
            "position": round(float(r.get("position",0)), 2),
        })
    return out

def gsc_summary(credentials, site_url, start, end):
    from googleapiclient.discovery import build
    svc = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)
    queries = gsc_query(svc, site_url, start, end, "query")
    pages = gsc_query(svc, site_url, start, end, "page")
    return {
        "top_queries": queries,
        "top_pages": pages,
        "totals": {
            "clicks": sum(x["clicks"] for x in queries),
            "impressions": sum(x["impressions"] for x in queries),
        }
    }

def credentials_from_env():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()
    if not raw:
        return None
    from google.oauth2 import service_account
    info = json.loads(raw)
    return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    now = now_local()
    today = now.date()
    end = today - timedelta(days=1)
    start = end - timedelta(days=6)
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=6)

    measurement_id = read_measurement_id()
    property_id = os.getenv("PIREVO_GA4_PROPERTY_ID","").strip()
    gsc_site = os.getenv("PIREVO_GSC_SITE_URL","").strip()
    creds_raw = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","").strip()

    report = {
        "report_version": 1,
        "generated_at": now.isoformat(),
        "timezone": "Asia/Manila",
        "window": {"start": str(start), "end": str(end)},
        "previous_window": {"start": str(prev_start), "end": str(prev_end)},
        "status": "BLOCKED_CONFIG",
        "blockers": [],
        "configuration": {
            "ga4_measurement_id_configured": bool(measurement_id),
            "ga4_property_id_configured": bool(property_id),
            "gsc_site_configured": bool(gsc_site),
            "google_service_account_configured": bool(creds_raw),
        },
        "ga4": None,
        "ga4_previous": None,
        "search_console": None,
        "business_summary": None,
        "notes": [
            "Amazon outbound clicks are not purchases.",
            "Revenue and commission are intentionally omitted unless a trusted downstream sales source is connected.",
        ],
    }

    if not measurement_id:
        report["blockers"].append("PIREVO GA4 measurement ID is blank in public/pirevo/config.js")
    if not property_id:
        report["blockers"].append("Missing PIREVO_GA4_PROPERTY_ID GitHub Actions variable/secret")
    if not gsc_site:
        report["blockers"].append("Missing PIREVO_GSC_SITE_URL GitHub Actions variable/secret")
    if not creds_raw:
        report["blockers"].append("Missing GOOGLE_SERVICE_ACCOUNT_JSON GitHub Actions secret")

    if property_id and gsc_site and creds_raw:
        try:
            creds = credentials_from_env()
            report["ga4"] = ga4_summary(creds, property_id, str(start), str(end))
            report["ga4_previous"] = ga4_summary(creds, property_id, str(prev_start), str(prev_end))
            report["search_console"] = gsc_summary(creds, gsc_site, str(start), str(end))

            cur = report["ga4"]["derived"]
            prev = report["ga4_previous"]["derived"]
            cur_over = report["ga4"]["overview"]
            prev_over = report["ga4_previous"]["overview"]
            report["business_summary"] = {
                "sessions": cur_over.get("sessions",0),
                "sessions_change_pct": delta_pct(cur_over.get("sessions",0), prev_over.get("sessions",0)),
                "users": cur_over.get("totalUsers",0),
                "pinterest_sessions": cur.get("pinterest_sessions",0),
                "google_organic_sessions": cur.get("google_organic_sessions",0),
                "product_views": cur.get("product_views",0),
                "affiliate_clicks": cur.get("affiliate_clicks",0),
                "affiliate_clicks_change_pct": delta_pct(cur.get("affiliate_clicks",0), prev.get("affiliate_clicks",0)),
                "affiliate_clicks_per_100_sessions": cur.get("affiliate_clicks_per_100_sessions"),
                "gsc_clicks": report["search_console"]["totals"]["clicks"],
                "gsc_impressions": report["search_console"]["totals"]["impressions"],
            }
            report["status"] = "OK" if measurement_id else "COLLECTION_NOT_ENABLED"
        except Exception as exc:
            report["status"] = "ERROR"
            report["blockers"].append(f"Analytics API error: {type(exc).__name__}: {exc}")

    # Privacy rule: this repository is public, so actual business metrics are never
    # written into the repository or printed into public Actions logs.
    print("PIREVO_BUSINESS_ANALYTICS_HEALTH")
    print(json.dumps({
        "status": report["status"],
        "ga4_access": bool(report.get("ga4")),
        "gsc_access": bool(report.get("search_console")),
        "collection_enabled": bool(measurement_id),
        "blockers": report["blockers"],
    }, indent=2))

if __name__ == "__main__":
    main()
