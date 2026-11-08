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
import re
import shlex
import shutil
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
TEST_CASES = {
    "test_battle_reveals_tie_continues_and_collects_with_native_pointer": "cards",
    "test_memory_canvas_card_flips_with_native_pointer": "memory",
    "test_shardturn_new_match_opens_and_dismisses_modal_with_native_pointer": "shardturn",
    "test_timer_start_and_cancel_with_native_pointer": "alarm",
}


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


def bounds(widget):
    return [widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_width(), widget.winfo_height()]


def visible_rectangle(widget):
    """Intersect the widget with each ancestor, including a scroll viewport."""
    left, top, width, height = bounds(widget)
    right, bottom = left + width, top + height
    parent = widget.master
    while parent is not None:
        x, y, width, height = bounds(parent)
        left, top, right, bottom = max(left, x), max(top, y), min(right, x+width), min(bottom, y+height)
        if parent == widget.winfo_toplevel():
            break
        parent = parent.master
    return [left, top, right, bottom]


def native_conky_surface(log):
    """Require a Conky layer surface with a real attached, committed buffer."""
    if not log.is_file():
        return None
    trace = log.read_text(errors="replace")
    layer = re.search(r'get_layer_surface\([^\n]*\bwl_surface[@#](\d+)[^\n]*"(?:conky|conky_namespace)"[^\n]*\)',
                      trace, re.IGNORECASE)
    if layer is None:
        return None
    surface = r'\bwl_surface[@#]' + layer.group(1) + r'\.'
    tail = trace[layer.end():]
    attach = re.search(surface + r'attach\(\s*wl_buffer[@#]\d+[^\n]*\)', tail)
    if attach is None:
        return None
    commit = re.search(surface + r'commit\(\)', tail[attach.end():])
    if commit is None:
        return None
    return {"surface": "wl_surface@" + layer.group(1), "layer_request": layer.group(0),
            "buffer_attach": attach.group(0), "buffer_commit": commit.group(0)}


