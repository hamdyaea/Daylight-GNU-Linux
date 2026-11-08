"""Pure parser regression tests for optional Linux measurements."""
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from daylight_ui import diagnostics as d


class Diagnostics(unittest.TestCase):
    def test_memory_uses_available_and_clamps(self):
        self.assertEqual(d.memory_values("MemTotal: 1000 kB\nMemFree: 20 kB\nMemAvailable: 400 kB"),
                         (1024000, 614400))
        self.assertEqual(d.memory_values("MemTotal: 10 kB\nMemAvailable: 20 kB"), (10240, 0))

    def test_cpu_excludes_duplicate_guest(self):
        self.assertEqual(d.cpu_times("cpu 10 0 20 40 5 3 2 0 10 0"), (80, 45))
        self.assertEqual(d.cpu_percent((100, 50), (200, 75)), 75.0)
        self.assertIsNone(d.cpu_percent((100, 50), (99, 51)))

    def test_throttle_current_and_history_are_separate(self):
        state = d.throttle_status("throttled=0x50001")
        self.assertEqual(state["current"], ["Undervoltage"])
        self.assertEqual(state["history"], ["Undervoltage", "Thermal/power throttling"])
        self.assertEqual(d.throttle_status("throttled=0x0")["current"], [])
        self.assertIsNone(d.throttle_status("Permission denied"))

    def test_soc_temperature_is_preferred(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, kind, value in [(0, "acpitz", "20000"), (1, "cpu-thermal", "55000")]:
                folder = root / f"thermal_zone{index}"
                folder.mkdir()
                (folder / "type").write_text(kind)
                (folder / "temp").write_text(value)
            self.assertEqual(d.thermal_reading(root), 55.0)


if __name__ == "__main__":
    unittest.main()
