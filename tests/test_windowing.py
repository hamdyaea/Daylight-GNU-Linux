#!/usr/bin/env python3
"""Tk wrapper ordering and dialog semantics on a disposable X11 display."""
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
UI = Path(os.environ.get("DAYLIGHT_UI_ROOT", ROOT / "desktop"))
sys.path.insert(0, str(UI))
from daylight_ui import windowing

try:
    import tkinter as tk
    from tkinter import filedialog
except ImportError:
    tk = None


class WindowingGuards(unittest.TestCase):
    def test_only_linux_wayland_with_xwayland_display_is_enabled(self):
        good = {"XDG_SESSION_TYPE": "wayland", "DISPLAY": ":77"}
        self.assertTrue(windowing.enabled(good, "linux"))
        for environment, platform in (({}, "linux"),
                                      ({"DISPLAY": ":77", "XDG_SESSION_TYPE": "x11"}, "linux"),
                                      ({"XDG_SESSION_TYPE": "wayland"}, "linux"),
                                      (good, "darwin")):
            self.assertFalse(windowing.enabled(environment, platform))


@unittest.skipUnless(tk is not None and os.environ.get("DISPLAY"),
                     "Requires Tk and a disposable display")
class WindowingDialogs(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.addCleanup(self.root.destroy)
        with patch.object(windowing, "enabled", return_value=True):
            self.assertTrue(windowing.prepare(self.root))

    def test_root_is_unmapped_until_complete_then_maps_normally(self):
        self.assertEqual(self.root.state(), "withdrawn")
        self.assertFalse(self.root.winfo_ismapped())
        self.assertFalse(self.root.overrideredirect())
        tk.Label(self.root, text="Completed interface").pack()
        windowing.finish(self.root)
        self.root.update()
        self.assertTrue(self.root.winfo_ismapped())
        self.assertFalse(self.root.overrideredirect())

    def test_toplevel_preserves_transient_type_grab_and_explicit_withdrawal(self):
        windowing.finish(self.root)
        self.root.update()
        dialog = tk.Toplevel(self.root)
        self.assertFalse(dialog.winfo_ismapped())
        self.assertFalse(dialog.overrideredirect())
        dialog.transient(self.root)
        dialog.wm_attributes("-type", "dialog")
        tk.Text(dialog).pack()
        self.root.update()
        self.assertTrue(dialog.winfo_ismapped())
        self.assertEqual(str(dialog.transient()), str(self.root))
        self.assertIn("dialog", dialog.wm_attributes("-type"))
        dialog.grab_set()
        self.assertIs(self.root.grab_current(), dialog)
        dialog.grab_release()
        dialog.destroy()
        hidden = tk.Toplevel(self.root)
        hidden.withdraw()
        self.root.update()
        self.assertEqual(hidden.state(), "withdrawn")
        self.assertFalse(hidden.winfo_ismapped())
        hidden.destroy()

    def test_native_tk_file_dialog_uses_prepared_toplevel_and_can_cancel(self):
        windowing.finish(self.root)
        self.root.update()
        observed = []
        errors = []

        def cancel():
            path = ".__tk_filedialog"
            try:
                self.assertTrue(self.root.tk.call("winfo", "exists", path))
                self.assertFalse(self.root.tk.getboolean(self.root.tk.call("wm", "overrideredirect", path)))
                observed.append(path)
                self.root.tk.call("::tk::dialog::file::CancelCmd", path)
            except BaseException as error:
                errors.append(error)
                self.root.tk.call("set", "::tk::Priv(selectFilePath)", "")

        self.root.after(250, cancel)
        selected = filedialog.askopenfilename(parent=self.root, initialdir="/tmp")
        self.assertFalse(selected)
        self.assertEqual(observed, [".__tk_filedialog"])
        self.assertEqual(errors, [])

    def test_shardturn_help_is_complete_and_viewable_before_grab(self):
        import shardturn_launcher
        root, app = shardturn_launcher.create_app(seed=42)
        self.addCleanup(app.close)
        root.update()
        original = tk.Frame.grab_set
        attempts = []

        def visible_grab(dialog):
            attempts.append(dialog)
            self.assertTrue(dialog.winfo_viewable())
            self.assertIsInstance(dialog, tk.Frame)
            text = next(widget for widget in dialog.winfo_children() if isinstance(widget, tk.Text))
            self.assertIn("Shardturn", text.get("1.0", "end"))
            return original(dialog)

        with patch.object(tk.Frame, "grab_set", visible_grab):
            app.show_help()
        self.assertEqual(len(attempts), 1)
        self.assertIs(root.grab_current(), app.help_window)
        self.assertTrue(app.help_window.winfo_viewable())
        self.assertFalse(any(isinstance(child, tk.Toplevel) for child in root.winfo_children()))
        text = next(widget for widget in app.help_window.winfo_children() if isinstance(widget, tk.Text))
        # A real WM may still focus this test's other Tk interpreter. Deliver
        # Escape from the focused help text, as a user would press the key.
        text.focus_force()
        root.update()
        self.assertIs(root.focus_get(), text)
        text.event_generate("<Escape>", when="tail")
        root.update()
        self.assertIsNone(app.help_window)
        self.assertIsNone(root.grab_current())

    def test_shardturn_help_does_not_swallow_other_grab_errors(self):
        import shardturn_launcher
        root, app = shardturn_launcher.create_app(seed=42)
        self.addCleanup(app.close)
        root.update()
        with patch.object(tk.Frame, "grab_set", side_effect=tk.TclError("another grab error")):
            with self.assertRaisesRegex(tk.TclError, "another grab error"):
                app.show_help()
        self.assertIsNone(app.help_window)


if __name__ == "__main__":
    unittest.main()
