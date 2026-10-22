#!/usr/bin/env python3
"""RUDE official-provider read-only report ingestion. No API keys in source.

Only publishes source-backed facts. Missing, unauthorized, or unpublished vendor
reports produce NO zero rows. Scheduled workflow runs must not be called live
until at least one real provider report was imported successfully.
"""
import base64, collections, csv, datetime as dt, decimal, gzip, hashlib, io, json, os, sys, urllib.parse, urllib.request, zipfile
from decimal import Decimal

APPLE_IDS = {"6812828056": "astramate", "6813155959": "keepry"}
PACKAGE_IDS = {"com.astralabs.astramate": "astramate", "com.astralabs.keepry": "keepry"}
UTC = dt.timezone.utc

def source_key(provider, app, cat, metric, unit, day, identity):
    key = "|".join([provider, app, cat, metric, unit, str(day), identity])
    return "rude." + hashlib.sha256(key.encode()).hexdigest()

def fact(provider, app, cat, metric, amount, unit, start, end, identity, provenance, status="estimated", app_version=None):
    if amount is None or not Decimal(str(amount)).is_finite():
        raise ValueError("Nonfinite reporting value")
    if cat in {"purchases", "downloads", "crashes"} and Decimal(str(amount)) < 0:
        raise ValueError("Negative count; instead record refunds separately")
    val=float(Decimal(str(amount)).quantize(Decimal("0.000001")))
    return {"app_key":app,"category":cat,"metric":metric,"metric_value":val,"metric_unit":unit,
            "period_start":str(start),"period_end":str(end),"report_status":status,
            "source_report_id":source_key(provider,app,cat,metric,unit,end,identity),
            "provenance":provenance[:500],"app_version":app_version}

def rows_table(text):
    reader=csv.DictReader(io.StringIO(text),delimiter="\t")
    if not reader.fieldnames: raise ValueError("Missing Apple report header")
    return list(reader)

def money(s):
    return Decimal(str(s or "0").replace(",", "").strip())

