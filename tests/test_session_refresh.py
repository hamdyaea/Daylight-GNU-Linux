#!/usr/bin/env python3
"""A running RC3 session can safely acquire one RC4 appearance owner.

SPDX-License-Identifier: GPL-3.0-only
"""
from pathlib import Path
import os
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from daylight_ui import state


class SessionRefresh(unittest.TestCase):
    def environment(self, **changes):
        return dict({"DAYLIGHT_SESSION":"1", "DISPLAY":":55", "XDG_SESSION_TYPE":"x11",
                     "XDG_SESSION_ID":"test-daylight"}, **changes)

    def snapshot(self, args=None, **changes):
        value={"pid":12345, "uid":os.getuid(), "started":5678,
               "args":args or ["/usr/bin/conky","-c",str(state.directory()/"conky.conf")],
               "environment":self.environment()}
        value.update(changes)
        return value

    def test_bootstrap_guard(self):
        good=self.environment()
        self.assertTrue(state.daylight_session(good,1000))
        self.assertFalse(state.daylight_session(good,0))
        self.assertFalse(state.daylight_session({"DISPLAY":":55"},1000))
        self.assertFalse(state.daylight_session({"DAYLIGHT_SESSION":"1"},1000))
        with patch.dict(os.environ,{},clear=True), patch.object(state.subprocess,"Popen") as spawn:
            self.assertFalse(state.ensure_session_manager())
            spawn.assert_not_called()

    def test_file_lock_is_authoritative_and_display_scoped(self):
        with tempfile.TemporaryDirectory() as temporary, patch.dict(os.environ,self.environment(
                XDG_RUNTIME_DIR=temporary,XDG_CONFIG_HOME=temporary),clear=True), \
                patch.object(state.os,"geteuid",return_value=1000), \
                patch.object(state.subprocess,"Popen") as spawn:
            descriptor=state.acquire_session_lock()
            self.assertIsNotNone(descriptor)
            try:
                self.assertIsNone(state.acquire_session_lock())
                self.assertFalse(state.ensure_session_manager())
                spawn.assert_not_called()
                other=state.acquire_session_lock(self.environment(DISPLAY=":56",XDG_RUNTIME_DIR=temporary))
                self.assertIsNotNone(other)
                os.close(other)
            finally:
                os.close(descriptor)
            self.assertTrue(state.ensure_session_manager())
            self.assertEqual(spawn.call_args.args[0][-1],"--session-appearance")

    def test_only_exact_same_user_same_display_daylight_children_qualify(self):
        environment=self.environment()
        good=self.snapshot()
        self.assertEqual(state.legacy_process_kind(good,environment),"conky")
        for change in ({"uid":os.getuid()+1},
                       {"environment":self.environment(DISPLAY=":56")},
                       {"environment":self.environment(DAYLIGHT_SESSION="0")},
                       {"environment":self.environment(XDG_SESSION_ID="another")},
                       {"args":["conky","-c","/home/other/conky.conf"]},
                       {"args":["conky","-c",str(state.directory()/"conky.conf"),"--config=/other"]},
                       {"args":["waybar"]}, {"args":["rpi-connect"]}):
            with self.subTest(change=change):
                self.assertIsNone(state.legacy_process_kind(self.snapshot(**change),environment))

    def test_wayland_exact_legacy_paths_and_runtime(self):
        environment=self.environment(XDG_SESSION_TYPE="wayland",WAYLAND_DISPLAY="wayland-0",XDG_RUNTIME_DIR="/run/user/1000")
        conky=self.snapshot(args=["conky","-c","/usr/share/daylight/labwc/conky.lua"],environment=environment)
        background=self.snapshot(args=["swaybg","-m","fill","-i","/usr/share/backgrounds/daylight/daylight-mountains.jpg"],environment=environment)
        self.assertEqual(state.legacy_process_kind(conky,environment),"conky")
        self.assertEqual(state.legacy_process_kind(background,environment),"wallpaper")
        foreign=self.snapshot(args=background["args"],environment=dict(environment,WAYLAND_DISPLAY="wayland-1"))
        self.assertIsNone(state.legacy_process_kind(foreign,environment))
        custom=self.snapshot(args=["swaybg","-i","/home/user/private.jpg"],environment=environment)
        self.assertIsNone(state.legacy_process_kind(custom,environment))

    def test_pidfd_handoff_rechecks_identity_before_sigterm(self):
        good=self.snapshot()
        descriptor=os.open(os.devnull,os.O_RDONLY)
        with patch.object(state.os,"pidfd_open",return_value=descriptor,create=True), \
                patch.object(state,"process_snapshot",return_value=good), \
                patch.object(state.signal,"pidfd_send_signal",create=True) as send, \
                patch.object(state.select,"select",return_value=([descriptor],[],[])):
            self.assertTrue(state.terminate_legacy(good))
            send.assert_called_once_with(descriptor,signal.SIGTERM)
        descriptor=os.open(os.devnull,os.O_RDONLY)
        with patch.object(state.os,"pidfd_open",return_value=descriptor,create=True), \
                patch.object(state,"process_snapshot",return_value=dict(good,started=good["started"]+1)), \
                patch.object(state.signal,"pidfd_send_signal",create=True) as send:
            self.assertFalse(state.terminate_legacy(good))
            send.assert_not_called()

    def test_handoff_never_signals_unrelated_processes(self):
        environment=self.environment()
        with tempfile.TemporaryDirectory() as temporary:
            proc=Path(temporary)
            for pid in (100,101,102): (proc/str(pid)).mkdir()
            records={100:self.snapshot(pid=100),
                     101:self.snapshot(pid=101,args=["conky","-c","/another/desktop.conf"]),
                     102:self.snapshot(pid=102,environment=self.environment(DISPLAY=":56"))}
            with patch.object(state.os,"geteuid",return_value=1000), \
                    patch.object(state,"process_snapshot",side_effect=lambda path:records[int(path.name)]), \
                    patch.object(state,"terminate_legacy",return_value=True) as retire:
                self.assertEqual(state.handoff_legacy(environment,proc),{"conky":True,"wallpaper":True})
                retire.assert_called_once_with(records[100],proc)
            with patch.object(state,"terminate_legacy") as retire:
                self.assertEqual(state.handoff_legacy({"DISPLAY":":55"},proc),{"conky":False,"wallpaper":False})
                retire.assert_not_called()

    def test_wayland_wrapper_loads_main_profile_not_itself(self):
        with tempfile.TemporaryDirectory() as temporary, \
                patch.dict(os.environ,{"XDG_CONFIG_HOME":temporary}), \
                patch.object(state.subprocess,"Popen") as launch:
            state.start_conky(wayland=True)
            self.assertEqual(launch.call_args.args[0],["conky","-c","/usr/share/daylight/labwc/conky.lua"])
            main=str(Path(temporary)/"daylight/conky.conf")
            self.assertEqual(launch.call_args.kwargs["env"]["DAYLIGHT_CONKY_CONFIG"],main)
            self.assertNotEqual(launch.call_args.args[0][-1],main)
            state.start_conky(wayland=False)
            self.assertEqual(launch.call_args.args[0],["conky","-c",main])
            self.assertEqual(launch.call_args.kwargs["env"]["DAYLIGHT_CONKY_CONFIG"],main)

    def test_x11_health_requires_nonzero_wm_window_property(self):
        with patch.object(state.shutil,"which",return_value="/usr/bin/xprop"), \
                patch.object(state.subprocess,"run") as run:
            run.return_value.returncode=0
            for output in ("_NET_SUPPORTING_WM_CHECK:  not found.\n",
                           "_NET_SUPPORTING_WM_CHECK(WINDOW): window id # 0x0\n", ""):
                run.return_value.stdout=output
                self.assertFalse(state.x11_display_alive())
            run.return_value.stdout="_NET_SUPPORTING_WM_CHECK(WINDOW): window id # 0x400001\n"
            self.assertTrue(state.x11_display_alive())
            run.return_value.returncode=1
            self.assertFalse(state.x11_display_alive())


if __name__=="__main__":
    unittest.main(verbosity=2)
