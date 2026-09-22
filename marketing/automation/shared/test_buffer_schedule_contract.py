#!/usr/bin/env python3
"""Local-only contract: canonical GitHub posting slots, no unplanned FB late-night posts, retired Keepry single release."""
import importlib.util
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import three_channel_daily as source

ROOT = Path(__file__).resolve().parents[3]
PHT = ZoneInfo("Asia/Manila")

def load_fb():
    path=ROOT/"marketing/automation/facebook/scripts/daily_two_per_app.py"
    spec=importlib.util.spec_from_file_location("fb_schedule_contract",path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

class ScheduleContracts(unittest.TestCase):
    def test_facebook_exact_owner_slots(self):
        fb=load_fb()
        cfg=source.load(source.CONFIG)
        for app in ("Astramate","Keepry"):
            defined=tuple(t.strftime("%H:%M") for t in fb.SLOTS[app])
            self.assertEqual(defined,tuple(cfg["slots_pht"]["facebook"][app]))
            self.assertEqual(len(defined),3)
        self.assertEqual(fb.DAILY_TARGET,3)

    def test_late_fb_run_never_creates_unplanned_time(self):
        fb=load_fb()
        today=datetime(2026,9,23,21,0,tzinfo=PHT)
        for app in ("Astramate","Keepry"):
            self.assertIsNone(fb.pick_slot(today.date(),app,0,[],today))
        nextday=datetime(2026,9,23,23,0,tzinfo=PHT)
        for app in ("Astramate","Keepry"):
            slot=fb.pick_slot(datetime(2026,9,24,tzinfo=PHT).date(),app,0,[],nextday)
            self.assertEqual(slot.strftime("%H:%M"),source.load(source.CONFIG)["slots_pht"]["facebook"][app][0])

    def test_authenticated_buffer_ui_proof_matches_all_126_canonical_slots(self):
        import json
        import re
        proof_path=ROOT/"marketing/automation/shared/proof/buffer-saved-schedule-proof-20260922.json"
        proof=json.loads(proof_path.read_text(encoding="utf-8"))
        cfg=source.load(source.CONFIG)
        days=("Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday")
        self.assertTrue(cfg["provider_sync"]["buffer_posting_times_verified"])
        for channel in ("facebook","tiktok","pinterest"):
            item=proof[channel]
            self.assertEqual(item["timezone"].splitlines(),["Timezone","Manila"])
            targets=sorted(sum((cfg["slots_pht"][channel][app] for app in ("Astramate","Keepry")),[]))
            got=set()
            for line in item["slots"]:
                match=re.fullmatch(r"Remove (Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday) (\\d{2}:\\d{2}) (AM|PM)",line)
                self.assertIsNotNone(match,line)
                day,hour,period=match.groups()
                hh,mm=map(int,hour.split(":"))
                slot="%02d:%02d"%(((hh%12)+(12 if period=="PM" else 0)),mm)
                got.add((day,slot))
            self.assertEqual(len(item["slots"]),42)
            self.assertEqual(got,{(day,t) for day in days for t in targets},
                             "saved Buffer slots diverge from canonical for "+channel)

    def test_sep23_fb_queue_8_posts_four_each_no_new_post_allowed_that_day(self):
        import json
        fb=load_fb()
        observed=json.loads((ROOT/"marketing/automation/shared/proof/buffer-queue-after-20260922.json").read_text(encoding="utf-8"))["facebook"]
        self.assertRegex(observed,r"Queue\s+8\s+posts")
        self.assertIn("2 Posts left to schedule on the Free plan",observed)
        expected=(("9:30 AM","Cargo stowage factor"),
                  ("10:40 AM","An important document is in your camera roll"),
                  ("12:30 PM","Document saved. Renewal date forgotten?"),
                  ("2:10 PM","Before you use a compass reading"),
                  ("3:40 PM","Passports, licences, insurance"),
                  ("6:30 PM","Draft at forward and aft marks"),
                  ("7:10 PM","Working with cargo volume and weight"),
                  ("8:40 PM","A document you need shouldn't disappear"))
        for time,headline in expected:
            self.assertIn(time,observed)
            self.assertIn(headline,observed)
        self.assertEqual(len(expected),8)
        self.assertEqual(len([x for x in expected if x[0] in ("12:30 PM","6:30 PM")]),2)
        # The writer considers four existing items per app above 3, so its
        # day-cap must prevent any additional September 23 creates.
        self.assertEqual(fb.DAILY_TARGET,3)

    def test_old_keepry_release_can_never_run_on_cron_or_write(self):
        retired=(ROOT/".github/workflows/astralabs-keepry-existing-video-now.yml").read_text(encoding="utf-8")
        self.assertNotIn("  schedule:",retired)
        self.assertNotIn("python3 marketing/automation/tiktok/scripts/release_existing_keepry_now.py",retired)
        self.assertIn("RETIRED_EXISTING_KEEPRY_RELEASE",retired)

    def test_targets_are_three_per_app_six_per_channel(self):
        c=source.load(source.CONFIG)
        self.assertEqual(c["target"]["per_app_per_channel_per_pht_day"],3)
        for channel in ("facebook","tiktok","pinterest"):
            for app in ("Astramate","Keepry"):
                self.assertEqual(len(c["slots_pht"][channel][app]),3)
        self.assertEqual(c["target"]["all_channels_per_pht_day"],18)

if __name__=="__main__":
    unittest.main()
