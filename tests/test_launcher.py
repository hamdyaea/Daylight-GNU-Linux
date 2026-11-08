#!/usr/bin/env python3
"""Freedesktop launcher parsing and atomic desktop preference regressions.

SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from daylight_ui import launcher, state


class DesktopEntries(unittest.TestCase):
    def test_field_codes_and_literal_shell_syntax(self):
        command = launcher.exec_arguments('/bin/echo "two words" %i %c %k %% %U "$(touch /tmp/no)"',
                                          "Demo", "demo-icon", "/tmp/demo.desktop")
        self.assertEqual(command, ("/bin/echo", "two words", "--icon", "demo-icon", "Demo",
                                   "/tmp/demo.desktop", "%", "$(touch /tmp/no)"))

    def test_reject_unknown_and_embedded_file_codes(self):
        for value in ("", "/bin/echo %Z", "/bin/echo prefix%F", "/bin/echo trailing%"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                launcher.exec_arguments(value, "App", "", "/tmp/a.desktop")

    def test_user_masking_localization_and_visibility(self):
        with tempfile.TemporaryDirectory() as temporary:
            own, system = Path(temporary)/"own", Path(temporary)/"system"
            own.mkdir(); system.mkdir()
            base = "[Desktop Entry]\nType=Application\nName=Tool\nName[fr]=Outil\nExec=/bin/echo %U\n"
            (system/"masked.desktop").write_text(base)
            (own/"masked.desktop").write_text("[Desktop Entry]\nHidden=true\n")
            (system/"tool.desktop").write_text(base+"OnlyShowIn=Daylight;Fluxbox;\n")
            (system/"hidden.desktop").write_text(base+"NoDisplay=true\n")
            (system/"other.desktop").write_text(base+"OnlyShowIn=GNOME;\n")
            (system/"excluded.desktop").write_text(base+"NotShowIn=Fluxbox;\n")
            (system/"missing.desktop").write_text(base+"TryExec=/nonexistent/not-a-program\n")
            found = launcher.discover([own,system],language="fr",desktop="Daylight:Fluxbox")
            self.assertEqual([app.identifier for app in found], ["tool.desktop"])
            self.assertEqual(found[0].name,"Outil")
            self.assertEqual(found[0].argv,("/bin/echo",))

    def test_invalid_file_is_skipped(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)
            (directory/"bad.desktop").write_text("not an ini file")
            self.assertEqual(launcher.discover([directory]),[])


class Preferences(unittest.TestCase):
    def test_core_change_preserves_newer_keys(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{"XDG_CONFIG_HOME":temporary}):
            directory=state.directory(); directory.mkdir()
            (directory/"settings.conf").write_text("# existing\nmonitor=on\nfuture_key=keep\n")
            state.save_core({"monitor":"off","profile":"minimal"})
            self.assertIn("future_key=keep",(directory/"settings.conf").read_text())
            self.assertEqual(state.read_core()["monitor"],"off")
            self.assertEqual(state.read_core()["profile"],"minimal")

    def test_unknown_core_values_rejected(self):
        with self.assertRaises(ValueError): state.save_core({"wallpaper":"../../etc/passwd"})

    def test_invalid_json_defaults_and_atomic_preferences(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{"XDG_CONFIG_HOME":temporary}):
            directory=state.directory(); directory.mkdir()
            (directory/"ui.json").write_text("invalid")
            self.assertEqual(state.load_ui()["language"],"en")
            state.save_ui({"language":"fr","welcome_completed":True})
            self.assertTrue(state.load_ui()["welcome_completed"])
            self.assertEqual(state.load_ui()["language"],"fr")
            self.assertEqual((directory/"ui.json").stat().st_mode & 0o777,0o600)

    def test_keyboard_choice_is_retained(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,{"XDG_CONFIG_HOME":temporary}):
            self.assertEqual(state.load_ui()["keyboard_layout"],"")
            state.save_ui({"keyboard_layout":"ch","keyboard_variant":"fr"})
            self.assertEqual(state.load_ui()["keyboard_layout"],"ch")
            self.assertEqual(state.load_ui()["keyboard_variant"],"fr")
            with self.assertRaises(ValueError):
                state.save_ui({"keyboard_variant":"unsupported"})

    def test_inherited_or_invalid_keyboard_never_executes(self):
        with patch.object(state.subprocess,"run") as run:
            for values in ({}, {"keyboard_layout":"","keyboard_variant":""},
                           {"keyboard_layout":"$(id)","keyboard_variant":""},
                           {"keyboard_layout":"ch","keyboard_variant":"bad"}):
                self.assertFalse(state.apply_keyboard(values))
            run.assert_not_called()

    def test_explicit_keyboard_uses_argument_list(self):
        with patch.object(state.shutil,"which",return_value="/usr/bin/setxkbmap"), \
             patch.object(state.subprocess,"run") as run:
            run.return_value.returncode=0
            self.assertTrue(state.apply_keyboard({"keyboard_layout":"ch","keyboard_variant":"fr"}))
            self.assertEqual(run.call_args.args[0],["/usr/bin/setxkbmap","-layout","ch","-variant","fr"])


if __name__=="__main__":
    unittest.main(verbosity=2)
