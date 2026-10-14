#!/usr/bin/env python3
"""PIREVO Pinterest v3 guard regression tests. No network or publishing."""
import importlib.util
import io
import pathlib
import unittest
from PIL import Image, ImageDraw

ROOT=pathlib.Path(__file__).resolve().parents[3]
SPEC=importlib.util.spec_from_file_location("v3",ROOT/"marketing/pirevo/validate_pinterest_v3.py")
v3=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(v3)

class GateTests(unittest.TestCase):
    def test_full_bleed_photo_texture_passes_preflight(self):
        image=Image.effect_noise((1000,1500),60).convert("RGB")
        zones=v3.thumbnail_photo_coverage(image)
        self.assertEqual(len(zones),6)
        self.assertGreater(min(zones),15)
    def test_old_boxed_layout_rejected(self):
        image=Image.new("RGB",(1000,1500),(248,247,241))
        draw=ImageDraw.Draw(image)
        draw.rectangle((75,105,925,775),fill=(235,230,215))
        draw.rectangle((180,210,820,660),fill=(160,130,105))
        with self.assertRaises(v3.Rejected):
            v3.thumbnail_photo_coverage(image)
    def test_old_renderers_always_quarantined(self):
        v3.check_banned_renderers(ROOT)
    def test_new_manifest_empty_cannot_authorize_posting(self):
        with self.assertRaises(v3.Rejected):
            v3.validate(ROOT,ROOT/"marketing/pirevo/approved_pins_v3.json",True)
    def test_manifest_baseline_ci_passes_without_publish(self):
        v3.validate(ROOT,ROOT/"marketing/pirevo/approved_pins_v3.json",False)

if __name__=="__main__":
    unittest.main(verbosity=2)
