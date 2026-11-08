#!/usr/bin/env python3
"""Packaged Tk/Xwayland input regression under a real headless compositor.

The compositor receives a native Wayland virtual pointer while an authentic RC4
Tk client remains mapped behind the new clients. This exercises labwc/Xwayland
stacking: an application tested alone can work while overlapping clients lose
native input. XTest, Tk invoke and synthetic Tk events must not drive this test.
Conky remains running as part of the normal desktop. Run only as a normal user
in the disposable package-test container.

SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import unittest


UI = Path("/usr/share/daylight/ui")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UI))


def stop(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


def historical_background_ui(runtime):
    """Extract the exact published RC4 desktop without installing old files."""
    name = "daylight-desktop_5.0.0~rc4_all.deb"
    archive = ROOT / "dist/previous-rc4" / name
    manifest = json.loads((ROOT / "release/rc4-packages.json").read_text())
    if not archive.is_file():
        raise AssertionError("Missing authentic RC4 desktop fixture: " + str(archive))
    if hashlib.sha256(archive.read_bytes()).hexdigest() != manifest["packages"][name]:
        raise AssertionError("The RC4 background client must match the published package checksum")
    destination = runtime / "previous-rc4"
    subprocess.run(["dpkg-deb", "--extract", str(archive), str(destination)], check=True)
    source = destination / "usr/share/daylight/ui"
    if not (source / "daylight_ui/shell.py").is_file():
        raise AssertionError("The authentic RC4 desktop fixture has no native UI")
    return source


def background_client(source, ready):
    """An old, independent Tk process; do not run its session bootstrap."""
    sys.path.insert(0, str(source))
    from daylight_ui.shell import Desktop
    root = Desktop("home")
    root.title("Daylight regression: authentic RC4 background")
    root.geometry(f"{root.winfo_screenwidth()}x{max(540, root.winfo_screenheight()-40)}+0+0")
    root.update()
    ready.write_text(json.dumps({"pid": os.getpid(), "inner": hex(root.winfo_id()),
                                 "frame": str(root.tk.call("wm", "frame", ".")),
                                 "source": str(source), "geometry": root.winfo_geometry(),
                                 "bounds": [root.winfo_rootx(), root.winfo_rooty(),
                                            root.winfo_width(), root.winfo_height()],
                                 "preload": os.environ.get("LD_PRELOAD")}))
    root.mainloop()


@unittest.skipUnless(os.environ.get("DAYLIGHT_WAYLAND_TEST_CLIENT") == "yes",
                     "Requires the isolated labwc package-test harness")
class NativeWaylandInput(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from daylight_ui import state
        from wayland_pointer import NativePointer
        # Exercise the installed appearance owner and the exact packaged Conky
        # wrapper, rather than constructing a special test-only Conky window.
        state.save_core({"monitor": "on", "profile": "balanced"})
        subprocess.run(["/usr/bin/daylight", "setup-session"], check=True)
        cls.manager_log = open(Path(os.environ["XDG_RUNTIME_DIR"]) / "appearance.log", "w")
        cls.manager = subprocess.Popen(
            [sys.executable, str(UI / "daylight_gui.py"), "--session-appearance"],
            stdout=cls.manager_log, stderr=subprocess.STDOUT)
        cls.addClassCleanup(cls.manager_log.close)
        cls.addClassCleanup(stop, cls.manager)
        deadline = time.monotonic() + 20
        cls.conky = None
        while time.monotonic() < deadline:
            if cls.manager.poll() is not None:
                raise AssertionError("Installed appearance owner exited before starting Conky")
            for path in Path("/proc").iterdir():
                if not path.name.isdigit():
                    continue
                record = state.process_snapshot(path)
                if (record and state.same_daylight_session(record)
                        and record["args"] and Path(record["args"][0]).name == "conky"):
                    cls.conky = record
                    break
            windows = subprocess.run(["xwininfo", "-root", "-tree"],
                                     capture_output=True, text=True, check=True).stdout
            if cls.conky and "conky" in windows.casefold():
                break
            time.sleep(.1)
        else:
            raise AssertionError("The installed Wayland appearance owner did not map Conky")
        # Keep an unmodified old client open throughout every foreground test.
        # Closing it before clicking would hide the actual stacking regression.
        runtime = Path(os.environ["XDG_RUNTIME_DIR"])
        source = historical_background_ui(runtime)
        ready = runtime / "background-ready.json"
        cls.background_log = (runtime / "background.log").open("w")
        cls.addClassCleanup(cls.background_log.close)
        environment = dict(os.environ, DAYLIGHT_SESSION="0", PYTHONNOUSERSITE="1",
                           XDG_CONFIG_HOME=str(runtime / "background-preferences"))
        for key in ("LD_PRELOAD", "DAYLIGHT_XTRACE_PATH", "DAYLIGHT_XINITIAL_OR_ISOLATED_TEST",
                    state.MANAGER_REVISION_KEY, "PYTHONPATH", "PYTHONSTARTUP"):
            environment.pop(key, None)
        cls.background = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--background-ui", str(source),
             "--background-ready", str(ready)], env=environment,
            stdout=cls.background_log, stderr=subprocess.STDOUT)
        cls.addClassCleanup(stop, cls.background)
        deadline = time.monotonic() + 15
        while not ready.is_file() and cls.background.poll() is None and time.monotonic() < deadline:
            time.sleep(.05)
        if not ready.is_file():
            raise AssertionError("The authentic RC4 background Tk client did not map; see background.log")
        cls.background_info = json.loads(ready.read_text())
        cls.pointer = NativePointer()
        cls.addClassCleanup(cls.pointer.close)
        cls.executor = ThreadPoolExecutor(max_workers=1)
        cls.addClassCleanup(cls.executor.shutdown, True)
        print("Native Wayland pointer active; Conky remains running:",
              json.dumps({"pid": cls.conky["pid"], "args": cls.conky["args"],
                          "display": os.environ["DISPLAY"],
                          "wayland": os.environ["WAYLAND_DISPLAY"],
                          "historical_background": cls.background_info}), flush=True)

    def setUp(self):
        from daylight_ui.shell import Desktop
        self.errors = []
        self.press_events = []
        self.root = Desktop("cards")
        self.root.geometry("1060x650+10+10")
        self.watch_root()
        self.addCleanup(self.close_root)
        self.pump(.5)
        self.root.lift()
        self.pump(.2)

    def watch_root(self):
        self.root.report_callback_exception = lambda kind, error, trace: self.errors.append(str(error))
        self.root.bind_all("<ButtonPress-1>", lambda event: self.press_events.append({
            "widget": str(event.widget), "class": event.widget.winfo_class(),
            "screen": [event.x_root, event.y_root]}), add="+")

    def close_root(self):
        import tkinter as tk
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assert_conky_alive()

    def pump(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.root.update()
            time.sleep(.01)

    def assert_conky_alive(self):
        from daylight_ui import state
        current = state.process_snapshot(Path("/proc") / str(self.conky["pid"]))
        self.assertIsNotNone(current, "Conky must remain alive during every input assertion")
        self.assertEqual(current["started"], self.conky["started"])
        self.assertEqual(current["args"], self.conky["args"])
        self.assertIsNone(self.manager.poll(), "The appearance owner must remain alive")
        self.assertIsNone(self.background.poll(), "The old overlapping RC4 client must remain alive")

    def click(self, widget, x=None, y=None):
        self.assert_conky_alive()
        self.root.update()
        x = widget.winfo_width() // 2 if x is None else x
        y = widget.winfo_height() // 2 if y is None else y
        target = (widget.winfo_rootx() + x, widget.winfo_rooty() + y,
                  self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.assertTrue(0 <= target[0] < target[2] and 0 <= target[1] < target[3], target)
        bx, by, bw, bh = self.background_info["bounds"]
        self.assertTrue(bx <= target[0] < bx+bw and by <= target[1] < by+bh,
                        "The click must overlap the historical Tk client: " + str(target))
        # Keep Tk's event loop alive while the compositor delivers pointer enter,
        # focus, button press and release through Xwayland.
        before = len(self.press_events)
        future = self.executor.submit(self.pointer.click, *target)
        deadline = time.monotonic() + 8
        while not future.done() and time.monotonic() < deadline:
            self.pump(.02)
        future.result(timeout=1)
        self.pump(.15)
        self.assert_conky_alive()
        self.assertGreater(len(self.press_events), before,
                           "The native Wayland click went to another overlapping Tk client")
        self.assertTrue(all(abs(actual-requested) <= 2 for actual, requested in
                            zip(self.press_events[-1]["screen"], target[:2])), self.press_events[-1])

    def page(self, name):
        self.root.show(name)
        self.pump(.25)
        return self.root.content.winfo_children()[0]

    def button(self, parent, label):
        from tkinter import ttk
        return next(widget for widget in descendants(parent)
                    if isinstance(widget, ttk.Button) and str(widget.cget("text")) == label)

    def test_battle_reveals_tie_continues_and_collects_with_native_pointer(self):
        from daylight_ui.game_models import Battle, Card
        page = self.page("cards")
        page.battle = Battle(hands=(
            [Card(8, "♣"), Card(2, "♣"), Card(14, "♠"), Card(3, "♦")],
            [Card(8, "♥"), Card(4, "♥"), Card(13, "♥"), Card(5, "♦")]))
        page.redraw()
        self.click(page.next_battle)
        self.assertEqual(page.battle.phase, "battle", "Native pointer did not reveal the cards")
        self.click(page.next_battle)
        self.assertEqual(page.battle.phase, "collect", "Native pointer did not continue the battle")
        self.assertEqual(len(page.battle.pot), 6)
        self.click(page.next_battle)
        self.assertEqual(page.battle.phase, "ready", "Native pointer did not collect the pot")
        self.assertEqual(page.battle.card_count(), 8)

    def test_memory_canvas_card_flips_with_native_pointer(self):
        page = self.page("memory")
        box = page.cv.bbox("memory-0")
        self.assertIsNotNone(box)
        self.click(page.cv, (box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        self.assertEqual(page.memory.open, [0], "Native pointer did not flip the Memory card")

    def test_timer_start_and_cancel_with_native_pointer(self):
        from tkinter import ttk
        page = self.page("alarm")
        entry = next(widget for widget in descendants(page) if isinstance(widget, ttk.Entry))
        entry.delete(0, "end")
        entry.insert(0, "1")
        self.click(self.button(page, "Start new timer"))
        self.assertTrue(any(isinstance(widget, ttk.Label) and
                            str(widget.cget("text")) == "Timer running."
                            for widget in descendants(page)), "Native pointer did not start the timer")
        self.click(self.button(page, "Cancel"))
        self.assertTrue(any(isinstance(widget, ttk.Label) and
                            str(widget.cget("text")) == "Timer cancelled."
                            for widget in descendants(page)), "Native pointer did not cancel the timer")

    def test_shardturn_new_match_opens_and_dismisses_modal_with_native_pointer(self):
        import tkinter as tk
        # Use the shipped factory so this test exercises exactly the same
        # window initialization as the installed Shardturn desktop launcher.
        spec = importlib.util.spec_from_file_location("daylight_packaged_shardturn_launcher",
                                                     UI / "shardturn_launcher.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.root.destroy()
        self.root, app = module.create_app(seed=42)
        self.root.geometry("1200x680+10+0")
        self.watch_root()
        self.pump(.5)
        self.root.lift()
        self.pump(.2)
        app.cancel_ai()
        original_game = app.game
        def click_region(action):
            a, b, c, d, _, _ = next(region for region in app.regions if region[4] == action)
            self.click(app.canvas, round(app.ox + (a + c) / 2 * app.scale),
                       round(app.oy + (b + d) / 2 * app.scale))
        click_region("new_match")
        self.assertEqual(app.overlay, ("confirm",), "Native pointer did not open Shardturn's N modal")
        click_region("cancel_overlay")
        self.assertIsNone(app.overlay, "Native pointer did not dismiss Shardturn's modal")
        self.assertIs(app.game, original_game)
        click_region("help")
        self.assertIsNotNone(app.help_window, "Native pointer did not open Shardturn's help dialog")
        self.pump(.25)
        help_text = next(widget for widget in descendants(app.help_window)
                         if isinstance(widget, tk.Text))
        self.click(help_text)
        self.assertEqual(self.press_events[-1]["class"], "Text")
        app.help_window.destroy()
        app.help_window = None
        app.cancel_ai()


def compositor_test(output):
    if os.geteuid() == 0:
        raise SystemExit("Run the Wayland compositor as the disposable normal user")
    if os.environ.get("DAYLIGHT_DISPOSABLE_TEST") != "yes":
        raise SystemExit("Requires DAYLIGHT_DISPOSABLE_TEST=yes")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="daylight-wayland-") as temporary:
        runtime = Path(temporary)
        runtime.chmod(0o700)
        config = runtime / "labwc"
        config.mkdir()
        result = runtime / "result.json"
        command = [sys.executable, str(Path(__file__).resolve()), "--client", "--result", str(result)]
        autostart = config / "autostart"
        autostart.write_text("#!/bin/sh\nexec " + shlex.join(command) + "\n")
        autostart.chmod(0o700)
        environment = dict(os.environ, XDG_RUNTIME_DIR=str(runtime),
                           XDG_CONFIG_HOME=str(runtime / "config"),
                           XDG_SESSION_TYPE="wayland", DAYLIGHT_SESSION="1",
                           DAYLIGHT_WAYLAND_TEST_CLIENT="yes",
                           WLR_BACKENDS="headless", WLR_RENDERER="pixman",
                           WLR_HEADLESS_OUTPUTS="1", LIBGL_ALWAYS_SOFTWARE="1")
        environment.pop("DISPLAY", None)
        environment.pop("WAYLAND_DISPLAY", None)
        # labwc starts Xwayland and exports its actual DISPLAY to autostart.
        with (output / "wayland-input.log").open("w") as log:
            compositor = subprocess.Popen(["labwc", "-C", str(config)], env=environment,
                                          stdout=log, stderr=subprocess.STDOUT,
                                          start_new_session=True)
            try:
                deadline = time.monotonic() + 100
                while not result.is_file() and compositor.poll() is None and time.monotonic() < deadline:
                    time.sleep(.1)
                if not result.is_file():
                    raise RuntimeError("labwc input test did not finish; see wayland-input.log")
                outcome = json.loads(result.read_text())
                (output / "wayland-input-result.json").write_text(json.dumps(outcome, indent=2) + "\n")
                if not outcome["success"]:
                    raise RuntimeError("Native Wayland input regression failed; see wayland-input.log")
            finally:
                # Stop only this disposable compositor's process group.
                if compositor.poll() is None:
                    os.killpg(compositor.pid, signal.SIGTERM)
                stop(compositor)
                for name in ("appearance.log", "background.log", "background-ready.json"):
                    source = runtime / name
                    if source.is_file():
                        (output / ("wayland-" + name)).write_bytes(source.read_bytes())
    print("DAYLIGHT_NATIVE_WAYLAND_INPUT_OK", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--background-ui", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--background-ready", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, default=Path("/tmp/daylight-wayland-evidence"))
    args = parser.parse_args()
    if args.background_ui:
        background_client(args.background_ui, args.background_ready)
        return 0
    if args.client:
        outcome = {"success": False}
        try:
            suite = unittest.defaultTestLoader.loadTestsFromTestCase(NativeWaylandInput)
            results = unittest.TextTestRunner(verbosity=2).run(suite)
            outcome.update(success=results.wasSuccessful(), tests=results.testsRun,
                           failures=len(results.failures), errors=len(results.errors),
                           skipped=len(results.skipped))
            if results.skipped or results.testsRun != 4:
                outcome["success"] = False
        except BaseException:
            traceback.print_exc()
        finally:
            args.result.write_text(json.dumps(outcome) + "\n")
        return 0 if outcome["success"] else 1
    compositor_test(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
