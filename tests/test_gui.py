#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: contact@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Exercise native dialogs in a disposable desktop, without recording their contents."""
import os
import re
import signal
import subprocess
import time
import unittest


class NativeDialogs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("DAYLIGHT_DISPOSABLE_TEST") != "yes" or os.geteuid() == 0:
            raise unittest.SkipTest("Requires an unprivileged disposable desktop test")

    def xdo(self, *args, check=True):
        return subprocess.run(["xdotool", *args], text=True, capture_output=True,
                              timeout=10, check=check)

    def window(self, title, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = self.xdo("search", "--onlyvisible", "--name", "^" + re.escape(title) + "$", check=False)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.splitlines()[-1]
            time.sleep(0.1)
        self.fail("Expected application window did not appear: " + title)

    def exercise(self, app, title, value=None, cancel=False, delay=0):
        process = subprocess.Popen(["/usr/bin/daylight", "app", app],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                   start_new_session=True)
        try:
            if value is not None or cancel:
                initial = self.window("Daylight GNU/Linux")
                self.xdo("windowactivate", "--sync", initial)
                if cancel:
                    self.xdo("key", "Escape")
                else:
                    self.xdo("key", "ctrl+a")
                    self.xdo("type", "--clearmodifiers", "--delay", "0", value)
                    self.xdo("key", "Return")
            if not cancel:
                time.sleep(delay)
                result = self.window(title)
                self.xdo("windowclose", result)
            _, error = process.communicate(timeout=10)
            self.assertEqual(process.returncode, 0, error.decode(errors="replace"))
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()

    def test_information(self):
        self.exercise("info", "Daylight GNU/Linux")

    def test_password(self):
        self.exercise("password", "Daylight Password Generator", "32")

    def test_temperature(self):
        self.exercise("temperature", "Daylight Temperature", "20 C")

    def test_dates(self):
        self.exercise("days", "Daylight Days Calculator", "2000-01-01")

    def test_connections(self):
        self.exercise("connect", "Daylight Connect - local information")

    def test_dice(self):
        self.exercise("dice", "Daylight Dice", "6 2")

    def test_coin(self):
        self.exercise("coin", "Daylight Coin")

    def test_lottery(self):
        self.exercise("lottery", "Daylight Lottery Simulator")

    def test_rpsls(self):
        self.exercise("rpsls", "Daylight RPSLS", "rock")

    def test_cards(self):
        self.exercise("cards", "Daylight Battle Cards")

    def test_tournament(self):
        self.exercise("tournament", "Daylight Tournament", "A,B,C,D")

    def test_basketball(self):
        self.exercise("basketball", "Daylight Basketball")

    def test_slots(self):
        self.exercise("slots", "Daylight Slot Simulator")

    def test_memory_cancellation(self):
        self.exercise("memory", "", cancel=True)

    def test_guess_cancellation(self):
        self.exercise("guess", "", cancel=True)

    def test_alarm(self):
        self.exercise("alarm", "Daylight Alarm", "2", delay=3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
