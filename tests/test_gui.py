#!/usr/bin/env python3
"""Exercise the actual native pages in an isolated desktop.

Copyright (C) 2026 Hamdy Abou El Anein — GPL-3.0-only.
No APT operation, network probe, speech output or real user preferences.
"""
import contextlib
import io
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
UI = Path(os.environ.get("DAYLIGHT_UI_ROOT", ROOT / "desktop"))
if not (UI / "daylight_ui").is_dir():
    UI = Path("/usr/share/daylight/ui")
sys.path.insert(0, str(UI))

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    tk = None


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


@unittest.skipUnless(tk is not None and os.environ.get("DISPLAY"), "Requires Tk and a disposable display")
class NativeDesktop(unittest.TestCase):
    def setUp(self):
        from daylight_ui.shell import Desktop
        self.preferences = tempfile.TemporaryDirectory(prefix="daylight-ui-test-")
        self.environment = mock.patch.dict(os.environ, XDG_CONFIG_HOME=self.preferences.name)
        self.environment.start()
        self.errors = []
        self.root = Desktop()
        self.root.report_callback_exception = lambda kind, error, trace: self.errors.append(str(error))
        self.root.update()

    def tearDown(self):
        try:
            self.root.destroy()
        finally:
            self.environment.stop()
            self.preferences.cleanup()
        self.assertEqual(self.errors, [])

    def page(self, name):
        # A traceback must fail this check even when the shell shows a friendly
        # recovery screen instead of propagating the exception.
        trace = io.StringIO()
        with contextlib.redirect_stderr(trace):
            self.root.show(name)
            self.root.update()
        self.assertNotIn("Traceback", trace.getvalue(), trace.getvalue())
        return self.root.content.winfo_children()[0]

    def button(self, parent, text):
        return next(w for w in descendants(parent)
                    if isinstance(w, (ttk.Button, tk.Button)) and str(w.cget("text")) == text)

    def pump(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.root.update()
            time.sleep(.01)

    def test_every_route_opens_at_desktop_and_small_screen_sizes(self):
        from daylight_ui.shell import GAME_NAMES, TOOL_NAMES
        for geometry in ("1060x760", "800x600"):
            self.root.geometry(geometry)
            for name in ("home", "apps", "games", "settings", "welcome", "telemetry", "launcher",
                         *TOOL_NAMES, *GAME_NAMES):
                with self.subTest(geometry=geometry, application=name):
                    page = self.page(name)
                    self.assertTrue(page.winfo_exists())
                    self.assertGreater(len(list(descendants(self.root.content))), 1)

    def test_memory_cards_receive_real_canvas_clicks(self):
        page = self.page("memory")
        box = page.cv.bbox("memory-0")
        self.assertIsNotNone(box)
        page.cv.event_generate("<Motion>", x=(box[0] + box[2]) // 2, y=(box[1] + box[3]) // 2)
        page.cv.event_generate("<Button-1>", x=(box[0] + box[2]) // 2, y=(box[1] + box[3]) // 2)
        self.root.update()
        self.assertEqual(page.memory.open, [0])
        self.assertGreater(len(page.cv.find_all()), 16)

    def test_battle_button_keeps_each_tie_and_collect_step(self):
        from daylight_ui.game_models import Battle, Card
        page = self.page("cards")
        page.battle = Battle(hands=(
            [Card(8, "♣"), Card(2, "♣"), Card(14, "♠"), Card(3, "♦")],
            [Card(8, "♥"), Card(4, "♥"), Card(13, "♥"), Card(5, "♦")]))
        page.next_battle.invoke()
        self.assertEqual(page.battle.phase, "battle")
        self.assertEqual(page.next_battle.cget("text"), "Continue battle")
        page.next_battle.invoke()
        self.assertEqual(page.battle.phase, "collect")
        self.assertEqual(len(page.battle.pot), 6)
        self.assertIn("6", page.next_battle.cget("text"))
        page.next_battle.invoke()
        self.assertEqual(page.battle.phase, "ready")
        self.assertEqual(page.battle.card_count(), 8)

    def test_temperature_rejects_nonfinite_input_in_window(self):
        page = self.page("temperature")
        entry = next(w for w in descendants(page) if isinstance(w, ttk.Entry))
        entry.delete(0, "end")
        entry.insert(0, "NaN")
        self.button(page, "Convert").invoke()
        self.assertTrue(any("finite number" in str(w.cget("text"))
                            for w in descendants(page) if isinstance(w, ttk.Label)))

    def test_timer_cancel_disarms_bell_and_navigation_cleans_callbacks(self):
        from daylight_ui import tools
        with mock.patch.object(tools.Page, "bell") as bell:
            page = self.page("alarm")
            entry = next(w for w in descendants(page) if isinstance(w, ttk.Entry))
            entry.delete(0, "end")
            entry.insert(0, "0.02")
            self.button(page, "Start new timer").invoke()
            self.button(page, "Cancel").invoke()
            self.pump(1.35)
            bell.assert_not_called()
            self.assertTrue(any("cancelled" in str(w.cget("text"))
                                for w in descendants(page) if isinstance(w, ttk.Label)))
            self.page("home")
            self.pump(.25)
            self.assertTrue(page._closed)
            self.assertEqual(page.jobs, set())

    def test_speech_stop_and_page_close_terminate_only_owned_child(self):
        from daylight_ui import tools
        class Speech:
            def __init__(self):
                self.returncode = None
                self.done = threading.Event()
            def poll(self):
                return self.returncode
            def communicate(self, data):
                self.done.wait(3)
            def terminate(self):
                self.returncode = -15
                self.done.set()
            def wait(self, timeout=None):
                self.done.wait(timeout)
                return self.returncode
            def kill(self):
                self.terminate()
        page = self.page("speech")
        child = Speech()
        # Patch only while the user action starts. Nothing executes or speaks.
        with mock.patch.object(tools.shutil, "which", return_value="/usr/bin/espeak-ng"), \
                mock.patch.object(tools.subprocess, "Popen", return_value=child):
            self.button(page, "Read aloud").invoke()
        self.assertIs(page.speech_process, child)
        self.button(page, "Stop").invoke()
        self.assertIsNone(page.speech_process)
        self.assertIsNotNone(child.poll())
        self.page("home")


if __name__ == "__main__":
    unittest.main(verbosity=2)
