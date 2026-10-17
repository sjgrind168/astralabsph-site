import importlib.util,io,gzip,zipfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location("rudeprovider",Path(__file__).with_name("sync.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

class OfficialProviderReportTests(unittest.TestCase):
    def test_apple_paid_iap_and_free_download_separate(self):
        header="Apple Identifier\tProduct Type Identifier\tUnits\tCustomer Price\tCustomer Currency\tDeveloper Proceeds\tCurrency of Proceeds\n"
        rows="6812828056\tIA1\t2\t5.99\tUSD\t4.50\tUSD\n6813155959\t1F\t4\t0\tUSD\t0\tUSD\n"
        out=m.apple_summary_sales(gzip.compress((header+rows).encode()),"2026-10-15","test-apple")
        self.assertEqual(len([x for x in out if x["app_key"]=="keepry"]),0)
        self.assertEqual(next(x["metric_value"] for x in out if x["metric"]=="paid_units"),2)
        self.assertEqual(next(x["metric_value"] for x in out if x["category"]=="gross_sales"),11.98)
        self.assertEqual(next(x["metric_value"] for x in out if x["category"]=="developer_proceeds"),9)
    def test_apple_refunds_preserve_sign_and_distinct_currency(self):
        header="Apple Identifier\tProduct Type Identifier\tUnits\tCustomer Price\tCustomer Currency\tDeveloper Proceeds\tCurrency of Proceeds\n"
        rows="6812828056\tIA1\t-1\t-2.99\tUSD\t2.50\tUSD\n6812828056\tIA1\t2\t4.99\tEUR\t3.00\tEUR\n"
        out=m.apple_summary_sales((header+rows).encode(),"2026-10-14","report")
        gross=[x for x in out if x["category"]=="gross_sales"]
        self.assertEqual(set(x["metric_unit"] for x in gross),{"USD","EUR"})
        self.assertEqual(next(x["metric_value"] for x in gross if x["metric_unit"]=="USD"),-2.99)
        self.assertEqual(next(x["metric_value"] for x in out if x["metric"]=="refunded_units"),1)
    def test_no_account_wide_apple_fallback(self):
        header="Apple Identifier\tProduct Type Identifier\tUnits\tCustomer Price\tCustomer Currency\tDeveloper Proceeds\tCurrency of Proceeds\n"
        out=m.apple_summary_sales((header+"999999999\tIA1\t5\t6\tUSD\t4\tUSD\n").encode(),"2026-10-15","report")
        self.assertEqual(out,[])
    def test_google_csv_uses_package_and_buyer_currency(self):
        header="Order Number,Order Charged Date,Financial Status,Package ID,Currency of Sale,Charged Amount,SKU ID\n"
        body="GPA.1,2026-10-14,charged,com.astralabs.keepry,USD,4.79,lifetime\nGPA.2,2026-10-14,charged,com.astralabs.astramate,PHP,199.00,premium\n"
        raw=io.BytesIO()
        with zipfile.ZipFile(raw,"w") as z:z.writestr("estimated.csv",(header+body).encode('utf-16'))
        out=m.google_sales_report(raw.getvalue(),"test-report")
        self.assertEqual(len([x for x in out if x['category']=='purchases']),2)
        self.assertEqual(next(x['metric_value'] for x in out if x['app_key']=='keepry' and x['category']=='gross_sales'),4.79)
        self.assertEqual(next(x['metric_unit'] for x in out if x['app_key']=='astramate' and x['category']=='gross_sales'),'PHP')
    def test_google_refund_not_a_purchase(self):
        header="Order Number,Order Charged Date,Financial Status,Package ID,Currency of Sale,Charged Amount\n"
        body="GPA.1,2026-10-14,refund,com.astralabs.keepry,USD,4.79\n"
        raw=io.BytesIO()
        with zipfile.ZipFile(raw,'w') as z:z.writestr('sales.csv',(header+body).encode('utf-8'))
        out=m.google_sales_report(raw.getvalue(),'report')
        self.assertFalse(any(x['metric']=='charged_orders' for x in out))
        self.assertEqual(next(x['metric_value'] for x in out if x['metric']=='refund_events'),1)
    def test_vitals_no_missing_data_as_zero(self):
        self.assertEqual(m.google_vitals_data({'rows':[]},'keepry','crashRate','2026-10-14'),[])
    def test_vitals_source_decimal_and_period(self):
        response={'rows':[{'startTime':{'year':2026,'month':10,'day':14},'metrics':[{'metric':'crashRate','decimalValue':{'value':'0.014'}}]}]}
        out=m.google_vitals_data(response,'keepry','crashRate','2026-10-14')
        self.assertEqual(out[0]['metric_unit'],'SOURCE_DECIMAL')
        self.assertEqual(out[0]['metric_value'],0.014)
        self.assertEqual(out[0]['period_end'],'2026-10-14')
    def test_ingest_keys_stable_on_rerun(self):
        a=m.source_key('google_play','keepry','purchases','orders','COUNT','2026-10-14','sales-202610')
        b=m.source_key('google_play','keepry','purchases','orders','COUNT','2026-10-14','sales-202610')
        self.assertEqual(a,b)

if __name__=='__main__':unittest.main()