def bounded_wayland_log(path, limit=1024 * 1024):
    """Keep the initial protocol proof, then drain without growing the log."""
    remaining = limit
    with path.open("wb") as output:
        while True:
            chunk = os.read(sys.stdin.fileno(), 8192)
            if not chunk:
                return
            if remaining:
                selected = chunk[:remaining]
                output.write(selected)
                output.flush()
                remaining -= len(selected)


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
        # A normal desktop has a pointer before Conky connects. Establish that
        # seat capability first: Conky 1.22.1 aborts if a previously empty headless
        # seat gains its first pointer later. NativePointer's constructor waits
        # for a compositor roundtrip after creating the device. Register this
        # cleanup first so Conky stops before the pointer disappears again.
        cls.pointer = NativePointer()
        cls.addClassCleanup(cls.pointer.close)
        # Exercise the installed appearance owner and the exact packaged Conky
        # wrapper, rather than constructing a special test-only Conky window.
        runtime = Path(os.environ.get("DAYLIGHT_WAYLAND_CASE_DIR", os.environ["XDG_RUNTIME_DIR"]))
        cls.native_conky_log = runtime / "conky-native.log"
        # Capture protocol diagnostics from Conky only. The shell exec retains
        # its PID and the installed owner's normal child cleanup; the logger
        # drains stderr to EOF while retaining at most 1 MiB of evidence.
        executable = shutil.which("conky")
        if executable is None:
            raise AssertionError("The installed desktop must provide Conky")
        shim_directory = runtime / "test-bin"
        shim_directory.mkdir()
        logger = shlex.join([sys.executable, str(Path(__file__).resolve()),
                             "--bounded-wayland-log", str(cls.native_conky_log)])
        shim = shim_directory / "conky"
        shim.write_text("#!/bin/bash\nexport WAYLAND_DEBUG=client\nexec " + shlex.quote(executable) +
                        ' "$@" 2> >(' + logger + ")\n")
        shim.chmod(0o700)
        state.save_core({"monitor": "on", "profile": "balanced"})
        subprocess.run(["/usr/bin/daylight", "setup-session"], check=True)
        cls.manager_log = (runtime / "appearance.log").open("w")
        cls.manager = subprocess.Popen(
            [sys.executable, str(UI / "daylight_gui.py"), "--session-appearance"],
            env=dict(os.environ, PATH=str(shim_directory) + os.pathsep + os.environ.get("PATH", "")),
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
            cls.native_protocol = native_conky_surface(cls.native_conky_log)
            if cls.conky and cls.native_protocol:
                break
            time.sleep(.1)
        else:
            raise AssertionError("Conky did not attach and commit a native Wayland layer buffer; see conky-native.log")
        (runtime / "native-conky-surface.json").write_text(json.dumps(cls.native_protocol, indent=2) + "\n")
        # Keep an unmodified old client open throughout every foreground test.
        # Closing it before clicking would hide the actual stacking regression.
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
        cls.executor = ThreadPoolExecutor(max_workers=1)
        cls.addClassCleanup(cls.executor.shutdown, True)
        print("Native Wayland pointer active; Conky remains running:",
              json.dumps({"pid": cls.conky["pid"], "args": cls.conky["args"],
                          "display": os.environ["DISPLAY"],
                          "wayland": os.environ["WAYLAND_DISPLAY"],
                          "native_conky_surface": cls.native_protocol,
                          "historical_background": cls.background_info}), flush=True)

    def setUp(self):
        self.errors = []
        self.press_events = []
        page = TEST_CASES[self._testMethodName]
        if page == "shardturn":
            spec = importlib.util.spec_from_file_location("daylight_packaged_shardturn_launcher",
                                                         UI / "shardturn_launcher.py")
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            self.root, self.shardturn = module.create_app(seed=42)
            self.root.geometry("1200x680+10+0")
        else:
            from daylight_ui.shell import Desktop
            self.root = Desktop(page)
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
        clip = visible_rectangle(widget)
        print(json.dumps({"native_click_target": list(target[:2]), "widget": str(widget),
                          "widget_bounds": bounds(widget), "root_bounds": bounds(self.root),
                          "visible_clip": clip, "canvas_bounds": bounds(self.root.canvas) if hasattr(self.root, "canvas") else None}), flush=True)
        self.assertTrue(0 <= target[0] < target[2] and 0 <= target[1] < target[3], target)
        self.assertTrue(widget.winfo_viewable() and clip[0] <= target[0] < clip[2]
                        and clip[1] <= target[1] < clip[3],
                        "Native pointer target is clipped outside its visible ancestor viewport")
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
        if self.root.current_page != name:
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
        start = self.button(page, "Start new timer")
        print(json.dumps({"timer_before_scroll": bounds(start),
                          "visible_clip": visible_rectangle(start),
                          "canvas_yview": list(self.root.canvas.yview())}), flush=True)
        self.root.canvas.yview_moveto(1)
        self.pump(.25)
        print(json.dumps({"timer_after_scroll": bounds(start),
                          "visible_clip": visible_rectangle(start),
                          "canvas_yview": list(self.root.canvas.yview())}), flush=True)
        self.click(start)
        self.assertTrue(any(isinstance(widget, ttk.Label) and
                            str(widget.cget("text")) == "Timer running."
                            for widget in descendants(page)), "Native pointer did not start the timer")
        self.click(self.button(page, "Cancel"))
        self.assertTrue(any(isinstance(widget, ttk.Label) and
                            str(widget.cget("text")) == "Timer cancelled."
                            for widget in descendants(page)), "Native pointer did not cancel the timer")

    def test_shardturn_new_match_opens_and_dismisses_modal_with_native_pointer(self):
        import tkinter as tk
        # setUp used the shipped factory, with one Tk interpreter in this
        # fresh process just as the installed Shardturn launcher does.
        app = self.shardturn
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
        self.assertEqual(self.press_events[-1]["widget"], str(help_text))
        close_button = next(widget for widget in descendants(app.help_window)
                            if isinstance(widget, tk.Button) and
                            str(widget.cget("text")) == "Close  ·  Esc")
        self.click(close_button)
        self.assertIsNone(app.help_window, "The native Close button did not dismiss the help panel")
        self.assertIsNone(self.root.grab_current())
        app.cancel_ai()


def client_batch(result):
    """Run each launcher check in a fresh Python process on this compositor."""
    cases = Path(os.environ["XDG_RUNTIME_DIR"]) / "cases"
    cases.mkdir(mode=0o700)
    aggregate = {"success": True, "tests": 0, "failures": 0, "errors": 0, "skipped": 0, "cases": []}
    for name, application in TEST_CASES.items():
        directory = cases / application
        directory.mkdir(mode=0o700)
        outcome_path = directory / "result.json"
        environment = dict(os.environ, DAYLIGHT_WAYLAND_CASE_DIR=str(directory),
                           XDG_CONFIG_HOME=str(directory / "config"))
        with (directory / "client.log").open("w") as log:
            child = subprocess.Popen(
                [sys.executable, str(Path(__file__).resolve()), "--client", "--test-name", name,
                 "--result", str(outcome_path)], env=environment, stdout=log, stderr=subprocess.STDOUT)
            try:
                returncode = child.wait(timeout=60)
            except subprocess.TimeoutExpired:
                stop(child)
                returncode = -1
        if outcome_path.is_file():
            outcome = json.loads(outcome_path.read_text())
        else:
            outcome = {"success": False, "tests": 0, "failures": 0, "errors": 1, "skipped": 0}
        outcome.update(application=application, returncode=returncode)
        if returncode or outcome["tests"] != 1 or outcome["skipped"]:
            outcome["success"] = False
        aggregate["cases"].append(outcome)
        aggregate["success"] = aggregate["success"] and outcome["success"]
        for key in ("tests", "failures", "errors", "skipped"):
            aggregate[key] += outcome[key]
        print(json.dumps({"fresh_process_case": application, "result": outcome}), flush=True)
        print((directory / "client.log").read_text(errors="replace"), flush=True)
    if aggregate["tests"] != len(TEST_CASES):
        aggregate["success"] = False
    result.write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0 if aggregate["success"] else 1


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
        command = [sys.executable, str(Path(__file__).resolve()), "--client-batch", "--result", str(result)]
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
                deadline = time.monotonic() + 260
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
                for directory in (runtime / "cases").glob("*"):
                    for name in ("client.log", "result.json", "appearance.log", "background.log",
                                 "background-ready.json", "conky-native.log", "native-conky-surface.json"):
                        source = directory / name
                        if source.is_file():
                            (output / ("wayland-" + directory.name + "-" + name)).write_bytes(source.read_bytes())
    print("DAYLIGHT_NATIVE_WAYLAND_INPUT_OK", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--client-batch", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--test-name", choices=tuple(TEST_CASES), help=argparse.SUPPRESS)
    parser.add_argument("--result", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--background-ui", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--background-ready", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--bounded-wayland-log", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--output", type=Path, default=Path("/tmp/daylight-wayland-evidence"))
    args = parser.parse_args()
    if args.bounded_wayland_log:
        bounded_wayland_log(args.bounded_wayland_log)
        return 0
    if args.background_ui:
        background_client(args.background_ui, args.background_ready)
        return 0
    if args.client_batch:
        return client_batch(args.result)
    if args.client:
        if not args.test_name:
            parser.error("--client requires exactly one --test-name")
        outcome = {"success": False, "tests": 0, "failures": 0, "errors": 1, "skipped": 0}
        try:
            suite = unittest.TestSuite([NativeWaylandInput(args.test_name)])
            results = unittest.TextTestRunner(verbosity=2).run(suite)
            outcome.update(success=results.wasSuccessful(), tests=results.testsRun,
                           failures=len(results.failures), errors=len(results.errors),
                           skipped=len(results.skipped))
            if results.skipped or results.testsRun != 1:
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
