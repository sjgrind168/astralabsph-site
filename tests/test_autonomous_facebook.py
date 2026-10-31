import importlib.util
import os
import unittest
from unittest.mock import patch
from pathlib import Path
from collections import Counter

SCRIPT=Path(__file__).resolve().parents[1]/"marketing/automation/facebook/scripts/daily_two_per_app.py"
spec=importlib.util.spec_from_file_location("editorial",SCRIPT)
editorial=importlib.util.module_from_spec(spec)
spec.loader.exec_module(editorial)


class AutonomousFacebookTests(unittest.TestCase):
    def test_rolling_content_is_unique_factual_and_three_creatives_per_app(self):
        with patch.dict(os.environ, {"ASTRALABS_EDITORIAL_AUTO_REFILL_ENABLED":"true"}):
            bank=editorial.candidates()
        self.assertEqual(len(bank), 36)
        self.assertEqual(len({x["id"] for x in bank}),36)
        slots=Counter((x["publish_day"],x["app"]) for x in bank)
        self.assertTrue(all(v==editorial.TARGET_BY_APP[app] for (_,app),v in slots.items()))
        for day,app in slots:
            creatives=[x["creative"] for x in bank if x["publish_day"]==day and x["app"]==app]
            self.assertEqual(len(set(creatives)),editorial.TARGET_BY_APP[app])
        for row in bank:
            self.assertGreaterEqual(len(row["copy"]),100)
            self.assertFalse(any(s in row["copy"].lower() for s in editorial.DENY))
            media,text=editorial.build_post(row)
            self.assertIn(row["id"],text)
            self.assertIn("www.astralabsph.com",text)
            self.assertTrue(media.endswith(".png"))

    def test_pagination_and_channel_safety(self):
        org="test-org"
        calls=[]
        def fake_query(q):
            calls.append(q)
            if len(calls)==1:
                self.assertIn("endCursor",q)
                return {"posts":{"edges":[{"node":{"id":"first","channelId":"fb123"}}],
                                 "pageInfo":{"hasNextPage":True,"endCursor":"opaque_cursor"}}}
            self.assertIn('after:"opaque_cursor"',q)
            return {"posts":{"edges":[{"node":{"id":"second","channelId":"fb123"}}],
                             "pageInfo":{"hasNextPage":False,"endCursor":"last"}}}
        with patch.object(editorial.fb,"EXPECTED_PAGE_ID","fb123"),patch.object(editorial.fb,"buffer_query",side_effect=fake_query):
            rows=editorial.full_history(org)
        self.assertEqual([r["id"] for r in rows],["first","second"])
        with patch.object(editorial.fb,"EXPECTED_PAGE_ID","fb123"), patch.object(editorial.fb,"buffer_query",return_value={"posts":{"edges":[],"pageInfo":{"hasNextPage":True,"endCursor":""}}}):
            with self.assertRaisesRegex(RuntimeError,"cursor"):
                editorial.full_history(org)

if __name__=="__main__":
    unittest.main()
