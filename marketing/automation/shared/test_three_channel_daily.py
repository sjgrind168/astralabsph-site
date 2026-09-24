#!/usr/bin/env python3
"""No-network readiness tests: never publish or call Buffer with empty approval ledger."""
import contextlib
import io
import os
import unittest
from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import three_channel_daily as campaign

class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.cfg = campaign.load(campaign.CONFIG)
        self.rows = campaign.source_plan(self.cfg)

    def test_six_per_day_three_each_and_unique_formats(self):
        self.assertEqual(len(self.rows), 42)
        self.assertEqual(len({r["id"] for r in self.rows}), 42)
        for day in range(1, 8):
            for app in campaign.APP_ORDER:
                d = [x for x in self.rows if x["day"] == day and x["app"] == app]
                self.assertEqual(len(d), 3)
                self.assertEqual({x["format"] for x in d}, set(campaign.FORMATS))

    def test_root_tracking_and_reject_subpages(self):
        good = "https://www.astralabsph.com/?utm_source=tiktok&utm_content=S26D1AV&app=astramate"
        self.assertTrue(campaign.valid_root_link(good, "S26D1AV", "Astramate", "tiktok"))
        for bad in (
            good.replace("www.astralabsph.com/", "www.astralabsph.com/astramate/"),
            good.replace("utm_source=tiktok", "utm_source=facebook"),
            good.replace("app=astramate", "app=keepry"),
            good.replace("www.astralabsph.com", "astramate.vercel.app"),
        ):
            self.assertFalse(campaign.valid_root_link(bad, "S26D1AV", "Astramate", "tiktok"))

    def test_all_channels_explicit_release_hold(self):
        self.assertEqual(self.cfg["target"]["all_channels_per_pht_day"], 18)
        self.assertEqual(self.cfg["target"]["per_app_per_channel_per_pht_day"], 3)
        self.assertEqual(campaign.validate_releases("tiktok", self.cfg, self.rows), [])
        self.assertEqual(campaign.validate_releases("pinterest", self.cfg, self.rows), [])

    def test_empty_inventory_never_calls_buffer_even_with_write_flag_on(self):
        for channel in campaign.CHANNELS:
            with mock.patch.dict(os.environ, {
                "ASTRALABS_" + channel.upper() + "_THREE_DAILY_PUBLISH_ENABLED": "true",
                "ASTRALABS_BUFFER_API_KEY": "not-a-real-key",
            }), mock.patch.object(campaign, "module", side_effect=AssertionError("NO BUFFER ALLOWED")):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    campaign.run(channel)
                self.assertIn("HELD_NO_APPROVED_ORIGINAL_MEDIA", buf.getvalue())

    def test_expired_editorial_day_needs_explicit_approved_restage_date(self):
        original = next(r for r in self.rows if r["id"] == "S26D1AV")
        now = datetime(2026, 9, 24, 8, 0, tzinfo=ZoneInfo("Asia/Manila"))
        self.assertIsNone(campaign.scheduled_window(self.cfg, "tiktok", original, now))
        approved = {"publish_date_pht": "2026-09-25"}
        due = campaign.scheduled_window(self.cfg, "tiktok", original, now, approved)
        self.assertEqual(due.strftime("%Y-%m-%d %H:%M"), "2026-09-25 09:45")

    def test_exact_slot_and_no_missed_slots(self):
        now = datetime(2026, 9, 23, 8, 0, tzinfo=ZoneInfo("Asia/Manila"))
        astramate = next(r for r in self.rows if r["id"] == "S26D1AV")
        due = campaign.scheduled_window(self.cfg, "tiktok", astramate, now)
        self.assertEqual(due.strftime("%H:%M"), "09:45")
        late = datetime(2026, 9, 23, 9, 30, tzinfo=ZoneInfo("Asia/Manila"))
        self.assertIsNone(campaign.scheduled_window(self.cfg, "tiktok", astramate, late))

if __name__ == "__main__":
    unittest.main()