def apple_summary_sales(data, day, report_id, app_ids=None):
    """Apple Sales & Trends SUMMARY TSV: counts, gross per customer currency,
    estimated proceeds per proceeds currency. Never convert or sum currencies.
    """
    apps=app_ids or APPLE_IDS
    content=gzip.decompress(data).decode("utf-8-sig") if data[:2]==b"\x1f\x8b" else data.decode("utf-8-sig")
    rows=rows_table(content)
    required={"Apple Identifier","Units","Product Type Identifier","Customer Price","Customer Currency","Developer Proceeds","Currency of Proceeds"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError("Apple source schema missing expected fields")
    totals=collections.defaultdict(Decimal)
    for row in rows:
        app=apps.get(str(row["Apple Identifier"]).strip())
        if not app: continue
        units=money(row["Units"]); price=money(row["Customer Price"]);proceeds=money(row["Developer Proceeds"])
        prod=(row["Product Type Identifier"] or "").strip().upper()
        buyer=(row["Customer Currency"] or "").strip().upper()
        merchant=(row["Currency of Proceeds"] or "").strip().upper()
        # A free app download is NOT a paid purchase. Count paid sales only;
        # negative unit rows count as refunds instead of negative purchases.
        paid = price != 0 or prod.startswith("IA")
        if paid and units>0: totals[app,"purchases","paid_units","COUNT"]+=units
        if paid and units<0: totals[app,"purchases","refunded_units","COUNT"]+=abs(units)
        if buyer and len(buyer)==3 and price!=0:
            # Apple refund prices are negative; abs(units) retains their sign.
            totals[app,"gross_sales","customer_price_total",buyer]+=abs(units)*price
        if merchant and len(merchant)==3 and proceeds!=0:
            totals[app,"developer_proceeds","estimated_proceeds",merchant]+=units*proceeds
    out=[]
    for (app,cat,key,unit),value in sorted(totals.items()):
        out.append(fact("app_store_connect",app,cat,key,value,unit,day,day,
             report_id+"-"+key+"-"+unit,"App Store Connect Sales & Trends daily SUMMARY; " +report_id, "estimated"))
    return out

def decode_google_zip(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names=[n for n in z.namelist() if n.lower().endswith(".csv")]
        if not names: raise ValueError("Google CSV missing from official ZIP")
        raw=z.read(names[0])
        if raw.startswith((b"\xff\xfe",b"\xfe\xff")) or raw[1:2] == b"\x00":
            return raw.decode("utf-16")
        return raw.decode("utf-8-sig")

def google_sales_report(blob, report_id, package_ids=None):
    """Google monthly estimated sales report with country-specific buyer currency.
    Does not represent payout or developer proceeds. One charged row per order.
    """
    apps=package_ids or PACKAGE_IDS
    rows=list(csv.DictReader(io.StringIO(decode_google_zip(blob))))
    required={"Package ID","Order Number","Financial Status","Order Charged Date","Currency of Sale","Charged Amount"}
    if not rows or not required.issubset(rows[0]):raise ValueError("Google estimated sales schema unavailable")
    totals=collections.defaultdict(Decimal)
    seen=set()
    for row in rows:
        app=apps.get((row["Package ID"] or "").strip());day=(row["Order Charged Date"] or "").strip()
        if not app or not day or len(day)!=10:continue
        currency=(row["Currency of Sale"] or "").strip().upper()
        if len(currency)!=3:continue
        status=(row["Financial Status"] or "").lower().strip()
        charge=money(row["Charged Amount"])
        order=(row["Order Number"] or "").strip()
        if status=="charged":
            order_identity=(app,day,order,(row.get("SKU ID") or ""))
            if order_identity not in seen:
                totals[app,day,"purchases","charged_orders","COUNT"]+=1
                seen.add(order_identity)
            totals[app,day,"gross_sales","customer_charged",currency]+=charge
        elif "refund" in status:
            totals[app,day,"purchases","refund_events","COUNT"]+=1
            totals[app,day,"gross_sales","customer_refunded",currency]+=abs(charge)
    out=[]
    for (app,day,cat,key,unit),value in sorted(totals.items()):
        out.append(fact("google_play",app,cat,key,value,unit,day,day,report_id+"-"+key+"-"+unit,
              "Google Play GCS estimated sales CSV; customer gross (tax inclusive); "+report_id,"estimated"))
    return out

def google_vitals_data(response, app, endpoint, request_day):
    """Record raw documented metric decimals without guessing percent scaling."""
    allowed={"crashRate":("crashes","crash_rate"),"anrRate":("performance","anr_rate"),
             "slowStartRate":("performance","slow_start_rate")}
    if endpoint not in allowed:raise ValueError("Unexpected Android vitals field")
    category,label=allowed[endpoint];out=[]
    for row in response.get("rows",[]):
        dim={x.get("dimension"):x.get("stringValue","") for x in row.get("dimensions",[])}
        tag=dim.get("startType","")
        key=label+("_"+tag.lower() if tag else "")
        for m in row.get("metrics",[]):
            if m.get("metric")!=endpoint:continue
            raw=m.get("decimalValue",{})
            value=raw.get("value") if isinstance(raw,dict) else raw
            if value is None:continue
            dd=row.get("startTime",{}) or {}
            day="%04d-%02d-%02d"%(int(dd.get("year",int(request_day[:4]))),int(dd.get("month",int(request_day[5:7]))),int(dd.get("day",int(request_day[8:10]))))
            out.append(fact("google_play",app,category,key,Decimal(str(value)),"SOURCE_DECIMAL",day,day,
                       endpoint+"-"+tag+"-"+day,"Google Play Developer Reporting API v1beta1 "+endpoint+"; source decimal (do not assume percent scaling)","verified"))
    return out

def provider_ingest(provider, facts):
    if not facts: return {"skipped":"no published facts"}
    token=os.environ.get("RUDE_PROVIDER_INGEST_TOKEN","")
    if not token:raise RuntimeError("Missing secure importer authorization")
    endpoint="https://cscqulbludoyzsgniits.supabase.co/functions/v1/rude-provider-ingest"
    accepted=0
    for i in range(0,len(facts),80):
        payload=json.dumps({"action":"ingest","provider":provider,"facts":facts[i:i+80]}).encode()
        req=urllib.request.Request(endpoint,data=payload,method="POST",headers={"Authorization":"Bearer "+token,"Content-Type":"application/json"})
        with urllib.request.urlopen(req,timeout=25) as response:
            answer=json.load(response)
            if not answer.get("ok"):raise RuntimeError("Verified importer refused the provider report")
            accepted+=int(answer["accepted"])
    return {"accepted":accepted}

def apple_fetch(day):
    import jwt
    issuer=os.environ["APPLE_ASC_ISSUER_ID"];kid=os.environ["APPLE_ASC_KEY_ID"]
    key=base64.b64decode(os.environ["APPLE_ASC_P8_B64"]).decode()
    start=int(dt.datetime.now(UTC).timestamp())
    token=jwt.encode({"iss":issuer,"iat":start,"exp":start+600,"aud":"appstoreconnect-v1"},key,algorithm="ES256",headers={"kid":kid,"typ":"JWT"})
    params={"filter[frequency]":"DAILY","filter[reportType]":"SALES","filter[reportSubType]":"SUMMARY",
            "filter[vendorNumber]":os.environ["APPLE_ASC_VENDOR_NUMBER"],"filter[reportDate]":day}
    url="https://api.appstoreconnect.apple.com/v1/salesReports?"+urllib.parse.urlencode(params)
    request=urllib.request.Request(url,headers={"Authorization":"Bearer "+token,"Accept":"application/a-gzip, application/octet-stream"})
    with urllib.request.urlopen(request,timeout=40) as response:return response.read()

def google_credentials(scopes):
    """Prefer short-lived GitHub Actions OIDC/ADC; legacy scoped key only when supplied.
    No credentials are returned in logs or exported to the iOS client.
    """
    import google.auth
    from google.oauth2 import service_account
    legacy=os.environ.get("GOOGLE_PLAY_SA_JSON_B64","")
    if legacy:
        info=json.loads(base64.b64decode(legacy))
        return service_account.Credentials.from_service_account_info(info,scopes=scopes),info.get("project_id")
    return google.auth.default(scopes=scopes)

def google_storage_client():
    from google.cloud import storage
    credentials,project=google_credentials(["https://www.googleapis.com/auth/devstorage.read_only"])
    return storage.Client(project=project,credentials=credentials)

def google_bucket():
    name=os.environ.get("GOOGLE_PLAY_REPORT_BUCKET","").replace("gs://", "").strip("/")
    if not name.startswith("pubsite_prod_") or "/" in name:
        raise ValueError("Official Google Play reporting bucket is not configured")
    return name

def read_csv_source(raw):
    """Google bulk exports are often UTF-16, not UTF-8."""
    if raw.startswith((b"\xff\xfe",b"\xfe\xff")) or raw[1:2]==b"\x00":
        return raw.decode("utf-16")
    return raw.decode("utf-8-sig")

def google_installs_report(raw, report_id, package_ids=None):
    """Parse one package's *country* dimension report for per-day totals.
    Never mix device/country/app-version reports, or sum across dimensions.
    Daily user installs differ from Play Console device acquisitions.
    """
    mapping=package_ids or PACKAGE_IDS
    source=csv.DictReader(io.StringIO(read_csv_source(raw)))
    required={"Date","Package Name","Daily User Installs","Daily Device Installs"}
    if not source.fieldnames or not required.issubset(set(source.fieldnames)):
        raise ValueError("Official Play installs CSV schema unavailable")
    grouped=collections.defaultdict(Decimal)
    observed=set()
    for row in source:
        app=mapping.get((row.get("Package Name") or "").strip())
        day=(row.get("Date") or "").strip()
        if not app or not day or len(day)!=10:
            continue
        try: dt.date.fromisoformat(day)
        except ValueError: continue
        country=(row.get("Country") or "").strip()
        identity=(app,day,country)
        if identity in observed:raise ValueError("Duplicate country/date row in official installs report")
        observed.add(identity)
        for name,key in (("Daily User Installs","daily_user_installs"),("Daily Device Installs","daily_device_installs")):
            val=Decimal(str(row.get(name) or "0").replace(",",""))
            if val<0 or not val.is_finite(): raise ValueError("Invalid official install count")
            grouped[app,day,key]+=val
    return [fact("google_play",app,"downloads",key,value,"COUNT",day,day,
            report_id+"-"+app+"-"+day+"-"+key,
            "Official Google Play Cloud Storage country-dimension installs export; "+report_id,"verified")
            for (app,day,key),value in sorted(grouped.items())]

def google_fetch_installs(month):
    from google.api_core.exceptions import NotFound
    client=google_storage_client()
    bucket=client.bucket(google_bucket())
    out=[]
    for pkg in PACKAGE_IDS:
        name=f"stats/installs/installs_{pkg}_{month}_country.csv"
        try: raw=bucket.blob(name).download_as_bytes(timeout=40)
        except NotFound:
            print("GOOGLE_INSTALLS_PENDING",pkg,month)
            continue
        rows=google_installs_report(raw,"play_gcs_"+name)
        if not rows:print("GOOGLE_INSTALLS_SOURCE_EMPTY",pkg,month)
        out.extend(rows)
    return out

def google_fetch_sales(month):
    from google.api_core.exceptions import NotFound
    client=google_storage_client()
    bucket=client.bucket(google_bucket())
    name="sales/salesreport_"+month+".zip"
    try:return bucket.blob(name).download_as_bytes(timeout=40)
    except NotFound:
        print("GOOGLE_SALES_REPORT_PENDING",month)
        return None

def google_fetch_vitals(app_pkg,day):
    import requests
    from google.auth.transport.requests import Request
    creds,_project=google_credentials(["https://www.googleapis.com/auth/playdeveloperreporting"])
    creds.refresh(Request())
    head={"Authorization":"Bearer "+creds.token,"Content-Type":"application/json"}
    start={"year":int(day[:4]),"month":int(day[5:7]),"day":int(day[8:10])}
    after=(dt.date.fromisoformat(day)+dt.timedelta(days=1))
    end={"year":after.year,"month":after.month,"day":after.day}
    out=[]
    for group,metric in [("crashRateMetricSet","crashRate"),("anrRateMetricSet","anrRate"),("slowStartRateMetricSet","slowStartRate")]:
        url=f"https://playdeveloperreporting.googleapis.com/v1beta1/apps/{app_pkg}/{group}:query"
        body={"timelineSpec":{"aggregationPeriod":"DAILY","startTime":start,"endTime":end},"metrics":[metric],"pageSize":100}
        if metric=="slowStartRate":body["dimensions"]=["startType"]
        data=requests.post(url,headers=head,json=body,timeout=30)
        if data.status_code in (403,404):
            # Missing permissions/data: NOT zero. Other metric sets still permitted.
            continue
        data.raise_for_status()
        response=data.json()
        out+=google_vitals_data(response,PACKAGE_IDS[app_pkg],metric,day)
        # Detect incomplete paginated provider results instead of treating them as complete.
        if response.get("nextPageToken"):
            raise RuntimeError("Google vitals pagination requires continuation; refusing partial report")
    return out

def main():
    day=(dt.datetime.now(UTC)-dt.timedelta(days=2)).date().isoformat()
    month=day[:7].replace("-", "")
    apple_keys=("APPLE_ASC_ISSUER_ID","APPLE_ASC_KEY_ID","APPLE_ASC_P8_B64","APPLE_ASC_VENDOR_NUMBER")
    # Default off: production Apple reports arrive via canonical AstraLabs
    # Sales ETL and its verified source-to-RUDE database trigger. Never run
    # two separate importers and count the same report as two sales sources.
    if os.environ.get("RUDE_APPLE_LEGACY_IMPORT") == "1" and all(os.environ.get(x) for x in apple_keys):
        try:
            raw=apple_fetch(day)
            data=apple_summary_sales(raw,day,"apple_sales_"+day)
            print("APPLE",provider_ingest("app_store_connect",data))
        except Exception as e:
            print("APPLE ERROR",type(e).__name__,str(e)[:120]);raise
    else: print("APPLE canonical source ETL active; duplicate RUDE Apple fetch disabled")
    google_failures=[]
    authenticated=bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or os.environ.get("GOOGLE_PLAY_SA_JSON_B64"))
    if authenticated and os.environ.get("GOOGLE_PLAY_REPORT_BUCKET"):
        for period in ((dt.date.fromisoformat(day).replace(day=1)-dt.timedelta(days=1)).strftime("%Y%m"),month):
            try:
                imports=google_fetch_installs(period)
                print("GOOGLE INSTALLS",period,provider_ingest("google_play",imports))
                raw=google_fetch_sales(period)
                if raw is not None:
                    data=google_sales_report(raw,"google_sales_"+period)
                    print("GOOGLE SALES",period,provider_ingest("google_play",data))
            except Exception as e:
                print("GOOGLE REPORT ERROR",type(e).__name__,str(e)[:140]);google_failures.append("GCS_"+type(e).__name__)
    else:print("GOOGLE REPORTS SKIPPED: keyless federation or legacy secret not configured")
    if authenticated and os.environ.get("GOOGLE_PLAY_ENABLE_VITALS")=="1":
        try:
            facts=[]
            for pkg in PACKAGE_IDS:facts+=google_fetch_vitals(pkg,day)
            print("GOOGLE VITALS",provider_ingest("google_play",facts))
        except Exception as e:
            print("GOOGLE VITALS ERROR",type(e).__name__,str(e)[:120]);google_failures.append("VITALS_"+type(e).__name__)
    else: print("GOOGLE VITALS SKIPPED: Developer Reporting API/permissions not yet verified")
    if google_failures:
        raise RuntimeError("Verified Google sources unavailable: "+", ".join(google_failures))

if __name__=="__main__":main()