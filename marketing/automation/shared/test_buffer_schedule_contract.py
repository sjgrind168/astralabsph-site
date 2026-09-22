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
