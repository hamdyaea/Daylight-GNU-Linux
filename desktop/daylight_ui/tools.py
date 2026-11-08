"""Modern offline Daylight utilities, built with Tk and vector artwork.

Copyright (C) 2026 Hamdy Abou El Anein. SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

from datetime import date, datetime
import math
from pathlib import Path
import queue
import secrets
import shutil
import string
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk

from . import diagnostics

PAGE_NAMES = {"info": "System information", "monitor": "System monitor",
              "password": "Password generator", "temperature": "Temperature converter",
              "days": "Days calculator", "connect": "Connections", "alarm": "Timer",
              "speech": "Text to speech", "sky": "Sun & Moon", "doctor": "Diagnostics"}

INK = "#292a43"
MUTED = "#66667b"
PAPER = "#faf8f2"
BACKGROUND = "#e9e6df"
HAIR = "#d7d2c8"
PURPLE = "#6548a3"
CORAL = "#ce6655"
AMBER = "#c79a36"
JADE = "#358d7d"
IRIS = "#7c6fbb"


def _number(value):
    return float(value.strip().replace(",", "."))


def _field(parent, text, variable, row, width=12):
    ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=(0, 20), pady=10)
    entry = ttk.Entry(parent, textvariable=variable, width=width)
    entry.grid(row=row, column=1, sticky="ew", pady=10)
    parent.columnconfigure(1, weight=1)
    return entry


def _message(parent, text="", color=None):
    color = color or MUTED
    widget = ttk.Label(parent, text=text, wraplength=340, foreground=color, justify="left")
    widget.pack(anchor="w", pady=(12, 0))
    return widget


class Page(ttk.Frame):
    def __init__(self, parent, title, subtitle, context=None):
        super().__init__(parent, padding=24)
        self.pack(fill="both", expand=True)
        self.context = context or {}
        self.jobs = set()
        self.speech_process = None
        self._closed = False
        self._wrap_width = 0
        ttk.Label(self, text=title, font=("DejaVu Sans", 25, "bold"), foreground=INK, wraplength=400).pack(anchor="w")
        ttk.Label(self, text=subtitle, foreground=MUTED, wraplength=400).pack(anchor="w", pady=(5, 20))
        self.body = ttk.Frame(self)
        self.body.pack(fill="both", expand=True)
        self.bind("<Destroy>", self._cleanup, add="+")
        self.bind("<Configure>", self._resize_text, add="+")

    def _resize_text(self, event):
        if event.widget is not self:
            return
        width = max(240, self.winfo_width() - 48)
        if width == self._wrap_width:
            return
        self._wrap_width = width
        def resize(widget):
            if isinstance(widget, ttk.Label):
                try:
                    if int(widget.cget("wraplength")):
                        widget.configure(wraplength=width)
                except (ValueError, tk.TclError):
                    pass
            for child in widget.winfo_children():
                resize(child)
        resize(self)

    def later(self, delay, function):
        holder = []
        def run():
            if holder:
                self.jobs.discard(holder[0])
            if not self._closed:
                function()
        job = self.after(delay, run)
        holder.append(job)
        self.jobs.add(job)
        return job

    def _cleanup(self, event):
        if event.widget is not self:
            return
        self._closed = True
        for job in self.jobs:
            try:
                self.after_cancel(job)
            except tk.TclError:
                pass
        self.jobs.clear()
        self.stop_speech()

    def stop_speech(self):
        process = self.speech_process
        self.speech_process = None
        if process and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
            # A daemon reaps a slow speech subprocess without holding the UI open.
            def reap():
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    try:
                        process.kill()
                    except OSError:
                        pass
                    process.wait()
            threading.Thread(target=reap, daemon=True).start()

    def async_read(self, function, callback):
        results = queue.Queue()
        def work():
            try:
                results.put((True, function()))
            except Exception as error:
                results.put((False, str(error)))
        threading.Thread(target=work, daemon=True).start()
        def poll():
            try:
                success, value = results.get_nowait()
            except queue.Empty:
                self.later(60, poll)
                return
            if success:
                callback(value)
            else:
                _message(self.body, "The local reading could not be completed: " + value, CORAL)
        self.later(30, poll)

    def illustration(self, height=200):
        art = tk.Canvas(self.body, height=height, bg=PAPER, highlightthickness=1,
                        highlightbackground=HAIR)
        art.pack(fill="x", pady=(0, 18))
        def resize(event):
            for tag, size in (("responsive-title", 19), ("responsive-subtitle", 10)):
                for item in art.find_withtag(tag):
                    x, _ = art.coords(item)
                    art.itemconfigure(item, width=max(100, event.width - x - 20),
                                      font=("DejaVu Sans", size if event.width > 650 else size - 3,
                                            "bold" if tag == "responsive-title" else "normal"))
        art.bind("<Configure>", resize)
        return art


def password_page(parent, context):
    page = Page(parent, "Password generator", "Made locally. Kept only in this window until you copy it.", context)
    art = page.illustration(130)
    art.create_oval(40, 35, 90, 85, outline=PURPLE, width=7)
    art.create_line(90, 60, 175, 60, fill=PURPLE, width=7)
    art.create_line(145, 60, 145, 83, fill=PURPLE, width=7)
    art.create_line(170, 60, 170, 78, fill=PURPLE, width=7)
    art.create_text(215, 50, text="A little privacy, by design.", anchor="w", fill=INK,
                    font=("DejaVu Sans", 19, "bold"), tags="responsive-title")
    art.create_text(215, 97, text="Operating system randomness · no saved history", anchor="w", fill=MUTED,
                    tags="responsive-subtitle")
    form = ttk.Frame(page.body)
    form.pack(fill="x")
    length = tk.StringVar(value="24")
    _field(form, "Length (8–256)", length, 0)
    symbols = tk.BooleanVar(value=True)
    ttk.Checkbutton(form, text="Include symbols", variable=symbols).grid(row=1, column=1, sticky="w", pady=8)
    value = tk.StringVar()
    output = ttk.Entry(page.body, textvariable=value, show="•", font=("DejaVu Sans Mono", 16))
    output.pack(fill="x", pady=18, ipady=9)
    controls = ttk.Frame(page.body)
    controls.pack(fill="x")
    status = _message(page.body)
    def generate():
        try:
            count = int(length.get())
            if not 8 <= count <= 256:
                raise ValueError("Choose a length between 8 and 256.")
            alphabet = string.ascii_letters + string.digits + ("!@#$%^&*()-_=+" if symbols.get() else "")
            value.set("".join(secrets.choice(alphabet) for _ in range(count)))
            status.configure(text="New password generated locally.", foreground=JADE)
        except ValueError:
            status.configure(text="Enter a whole number between 8 and 256.", foreground=CORAL)
    def copy():
        if value.get():
            page.clipboard_clear()
            page.clipboard_append(value.get())
            status.configure(text="Copied. Your desktop clipboard may retain it until replaced.", foreground=MUTED)
    ttk.Button(controls, text="Generate password", command=generate).pack(side="left")
    ttk.Button(controls, text="Copy", command=copy).pack(side="left", padx=10)
    revealed = tk.BooleanVar(value=False)
    ttk.Checkbutton(controls, text="Show", variable=revealed,
                    command=lambda: output.configure(show="" if revealed.get() else "•")).pack(side="left")
    generate()
    return page


def temperature_page(parent, context):
    page = Page(parent, "Temperature converter", "Celsius, Fahrenheit and Kelvin, in one place.", context)
    art = page.illustration(160)
    form = ttk.Frame(page.body)
    form.pack(fill="x")
    value, unit = tk.StringVar(value="20"), tk.StringVar(value="C")
    _field(form, "Temperature", value, 0)
    ttk.Label(form, text="Unit").grid(row=1, column=0, sticky="w", pady=10)
    ttk.Combobox(form, textvariable=unit, values=("C", "F", "K"), state="readonly", width=12).grid(row=1, column=1, sticky="w")
    result = _message(page.body)
    def convert(*_):
        try:
            number = _number(value.get())
            c = number if unit.get() == "C" else (number - 32) * 5 / 9 if unit.get() == "F" else number - 273.15
            if not math.isfinite(c) or c < -273.150000001:
                raise ValueError()
            result.configure(text=f"{c:,.2f} °C     ·     {c * 9 / 5 + 32:,.2f} °F     ·     {c + 273.15:,.2f} K", foreground=INK,
                             font=("DejaVu Sans", 19, "bold"))
            art.delete("all")
            art.create_oval(42, 99, 86, 143, fill=CORAL, outline="")
            art.create_line(64, 28, 64, 115, fill=HAIR, width=18)
            art.create_line(64, 115, 64, 115 - max(5, min(78, (c + 20) * .8)), fill=CORAL, width=10)
            art.create_text(120, 65, text="Every degree, clearly.", anchor="w", fill=INK, font=("DejaVu Sans", 21, "bold"),
                            tags="responsive-title", width=max(100, art.winfo_width()-140))
            art.create_text(120, 108, text="Local calculation · physical limits checked", anchor="w", fill=MUTED,
                            tags="responsive-subtitle", width=max(100, art.winfo_width()-140))
        except (ValueError, OverflowError):
            result.configure(text="Enter a finite number above absolute zero.", foreground=CORAL, font=("DejaVu Sans", 12))
    ttk.Button(page.body, text="Convert", command=convert).pack(anchor="w", pady=14)
    form.bind("<Return>", convert)
    convert()
    return page


def days_page(parent, context):
    page = Page(parent, "Days calculator", "Choose two calendar dates. Today follows your computer's local date.", context)
    art = page.illustration(140)
    for x, number in [(40, "01"), (145, "31")]:
        art.create_rectangle(x, 25, x + 75, 112, fill=PAPER, outline=HAIR, width=2)
        art.create_rectangle(x, 25, x + 75, 45, fill=IRIS, outline="")
        art.create_text(x + 38, 77, text=number, fill=INK, font=("DejaVu Sans", 26, "bold"))
    art.create_text(260, 65, text="Make the days count.", anchor="w", fill=INK, font=("DejaVu Sans", 22, "bold"),
                    tags="responsive-title")
    form = ttk.Frame(page.body)
    form.pack(fill="x")
    start, end = tk.StringVar(value="2000-01-01"), tk.StringVar(value=date.today().isoformat())
    _field(form, "Start · YYYY-MM-DD", start, 0)
    _field(form, "End · YYYY-MM-DD", end, 1)
    controls = ttk.Frame(page.body)
    controls.pack(fill="x", pady=12)
    result = _message(page.body)
    def calculate():
        try:
            first, last = date.fromisoformat(start.get()), date.fromisoformat(end.get())
            days = (last - first).days
            result.configure(text=f"{days:,} days", font=("DejaVu Sans", 28, "bold"), foreground=INK)
        except ValueError:
            result.configure(text="Enter valid dates in YYYY-MM-DD format.", font=("DejaVu Sans", 12), foreground=CORAL)
    ttk.Button(controls, text="Calculate", command=calculate).pack(side="left")
    ttk.Button(controls, text="Use today", command=lambda: (end.set(date.today().isoformat()), calculate())).pack(side="left", padx=10)
    calculate()
    return page


def alarm_page(parent, context):
    page = Page(parent, "Timer", "A quiet place to focus. The timer runs while this page stays open.", context)
    art = page.illustration(230)
    state = {"remaining": 300.0, "total": 300.0, "deadline": None}
    form = ttk.Frame(page.body)
    form.pack(fill="x")
    minutes = tk.StringVar(value="5")
    _field(form, "Minutes (up to 1440)", minutes, 0)
    controls = ttk.Frame(page.body)
    controls.pack(anchor="w", pady=12)
    status = _message(page.body, "Ready when you are.")
    def paint():
        if state["deadline"] is not None:
            state["remaining"] = max(0, state["deadline"] - time.monotonic())
            if state["remaining"] <= 0:
                state["deadline"] = None
                status.configure(text="Your timer has finished.", foreground=JADE)
                page.bell()
        seconds = math.ceil(state["remaining"])
        art.delete("all")
        art.create_oval(28, 18, 220, 210, outline=HAIR, width=10)
        if state["remaining"] > 0:
            art.create_arc(28, 18, 220, 210, start=90, extent=-360 * state["remaining"] / max(1, state["total"]), style="arc", outline=PURPLE, width=10)
        art.create_text(124, 112, text=f"{seconds // 60:02}:{seconds % 60:02}", fill=INK, font=("DejaVu Sans Mono", 30, "bold"))
        art.create_text(260, 78, text="A moment, just for this.", fill=INK, anchor="w", font=("DejaVu Sans", 18, "bold"),
                        width=max(100, art.winfo_width()-280))
        art.create_text(260, 146, text="Pause at any time. Closing the page cancels it.", anchor="w", fill=MUTED,
                        width=max(100, art.winfo_width()-280))
        page.later(200, paint)
    def start():
        try:
            seconds = _number(minutes.get()) * 60
            if not math.isfinite(seconds) or not 1 <= seconds <= 86400:
                raise ValueError()
            state.update(total=seconds, remaining=seconds, deadline=time.monotonic() + seconds)
            status.configure(text="Timer running.", foreground=PURPLE)
        except ValueError:
            status.configure(text="Choose a duration from 1 second to 1440 minutes.", foreground=CORAL)
    def pause():
        if state["deadline"] is None and state["remaining"] > 0:
            state["deadline"] = time.monotonic() + state["remaining"]
            status.configure(text="Timer running.", foreground=PURPLE)
        elif state["deadline"] is not None:
            state["remaining"] = max(0, state["deadline"] - time.monotonic())
            state["deadline"] = None
            status.configure(text="Paused. Press Pause / resume to continue.", foreground=MUTED)
    def cancel():
        state.update(deadline=None, remaining=0)
        status.configure(text="Timer cancelled.", foreground=MUTED)
    for label, action in [("Start new timer", start), ("Pause / resume", pause), ("Cancel", cancel)]:
        ttk.Button(controls, text=label, command=action).pack(side="left", padx=(0, 10))
    paint()
    return page


def speech_page(parent, context):
    page = Page(parent, "Text to speech", "Your words, read locally with eSpeak NG.", context)
    text = tk.Text(page.body, height=9, width=1, wrap="word", font=("DejaVu Sans", 15), background=PAPER,
                   foreground=INK, insertbackground=INK, relief="flat", padx=18, pady=18,
                   highlightthickness=1, highlightbackground=HAIR)
    text.pack(fill="both", expand=True)
    text.insert("1.0", "Welcome to Daylight Linux.")
    controls = ttk.Frame(page.body)
    controls.pack(fill="x", pady=16)
    voice = tk.StringVar(value="en")
    rate = tk.IntVar(value=160)
    ttk.Label(controls, text="Voice").pack(side="left", padx=(0, 8))
    ttk.Combobox(controls, textvariable=voice, values=("en", "fr", "de"), state="readonly", width=5).pack(side="left")
    ttk.Label(controls, text="Speed").pack(side="left", padx=(16, 8))
    ttk.Spinbox(controls, from_=80, to=300, textvariable=rate, width=5).pack(side="left")
    actions = ttk.Frame(page.body)
    actions.pack(anchor="w", pady=(0, 6))
    status = _message(page.body, "Ready. Nothing is uploaded.")
    def stop():
        page.stop_speech()
        status.configure(text="Stopped.", foreground=MUTED)
    def speak():
        executable = shutil.which("espeak-ng")
        if not executable:
            status.configure(text="Install espeak-ng to enable local speech.", foreground=CORAL)
            return
        content = text.get("1.0", "end-1c")
        try:
            speed = int(rate.get())
            if not 80 <= speed <= 300 or not 1 <= len(content) <= 4000:
                raise ValueError()
        except (ValueError, tk.TclError):
            status.configure(text="Enter 1–4000 characters and a speed between 80 and 300.", foreground=CORAL)
            return
        page.stop_speech()
        try:
            process = subprocess.Popen([executable, "--stdin", "-v", voice.get(), "-s", str(speed)],
                                       stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            page.speech_process = process
            def feed():
                try:
                    process.communicate(content.encode("utf-8"))
                except (OSError, ValueError):
                    pass
            threading.Thread(target=feed, daemon=True).start()
            status.configure(text="Speaking…", foreground=PURPLE)
            def finished():
                if page.speech_process is not process:
                    return
                if process.poll() is None:
                    page.later(150, finished)
                else:
                    page.speech_process = None
                    status.configure(text="Finished." if process.returncode == 0 else "Speech could not complete. Check your audio output.",
                                     foreground=JADE if process.returncode == 0 else CORAL)
            page.later(150, finished)
        except OSError:
            status.configure(text="eSpeak NG could not start.", foreground=CORAL)
    ttk.Button(actions, text="Read aloud", command=speak).pack(side="left", padx=(0, 8))
    ttk.Button(actions, text="Stop", command=stop).pack(side="left")
    return page


def network_page(parent, context):
    page = Page(parent, "Connections", "Addresses and gateways from this computer. No external connection test.", context)
    art = page.illustration(110)
    for x, fill in [(40, JADE), (170, IRIS), (300, AMBER)]:
        art.create_rectangle(x, 28, x + 62, 73, fill=fill, outline="")
        art.create_line(x + 31, 73, x + 31, 86, fill=fill, width=4)
        art.create_line(x + 15, 87, x + 47, 87, fill=fill, width=4)
    art.create_line(102, 50, 170, 50, fill=HAIR, width=3)
    art.create_line(232, 50, 300, 50, fill=HAIR, width=3)
    art.create_text(400, 53, text="Your local connections", anchor="w", fill=INK, font=("DejaVu Sans", 19, "bold"),
                    tags="responsive-title")
    table = ttk.Treeview(page.body, columns=("interface", "state", "addresses"), show="headings", height=7)
    for column, title, width in [("interface", "Interface", 100), ("state", "State", 85), ("addresses", "Addresses", 200)]:
        table.heading(column, text=title)
        table.column(column, width=width, stretch=column == "addresses")
    table.pack(fill="both", expand=True)
    gateway = _message(page.body, "Reading local interfaces…")
    def display(data):
        table.delete(*table.get_children())
        for interface in data["interfaces"]:
            table.insert("", "end", values=(interface["name"], interface["state"], ", ".join(interface["addresses"]) or "Not available"))
        routes = "; ".join(f"{item['gateway']} via {item['dev']}" for item in data["gateways"])
        gateway.configure(text="Default gateway: " + (routes or "No route found") +
                          ("" if data["addresses_supported"] else " · Install iproute2 to read addresses."))
    def refresh():
        page.async_read(diagnostics.network_info, display)
    ttk.Button(page.body, text="Refresh connections", command=refresh).pack(anchor="w", pady=12)
    refresh()
    return page


def _gauge(canvas, x, y, title, fraction, value, color, caption):
    canvas.create_rectangle(x, y, x + 215, y + 145, fill=PAPER, outline=HAIR)
    canvas.create_text(x + 16, y + 24, text=title.upper(), anchor="w", fill=MUTED, font=("DejaVu Sans", 10, "bold"))
    canvas.create_text(x + 16, y + 66, text=value, anchor="w", fill=INK, font=("DejaVu Sans", 26, "bold"))
    canvas.create_rectangle(x + 16, y + 100, x + 199, y + 107, fill=BACKGROUND, outline="")
    if fraction is not None:
        canvas.create_rectangle(x + 16, y + 100, x + 16 + 183 * min(1, max(0, fraction)), y + 107, fill=color, outline="")
    canvas.create_text(x + 16, y + 126, text=caption, anchor="w", fill=MUTED, font=("DejaVu Sans", 9))


def monitor_page(parent, context):
    page = Page(parent, "System monitor", "A clear view of your computer, with Raspberry Pi readings when supported.", context)
    model = ttk.Label(page.body, text="Reading local sensors…", font=("DejaVu Sans", 17, "bold"), foreground=INK)
    model.pack(anchor="w", pady=(0, 12))
    art = page.illustration(320)
    detail = _message(page.body)
    power = _message(page.body)
    previous = {"cpu": None}
    latest = {}
    def draw(_=None):
        if not latest:
            return
        data, cpu = latest["data"], latest["cpu"]
        art.delete("all")
        width = max(240, art.winfo_width())
        card_width = 215
        columns = max(1, min(3, (width - 12) // (card_width + 14)))
        items = [
            ("Processor", None if cpu is None else cpu / 100, "…" if cpu is None else f"{cpu:.0f}%", PURPLE, "Sampling CPU time" if cpu is None else "Current processor use"),
            ("Memory", data["memory_used"] / max(1, data["memory_total"]), f"{data['memory_used'] / 2**30:.1f} GiB", IRIS, f"of {data['memory_total'] / 2**30:.1f} GiB available RAM"),
            ("Temperature", None if data["temperature"] is None else data["temperature"] / 100,
             "—" if data["temperature"] is None else f"{data['temperature']:.1f} °C", CORAL, "Sensor unavailable" if data["temperature"] is None else "CPU / SoC thermal sensor"),
        ]
        rows = math.ceil(len(items) / columns)
        art.configure(height=rows * 159 + 12)
        for index, item in enumerate(items):
            _gauge(art, 6 + (index % columns) * 229, 6 + (index // columns) * 159, *item)
    def display(data):
        cpu = diagnostics.cpu_percent(previous["cpu"], data["cpu_times"])
        previous["cpu"] = data["cpu_times"]
        latest.update(data=data, cpu=cpu)
        model.configure(text=data["model"])
        hours, minutes = divmod(data["uptime"] // 60, 60)
        disk = data["storage"]
        disk_text = f"{disk['free'] / 2**30:.1f} GiB free on / ({disk['free'] / max(1, disk['total']) * 100:.0f}%)" if disk else "Storage reading unavailable"
        detail.configure(text=f"{data['system']} · {data['architecture']} · up {hours}h {minutes:02}m\n{disk_text}")
        if data["is_pi"]:
            flags = data["power"]
            if flags is None:
                power.configure(text="Pi firmware power reading unavailable. vcgencmd may be missing or inaccessible.", foreground=MUTED)
            else:
                current = ", ".join(flags["current"]) or "No active power or thermal warnings"
                history = ", ".join(flags["history"]) or "None recorded"
                power.configure(text=f"NOW · {current}\nSINCE BOOT · {history}", foreground=CORAL if flags["current"] else JADE)
        else:
            power.configure(text="Power warnings are shown on Raspberry Pi hardware with firmware support.", foreground=MUTED)
        draw()
        page.later(2000, refresh)
    def refresh():
        page.async_read(diagnostics.snapshot, display)
    art.bind("<Configure>", draw)
    refresh()
    return page


def doctor_page(parent, context):
    page = Page(parent, "Diagnostics", "Local checks with explanations. You stay in control of any changes.", context)
    cards = ttk.Frame(page.body)
    cards.pack(fill="both", expand=True)
    def display(checks):
        for child in cards.winfo_children():
            child.destroy()
        for item in checks:
            frame = ttk.Frame(cards, padding=(12, 8))
            frame.pack(fill="x", pady=4)
            ttk.Label(frame, text="●", foreground=JADE if item["ok"] else AMBER, font=("DejaVu Sans", 18)).pack(side="left", padx=(0, 12))
            content = ttk.Frame(frame)
            content.pack(fill="x", expand=True)
            ttk.Label(content, text=item["name"], font=("DejaVu Sans", 12, "bold")).pack(anchor="w")
            ttk.Label(content, text=item["detail"], foreground=MUTED, wraplength=650).pack(anchor="w", pady=(3, 0))
    ttk.Button(page.body, text="Run checks again", command=lambda: page.async_read(diagnostics.doctor_checks, display)).pack(anchor="w", pady=12)
    page.async_read(diagnostics.doctor_checks, display)
    return page


def sky_page(parent, context):
    from .sky import calculate_sun, calculate_moon
    page = Page(parent, "Sun & Moon", "A little daylight, wherever you are. Calculated locally for your chosen location.", context)
    state = page.context.get("state", {})
    form = ttk.Frame(page.body)
    form.pack(fill="x")
    latitude = tk.StringVar(value=str(state.get("latitude", 46.8)))
    longitude = tk.StringVar(value=str(state.get("longitude", 7.15)))
    timezone = tk.StringVar(value=state.get("timezone", "Europe/Zurich"))
    selected_date = tk.StringVar(value=date.today().isoformat())
    for index, (label, variable) in enumerate([
        ("Latitude (−90 to 90)", latitude), ("Longitude (−180 to 180)", longitude),
        ("Time zone · IANA name", timezone), ("Date · YYYY-MM-DD", selected_date),
    ]):
        row, column = divmod(index, 2)
        cell = ttk.Frame(form, padding=(0, 0, 14 if column == 0 else 0, 8))
        cell.grid(row=row, column=column, sticky="ew")
        ttk.Label(cell, text=label, foreground=MUTED).pack(anchor="w", pady=(0, 5))
        ttk.Entry(cell, textvariable=variable, width=18).pack(fill="x")
    form.columnconfigure(0, weight=1)
    form.columnconfigure(1, weight=1)
    controls = ttk.Frame(page.body)
    controls.pack(anchor="w", pady=12)
    art = page.illustration(220)
    status = _message(page.body)
    # Put the result first, so small Raspberry Pi screens show the sky rather
    # than a wall of location fields. Location controls remain directly below.
    art.pack_configure(before=form)
    status.pack_configure(before=form)
    current = {}
    def draw(_=None):
        if not current:
            return
        sun, moon = current["sun"], current["moon"]
        art.delete("all")
        width = max(440, art.winfo_width())
        horizon = 158
        art.create_line(26, horizon, width * .58, horizon, fill=HAIR, width=2)
        art.create_arc(35, 28, width * .58 - 10, 285, start=0, extent=180, outline=AMBER, width=3, style="arc")
        art.create_oval(width * .28 - 22, 18, width * .28 + 22, 62, fill=AMBER, outline="")
        rise = sun["sunrise"].strftime("%H:%M") if sun["sunrise"] else "—"
        setting = sun["sunset"].strftime("%H:%M") if sun["sunset"] else "—"
        art.create_text(40, 185, text=f"{rise}\nSUNRISE", anchor="w", fill=INK, font=("DejaVu Sans", 10, "bold"))
        art.create_text(width * .57, 185, text=f"{setting}\nSUNSET", anchor="e", fill=INK, font=("DejaVu Sans", 10, "bold"))
        center = width * .79
        art.create_oval(center - 40, 34, center + 40, 114, fill="#292c49", outline="")
        # A vector lunar disc: clip its lit portion mathematically, avoiding raster assets.
        phase = moon["phase_fraction"]
        waxing = phase < .5
        cosphase = math.cos(2 * math.pi * phase)
        for yy in range(-39, 40):
            half = math.sqrt(max(0, 40**2 - yy**2))
            left, right = ((cosphase * half, half) if waxing else (-half, -cosphase * half))
            art.create_line(center + left, 74 + yy, center + right, 74 + yy, fill="#f1d995")
        art.create_text(center, 141, text=moon["phase_name"], fill=INK, font=("DejaVu Sans", 12, "bold"))
        art.create_text(center, 167, text=f"{moon['illumination'] * 100:.0f}% illuminated", fill=MUTED)
    def calculate(save=False):
        try:
            chosen = date.fromisoformat(selected_date.get())
            lat, lon = _number(latitude.get()), _number(longitude.get())
            sun = calculate_sun(chosen, lat, lon, timezone.get().strip())
            moon = calculate_moon(chosen)
            current.update(sun=sun, moon=moon)
            from zoneinfo import ZoneInfo
            next_full = moon["next_full_moon"].astimezone(ZoneInfo(timezone.get().strip()))
            polar = {"polar_day": " · Sun stays above the horizon", "polar_night": " · Sun stays below the horizon"}.get(sun.get("polar_state"), "")
            status.configure(text=f"{sun['day_length_hours']:.2f} hours of daylight{polar}\nApproximate next full moon: {next_full:%Y-%m-%d %H:%M} ({timezone.get().strip()})\nAstronomical estimates: terrain, weather and actual atmospheric refraction can shift observed times.", foreground=MUTED)
            if save:
                callback = page.context.get("save_state")
                if callback:
                    callback({"latitude": lat, "longitude": lon, "timezone": timezone.get().strip()})
                else:
                    from .state import save_ui
                    save_ui({"latitude": lat, "longitude": lon, "timezone": timezone.get().strip()})
            draw()
        except (ValueError, KeyError, OSError, OverflowError) as error:
            status.configure(text="Check the location, time zone and date. " + str(error), foreground=CORAL)
    ttk.Button(controls, text="Calculate", command=calculate).pack(side="left", padx=(0, 10))
    ttk.Button(controls, text="Save location for the desktop", command=lambda: calculate(True)).pack(side="left")
    art.bind("<Configure>", draw)
    calculate()
    return page


def build(parent, name, context=None):
    # The shell rebuilds pages when the appearance changes. Canvas artwork must
    # follow the shared palette as well as ttk's widget colours.
    from .theme import PALETTE
    global INK, MUTED, PAPER, BACKGROUND, HAIR, PURPLE, CORAL, AMBER, JADE, IRIS
    INK, MUTED, PAPER = PALETTE["ink"], PALETTE["muted"], PALETTE["panel"]
    BACKGROUND, HAIR, PURPLE = PALETTE["bg"], PALETTE["line"], PALETTE["accent"]
    CORAL, AMBER, JADE, IRIS = (PALETTE[key] for key in ("coral", "amber", "jade", "iris"))
    builders = {"password": password_page, "temperature": temperature_page, "days": days_page,
                "alarm": alarm_page, "speech": speech_page, "connect": network_page,
                "info": monitor_page, "monitor": monitor_page, "doctor": doctor_page, "sky": sky_page}
    if name not in builders:
        raise ValueError("Unknown utility: " + name)
    return builders[name](parent, context)
