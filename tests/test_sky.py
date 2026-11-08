"""Regression coverage for local astronomy, including DST and polar days."""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from daylight_ui.sky import calculate_sun, calculate_moon, NEW_MOON_EPOCH, SYNODIC_MONTH


class SolarEstimates(unittest.TestCase):
    def test_equator_equinox(self):
        result = calculate_sun(date(2026, 3, 20), 0, 0, "UTC")
        self.assertIsNone(result["polar_state"])
        self.assertAlmostEqual(result["day_length_hours"], 12.11, delta=0.08)
        self.assertTrue(5 <= result["sunrise"].hour <= 6)
        self.assertTrue(18 <= result["sunset"].hour <= 19)

    def test_swiss_summer_winter_and_dst(self):
        summer = calculate_sun(date(2026, 6, 21), 46.8, 7.15, "Europe/Zurich")
        winter = calculate_sun(date(2026, 12, 21), 46.8, 7.15, "Europe/Zurich")
        self.assertGreater(summer["day_length_hours"], 15.5)
        self.assertLess(winter["day_length_hours"], 9)
        self.assertEqual(summer["sunrise"].utcoffset(), timedelta(hours=2))
        self.assertEqual(winter["sunrise"].utcoffset(), timedelta(hours=1))
        self.assertEqual(summer["sunrise"].date(), date(2026, 6, 21))
        self.assertEqual(summer["sunset"].date(), date(2026, 6, 21))

    def test_dst_transition_uses_event_offset(self):
        before = calculate_sun(date(2026, 3, 28), 46.8, 7.15, "Europe/Zurich")
        after = calculate_sun(date(2026, 3, 29), 46.8, 7.15, "Europe/Zurich")
        self.assertEqual(before["sunrise"].utcoffset(), timedelta(hours=1))
        self.assertEqual(after["sunrise"].utcoffset(), timedelta(hours=2))

    def test_polar_day_night(self):
        for latitude, summer_month, winter_month in [(78, 6, 12), (-78, 12, 6), (90, 6, 12), (-90, 12, 6)]:
            summer = calculate_sun(date(2026, summer_month, 21), latitude, 0, "UTC")
            winter = calculate_sun(date(2026, winter_month, 21), latitude, 0, "UTC")
            self.assertEqual(summer["polar_state"], "polar_day")
            self.assertEqual(summer["day_length_hours"], 24)
            self.assertEqual(winter["polar_state"], "polar_night")
            self.assertEqual(winter["day_length_hours"], 0)
            self.assertIsNone(summer["sunset"])
            self.assertIsNone(winter["sunrise"])

    def test_dateline_and_explicit_timezone(self):
        for lon, zone in [(179, "Pacific/Auckland"), (-179, "Pacific/Honolulu"), (179, "Pacific/Honolulu")]:
            result = calculate_sun(date(2026, 4, 12), 0, lon, zone)
            self.assertEqual(result["solar_noon"].date(), date(2026, 4, 12))
            self.assertGreater(result["sunset"].astimezone(timezone.utc), result["sunrise"].astimezone(timezone.utc))

    def test_invalid_input(self):
        for lat, lon in [(91, 0), (0, 181), (float("nan"), 0), (0, float("inf"))]:
            with self.assertRaises(ValueError):
                calculate_sun(date(2026, 1, 1), lat, lon, "UTC")
        for zone in ["Not/AZone", "/etc/passwd", None]:
            with self.assertRaises(ValueError):
                calculate_sun(date(2026, 1, 1), 0, 0, zone)
        with self.assertRaises(ValueError):
            calculate_sun(date(1800, 1, 1), 0, 0, "UTC")


class LunarEstimates(unittest.TestCase):
    def test_reference_new_moon(self):
        result = calculate_moon(NEW_MOON_EPOCH)
        self.assertAlmostEqual(result["phase_fraction"], 0)
        self.assertAlmostEqual(result["illumination"], 0)
        self.assertEqual(result["phase_name"], "New moon")
        self.assertTrue(result["approximate"])

    def test_half_cycle_is_full(self):
        full = NEW_MOON_EPOCH + timedelta(days=SYNODIC_MONTH / 2)
        result = calculate_moon(full)
        self.assertAlmostEqual(result["phase_fraction"], 0.5)
        self.assertAlmostEqual(result["illumination"], 1)
        self.assertEqual(result["phase_name"], "Full moon")
        self.assertGreater(result["next_full_moon"], full)

    def test_next_full_is_future_and_bounded(self):
        for d in [date(1900, 1, 1), date(2000, 1, 1), date(2026, 11, 8), date(2100, 12, 1)]:
            result = calculate_moon(d)
            delay = (result["next_full_moon"] - result["sampled_at"]).total_seconds() / 86400
            self.assertTrue(0 < delay <= SYNODIC_MONTH)
            self.assertTrue(0 <= result["illumination"] <= 1)
            self.assertTrue(0 <= result["phase_fraction"] < 1)

    def test_naive_datetime_rejected(self):
        with self.assertRaises(ValueError):
            calculate_moon(datetime(2026, 1, 1))


if __name__ == "__main__":
    unittest.main()
