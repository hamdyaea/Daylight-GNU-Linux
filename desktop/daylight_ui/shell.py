"""Daylight application library, first steps, settings and session appearance.

Copyright (C) 2026 Hamdy Abou El Anein
SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from zoneinfo import ZoneInfo

from . import launcher, state, theme, windowing

ROOT = Path(__file__).resolve().parent.parent
RESOURCE_ROOT = Path("/usr/share/daylight")
WALLPAPER_ROOT = Path("/usr/share/backgrounds/daylight")
if not WALLPAPER_ROOT.is_dir():
    WALLPAPER_ROOT = ROOT.parent / "assets/wallpapers"

GAME_NAMES = {"shardturn": "Daylight Shardturn", "cards": "Battle Cards", "memory": "Memory",
              "tournament": "2018 World Cup", "basketball": "NBA Playoffs", "rpsls": "Rock · Paper · Spock",
              "dice": "Dice", "coin": "Coin Flip", "slots": "Symbols", "lottery": "Lottery", "guess": "Guess the Number"}
TOOL_NAMES = {"monitor": "System Monitor", "sky": "Sun & Moon", "password": "Passwords",
              "temperature": "Temperature", "days": "Date Calculator", "connect": "Connections",
              "alarm": "Timer", "speech": "Read Aloud", "doctor": "Diagnostics", "info": "About this Computer"}
DESCRIPTIONS = {
    "shardturn": "The colour card duel. Original geometric cards and thoughtful play.",
    "cards": "A full deck, face-down battles and a prize to collect.",
    "memory": "Turn the illustrated tiles. Find every matching pair.",
    "tournament": "Simulate the FIFA 2018 World Cup from its eight historical groups to the trophy.",
    "basketball": "Simulate the historical NBA playoff conferences to the champion.",
    "rpsls": "Five choices, ten winning combinations. Make your move.",
    "dice": "Roll illustrated dice, choose the sides and roll again.",
    "coin": "Flip the original photographic coin artwork.", "slots": "Match colourful symbols. No wagers or money.",
    "lottery": "A playful number draw. A simulation, never a prediction.",
    "guess": "Use the clues to find the hidden number.",
    "monitor": "Live CPU, memory, temperature, storage and Raspberry Pi health.",
    "sky": "Your sunrise, sunset and Moon, calculated on this computer.",
    "password": "Create a strong password locally, reveal it and copy it.",
    "temperature": "Celsius, Fahrenheit and Kelvin in one place.",
    "days": "Compare dates with a proper calendar and local dates.",
    "connect": "Understand your local interfaces, addresses and route.",
    "alarm": "Set a countdown, pause it and hear when time is up.",
    "speech": "Let your computer read text aloud, with a stop button.",
    "doctor": "Check the desktop and find useful explanations.",
    "info": "Hardware, system and the Daylight version.",
}
WORDS = {
 "en": {"home":"Home", "apps":"Applications", "games":"Games", "settings":"Settings", "launcher":"Find an application", "welcome":"First steps", "telemetry":"Privacy & statistics", "tools":"EVERYDAY TOOLS", "play":"A LITTLE TIME TO PLAY", "title":"A brighter desktop.", "subtitle":"Small native applications, thoughtfully brought together.", "open":"Open", "search":"Search installed applications…", "back":"Back", "saved":"Settings saved", "language":"Language", "finish":"Start exploring", "welcome_title":"Welcome to Daylight", "welcome_text":"Make yourself comfortable. These choices belong to your Daylight session.", "never":"Do not show this welcome again", "keyboard":"Keyboard layout", "privacy":"Boot statistics are optional and disabled on new installations."},
 "fr": {"home":"Accueil", "apps":"Applications", "games":"Jeux", "settings":"Réglages", "launcher":"Rechercher une application", "welcome":"Premiers pas", "telemetry":"Confidentialité et statistiques", "tools":"LES OUTILS DU QUOTIDIEN", "play":"UN MOMENT POUR JOUER", "title":"Un bureau qui rayonne.", "subtitle":"De petites applications natives réunies avec soin.", "open":"Ouvrir", "search":"Rechercher parmi les applications installées…", "back":"Retour", "saved":"Réglages enregistrés", "language":"Langue", "finish":"Découvrir Daylight", "welcome_title":"Bienvenue dans Daylight", "welcome_text":"Installez-vous confortablement. Ces choix concernent votre session Daylight.", "never":"Ne plus afficher cet accueil", "keyboard":"Disposition du clavier", "privacy":"Les statistiques de démarrage sont facultatives et désactivées à l’installation."},
 "de": {"home":"Start", "apps":"Anwendungen", "games":"Spiele", "settings":"Einstellungen", "launcher":"Anwendung suchen", "welcome":"Erste Schritte", "telemetry":"Datenschutz und Statistik", "tools":"WERKZEUGE FÜR DEN ALLTAG", "play":"ZEIT ZUM SPIELEN", "title":"Ein heller Desktop.", "subtitle":"Kleine native Anwendungen, sorgfältig vereint.", "open":"Öffnen", "search":"Installierte Anwendungen durchsuchen…", "back":"Zurück", "saved":"Einstellungen gespeichert", "language":"Sprache", "finish":"Daylight entdecken", "welcome_title":"Willkommen bei Daylight", "welcome_text":"Richten Sie sich ein. Diese Auswahl gilt für Ihre Daylight-Sitzung.", "never":"Diesen Startbildschirm nicht mehr anzeigen", "keyboard":"Tastaturbelegung", "privacy":"Startstatistiken sind freiwillig und bei neuen Installationen ausgeschaltet."},
}


def games_installed():
    return (RESOURCE_ROOT / "games.enabled").is_file() or (ROOT.parent / "Cargo.toml").is_file()


def daylight_binary():
    installed = shutil.which("daylight")
    if installed:
        return installed
    for candidate in (ROOT.parent / "target/debug/daylight", ROOT.parent / "target/x86_64-unknown-linux-musl/release/daylight", ROOT.parent / "target/aarch64-unknown-linux-musl/release/daylight"):
        if candidate.is_file():
            return str(candidate)
    return "daylight"


def daylight_call(*arguments):
    return subprocess.run([daylight_binary(), *arguments], capture_output=True, text=True, timeout=8)


def local_time(values):
    try:
        return dt.datetime.now(ZoneInfo(str(values.get("timezone", "Europe/Zurich"))))
    except (ValueError, KeyError):
        return dt.datetime.now().astimezone()


def solar_period(values):
    now = local_time(values)
    try:
        from .sky import calculate_sun
        sun = calculate_sun(now.date(), float(values["latitude"]), float(values["longitude"]), str(values["timezone"]))
        if sun.get("polar_state") == "polar_day": return "day"
        if sun.get("polar_state") == "polar_night": return "night"
        sunrise, sunset = sun["sunrise"], sun["sunset"]
        if sunrise and sunset:
            if now < sunrise or now >= sunset: return "night"
            if now < sunrise + dt.timedelta(hours=1): return "morning"
            if now >= sunset - dt.timedelta(hours=1): return "evening"
            return "day"
    except (ImportError, ValueError, KeyError, TypeError):
        pass
    return "night" if now.hour < 7 or now.hour >= 20 else "day"


def effective_appearance(values):
    return ("dark" if solar_period(values) == "night" else "light") if values.get("appearance") == "automatic" else values.get("appearance", "light")


def wallpaper_path(values=None):
    values = state.load_ui() if values is None else values
    if values.get("wallpaper_mode") == "daylight":
        choice = {"night":"daylight-night.jpg", "morning":"daylight-sunrise.jpg", "day":"daylight-mountains.jpg", "evening":"daylight-himalaya.jpg"}[solar_period(values)]
    elif values.get("custom_wallpaper") and Path(values["custom_wallpaper"]).is_file():
        return Path(values["custom_wallpaper"])
    else:
        choice = state.read_core().get("wallpaper", "daylight-mountains.jpg")
    return WALLPAPER_ROOT / choice


def display_alive():
    if state.session_kind() == "wayland":
        display = Path(os.environ.get("WAYLAND_DISPLAY", ""))
        if not display.is_absolute():
            display = Path(os.environ.get("XDG_RUNTIME_DIR", "")) / display
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(.5)
                connection.connect(str(display))
            return True
        except OSError:
            return False
    return state.x11_display_alive()


def appearance_session():
    """Own this Daylight display's background and Conky, including RC3 handoff."""
    if not state.daylight_session():
        return
    descriptor = state.acquire_session_lock()
    if descriptor is None:
        return
    running = True
    monitor_process = None
    wallpaper_process = None
    wayland = state.session_kind() == "wayland"
    def stop(*_):
        nonlocal running
        running = False
    def stop_owned(process):
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    last_path, last_monitor, last_keyboard, last_health = None, None, None, 0.0
    try:
        if not display_alive():
            return
        allowed = state.handoff_legacy()
        while running:
            if time.monotonic() - last_health > 30:
                if not display_alive():
                    break
                last_health = time.monotonic()
            values, core = state.load_ui(), state.read_core()
            keyboard = (values["keyboard_layout"], values["keyboard_variant"])
            if keyboard != last_keyboard:
                # setxkbmap controls only X11. Never pretend it configures a
                # Wayland compositor or touch the session-defaults package.
                if not wayland:
                    state.apply_keyboard(values)
                last_keyboard = keyboard
            path = wallpaper_path(values)
            if path != last_path and allowed["wallpaper"]:
                try:
                    if path.is_file():
                        if wayland and shutil.which("swaybg"):
                            stop_owned(wallpaper_process)
                            wallpaper_process = subprocess.Popen(
                                ["swaybg", "-m", "fill", "-i", str(path)],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        elif not wayland and shutil.which("feh"):
                            subprocess.run(["feh", "--no-fehbg", "--bg-max", str(path)],
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                           timeout=5, check=False)
                except (OSError, subprocess.TimeoutExpired):
                    pass
                last_path = path
            monitor = (core["monitor"], core["profile"])
            if monitor != last_monitor and allowed["conky"]:
                stop_owned(monitor_process)
                monitor_process = None
                if core["monitor"] == "on" and shutil.which("conky"):
                    try:
                        # Both renderers consume the generated user profile.
                        # Wayland's installed wrapper is only the entry point.
                        ready = daylight_call("setup-session").returncode == 0
                        if wayland:
                            ready = ready and Path("/usr/share/daylight/ui/conky-wayland.lua").is_file()
                        if ready:
                            monitor_process = state.start_conky(wayland=wayland)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                last_monitor = monitor
            for _ in range(4):
                if not running:
                    break
                time.sleep(.5)
    finally:
        stop_owned(monitor_process)
        stop_owned(wallpaper_process)
        os.close(descriptor)


class Desktop(tk.Tk):
    def __init__(self, page="home"):
        super().__init__()
        windowing.prepare(self)
        self.values = state.load_ui()
        self.title("Daylight GNU/Linux")
        self.geometry("1060x760")
        self.minsize(760, 540)
        theme.apply(self, effective_appearance(self.values), self.values["text_scale"])
        self.current_page = page
        self.images = []
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.bind("<Control-f>", lambda _: self.show("launcher"))
        self.bind("<Control-Home>", lambda _: self.show("home"))
        self.bind("<Escape>", lambda _: self.show("home") if self.current_page not in ("home", "welcome") else self.destroy())
        self.sidebar = tk.Frame(self, bg=theme.PALETTE["night"], width=204)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self.build_sidebar()
        workspace = ttk.Frame(self)
        workspace.pack(fill="both", expand=True)
        top = ttk.Frame(workspace, padding=(26, 19))
        top.pack(fill="x")
        self.breadcrumb = ttk.Label(top, text="", style="Heading.TLabel")
        self.breadcrumb.pack(side="left")
        ttk.Button(top, text="⌕  Ctrl+F", command=lambda:self.show("launcher")).pack(side="right")
        ttk.Separator(workspace).pack(fill="x")
        self.canvas = tk.Canvas(workspace, bg=theme.PALETTE["bg"], highlightthickness=0)
        self.scroll = ttk.Scrollbar(workspace, command=self.canvas.yview)
        self.scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.content = ttk.Frame(self.canvas, padding=(26, 20, 26, 30))
        self.content_window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda _:self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e:self.canvas.itemconfigure(self.content_window, width=e.width))
        self.bind_all("<MouseWheel>", self.wheel, add=True)
        self.bind_all("<Button-4>", lambda e:self.canvas.yview_scroll(-3,"units"),add=True)
        self.bind_all("<Button-5>", lambda e:self.canvas.yview_scroll(3,"units"),add=True)
        self.show(page)
        self.last_appearance=effective_appearance(self.values)
        self.appearance_job=self.after(60000,self.appearance_tick)
        windowing.finish(self)

    def destroy(self):
        if hasattr(self,"appearance_job"):
            try:self.after_cancel(self.appearance_job)
            except tk.TclError:pass
        super().destroy()

    def appearance_tick(self):
        self.values=state.load_ui()
        appearance=effective_appearance(self.values)
        if appearance!=self.last_appearance:
            previous=dict(theme.PALETTE)
            theme.apply(self,appearance,self.values["text_scale"])
            replacements={value:theme.PALETTE[key] for key,value in previous.items()}
            self.recolor(self,replacements)
            # Future canvas redraws must use the same palette without rebuilding
            # a page: a game, timer or partially entered form keeps its state.
            palette_names={"INK":"ink","MUTED":"muted","PAPER":"panel",
                           "BACKGROUND":"bg","BG":"bg","PANEL":"panel",
                           "HAIR":"line","LINE":"line","NIGHT":"night",
                           "PURPLE":"accent","ACCENT":"accent"}
            for module_name in ("daylight_ui.games","daylight_ui.tools"):
                module=sys.modules.get(module_name)
                if module is not None:
                    for variable,key in palette_names.items():
                        if module_name=="daylight_ui.games" and variable=="PAPER":key="card"
                        if hasattr(module,variable):setattr(module,variable,theme.PALETTE[key])
                    if module_name=="daylight_ui.games":
                        # A game's canvas also has fixed light engravings on
                        # night/amber artwork. Repaint those semantic colours
                        # after generic widget recolouring, without resetting
                        # its model, timer, selections or pending animation.
                        for widget in self.content.winfo_children():
                            if isinstance(widget,module.GamePage):widget.redraw()
            self.last_appearance=appearance
        self.appearance_job=self.after(60000,self.appearance_tick)

    def recolor(self,widget,replacements):
        for option in ("background","foreground","insertbackground","highlightbackground",
                       "highlightcolor","activebackground","activeforeground"):
            try:
                value=str(widget.cget(option))
                if value in replacements:widget.configure(**{option:replacements[value]})
            except tk.TclError:pass
        if isinstance(widget,tk.Canvas):
            for item in widget.find_all():
                for option in ("fill","outline"):
                    try:
                        value=widget.itemcget(item,option)
                        if value in replacements:widget.itemconfigure(item,**{option:replacements[value]})
                    except tk.TclError:pass
        for child in widget.winfo_children():self.recolor(child,replacements)

    def input_fonts(self,widget):
        for child in widget.winfo_children():
            if isinstance(child,(ttk.Entry,ttk.Combobox)):
                if str(child.cget("font")) in ("TkTextFont","TkDefaultFont"):
                    child.configure(font=("DejaVu Sans",round(11*self.values["text_scale"])))
            self.input_fonts(child)

    def wheel(self, event):
        if not isinstance(event.widget, (ttk.Combobox, tk.Listbox, ttk.Treeview)):
            self.canvas.yview_scroll(-int(event.delta/120), "units")

    def word(self,key):
        return WORDS[self.values["language"]].get(key,key)

    def build_sidebar(self):
        for widget in self.sidebar.winfo_children(): widget.destroy()
        art=tk.Canvas(self.sidebar,width=190,height=98,bg=theme.PALETTE["night"],highlightthickness=0)
        art.pack(pady=(14,0))
        theme.emblem(art,37,42,28)
        art.create_text(76,35,text="DAYLIGHT",anchor="w",fill="#faf8f2",font=("DejaVu Sans",13,"bold"))
        art.create_text(76,56,text="GNU / LINUX",anchor="w",fill="#c0bfd0",font=("DejaVu Sans",8))
        pages=[("home","◈"),("apps","◇")]
        if games_installed(): pages.append(("games","♧"))
        pages += [("launcher","⌕"),("settings","⚙"),("welcome","☀"),("telemetry","◎")]
        for name,symbol in pages:
            b=tk.Button(self.sidebar,text=f"{symbol}   {self.word(name)}",anchor="w",wraplength=157,
                        justify="left",command=lambda n=name:self.show(n),relief="flat",bd=0,
                        bg=theme.PALETTE["night"],fg="#eeebe4",activebackground="#48405f",
                        activeforeground="white",font=("DejaVu Sans",10),padx=17,pady=12,
                        highlightthickness=1,highlightbackground=theme.PALETTE["night"],
                        highlightcolor="#c79a36",cursor="hand2")
            b.pack(fill="x",padx=10,pady=2)
        tk.Label(self.sidebar,text="Local. Native. Yours.",bg=theme.PALETTE["night"],fg="#c0bfd0",
                 font=("DejaVu Sans",9)).pack(side="bottom",pady=24)

    def save(self,changes):
        self.values=state.save_ui(changes)
        return self.values

    def show(self,name):
        if name in GAME_NAMES and not games_installed():
            messagebox.showinfo("Daylight Games","Install daylight-games to open the optional games.",parent=self)
            return
        self.current_page=name
        self.images=[]
        for widget in self.content.winfo_children(): widget.destroy()
        self.canvas.yview_moveto(0)
        self.breadcrumb.configure(text=self.word(name) if name in WORDS["en"] else TOOL_NAMES.get(name,GAME_NAMES.get(name,name)))
        context={"navigate":self.show,"language":self.values["language"],"state":self.values,"save_state":self.save}
        try:
            if name in ("home","apps","games"): self.library(name)
            elif name=="settings": self.settings()
            elif name=="welcome": self.welcome()
            elif name in ("telemetry", "privacy"): self.telemetry()
            elif name=="launcher": self.launcher()
            elif name=="shardturn": self.shardturn()
            elif name in GAME_NAMES:
                from . import games
                games.build(self.content,name,context)
            elif name in TOOL_NAMES:
                from . import tools
                tools.build(self.content,name,context)
            else: raise ValueError(f"Unknown application: {name}")
            self.input_fonts(self.content)
        except Exception as error:
            ttk.Label(self.content,text="This application could not open",style="Heading.TLabel").pack(anchor="w",pady=10)
            ttk.Label(self.content,text=str(error),wraplength=580).pack(anchor="w",pady=10)
            ttk.Button(self.content,text="Return home",command=lambda:self.show("home")).pack(anchor="w",pady=10)
            # Keep useful diagnostics for a terminal launch, never swallow a traceback.
            import traceback
            traceback.print_exc()

    def library(self,page):
        p=theme.PALETTE
        ttk.Label(self.content,text=self.word("title") if page=="home" else self.word(page),style="Title.TLabel",wraplength=500).pack(anchor="w",pady=(0,8))
        ttk.Label(self.content,text=self.word("subtitle"),style="Muted.TLabel",wraplength=490).pack(anchor="w",pady=(0,24))
        if page=="home":
            feature=theme.panel(self.content)
            feature.pack(fill="x",pady=(0,22))
            art=tk.Canvas(feature,width=85,height=73,bg=p["panel"],highlightthickness=0)
            art.pack(side="left",padx=(0,16))
            theme.emblem(art,40,31,36)
            ttk.Label(feature,text="Sun & Moon",style="Card.TLabel",font=("DejaVu Sans",18,"bold")).pack(anchor="w")
            ttk.Label(feature,text="Follow the daylight. Discover today's sky.",style="Card.TLabel",wraplength=330).pack(anchor="w",pady=6)
            ttk.Button(feature,text=self.word("open"),style="Accent.TButton",command=lambda:self.show("sky")).pack(anchor="w")
        entries=GAME_NAMES if page=="games" else TOOL_NAMES
        if page=="home": entries={k:TOOL_NAMES[k] for k in ("monitor","password","alarm","connect")}
        self.card_grid(self.content,entries)
        if page=="home" and games_installed():
            ttk.Label(self.content,text=self.word("play"),style="Heading.TLabel").pack(anchor="w",pady=(30,14))
            self.card_grid(self.content,{k:GAME_NAMES[k] for k in ("shardturn","cards","memory","tournament")})

    def card_grid(self,parent,entries):
        grid=ttk.Frame(parent)
        grid.pack(fill="x")
        cards=[]
        for slug,title in entries.items():
            card=theme.panel(grid,padding=16)
            icon=tk.Canvas(card,width=55,height=58,bg=theme.PALETTE["panel"],highlightthickness=0)
            icon.pack(anchor="w")
            theme.icon(icon,slug)
            ttk.Label(card,text=title,style="Card.TLabel",font=("DejaVu Sans",13,"bold")).pack(anchor="w",pady=(6,7))
            description=ttk.Label(card,text=DESCRIPTIONS.get(slug,""),style="Card.TLabel",wraplength=260,justify="left")
            description.pack(anchor="w",fill="x",pady=(0,14))
            ttk.Button(card,text=self.word("open")+"  →",command=lambda n=slug:self.show(n)).pack(anchor="w")
            cards.append((card,description))
        last_columns=[None]
        def layout(event=None):
            width=grid.winfo_width()
            columns=3 if width>=940 else 2 if width>=490 else 1
            if columns==last_columns[0]: return
            last_columns[0]=columns
            for i in range(3): grid.columnconfigure(i,weight=1 if i<columns else 0,uniform="cards" if i<columns else "")
            for index,(card,desc) in enumerate(cards):
                card.grid(row=index//columns,column=index%columns,sticky="nsew",padx=(0,12),pady=(0,12))
                desc.configure(wraplength=max(160,(max(width,490)//columns)-65))
        grid.bind("<Configure>",layout)

    def welcome(self):
        ttk.Label(self.content,text=self.word("welcome_title"),style="Title.TLabel",wraplength=500).pack(anchor="w",pady=(0,12))
        ttk.Label(self.content,text=self.word("welcome_text"),wraplength=490).pack(anchor="w",pady=(0,24))
        ttk.Label(self.content,text=self.word("language"),style="Heading.TLabel").pack(anchor="w")
        language=tk.StringVar(value={"en":"English","fr":"Français","de":"Deutsch"}[self.values["language"]])
        combo=ttk.Combobox(self.content,textvariable=language,state="readonly",values=("English","Français","Deutsch"),width=25)
        combo.pack(anchor="w",pady=10)
        combo.bind("<<ComboboxSelected>>",lambda _:self.change_language({"English":"en","Français":"fr","Deutsch":"de"}[language.get()],"welcome"))
        ttk.Label(self.content,text=self.word("keyboard"),style="Heading.TLabel").pack(anchor="w",pady=(16,6))
        keyboard=ttk.Frame(self.content)
        keyboard.pack(anchor="w")
        for index,(name,layout,variant) in enumerate([("Swiss French","ch","fr"),("Swiss German","ch",""),("French","fr",""),("US English","us","")]):
            ttk.Button(keyboard,text=name,command=lambda a=layout,b=variant:self.keyboard(a,b),state="disabled" if state.session_kind()=="wayland" else "normal").grid(row=index//2,column=index%2,sticky="ew",padx=(0,6),pady=6)
        keyboard_help=("Wayland keeps the keyboard layout from your base desktop. Change it in that desktop’s input settings." if state.session_kind()=="wayland" else "Remembered for Daylight X11 sessions. Your base system’s keyboard settings remain available for other desktops.")
        ttk.Label(self.content,text=keyboard_help,wraplength=490,style="Muted.TLabel").pack(anchor="w",pady=(0,18))
        privacy=theme.panel(self.content)
        privacy.pack(fill="x",pady=(0,12))
        ttk.Label(privacy,text=self.word("telemetry"),style="Card.TLabel",
                  font=("DejaVu Sans",14,"bold")).pack(anchor="w",pady=(0,6))
        ttk.Label(privacy,text=self.word("privacy"),style="Card.TLabel",
                  wraplength=450).pack(anchor="w",pady=5)
        # Present the actual opt-in state on the first-run page. No command is
        # executed without an explicit click and administrator confirmation.
        telemetry_path = Path("/etc/daylight/telemetry.conf")
        telemetry_installed = telemetry_path.is_file()
        try:
            telemetry_enabled = any(line.strip().lower() == "enabled=yes" for line in telemetry_path.read_text().splitlines())
        except OSError:
            telemetry_enabled = False
        status_text = {
            "en": "Boot statistics: {}", "fr": "Statistiques de démarrage : {}",
            "de": "Startstatistik: {}",
        }[self.values["language"]]
        state_text = ({"en": "Enabled", "fr": "Activées", "de": "Aktiviert"}
                      if telemetry_enabled else {"en": "Disabled", "fr": "Désactivées", "de": "Deaktiviert"})
        ttk.Label(privacy, text=status_text.format(state_text[self.values["language"]]),
                  style="Card.TLabel").pack(anchor="w", pady=(8, 5))
        if telemetry_installed:
            action = "off" if telemetry_enabled else "on"
            button_text = ({"en": "Disable boot statistics…", "fr": "Désactiver les statistiques…", "de": "Startstatistik deaktivieren…"}
                           if telemetry_enabled else {"en": "Enable boot statistics…", "fr": "Activer les statistiques…", "de": "Startstatistik aktivieren…"})
            def toggle_telemetry():
                command = "sudo daylight telemetry " + action
                if not messagebox.askyesno("Daylight telemetry", "Run this administrator command?\n\n" + command, parent=self):
                    return
                terminal = shutil.which("x-terminal-emulator") or shutil.which("xterm")
                if terminal:
                    subprocess.Popen([terminal, "-e", "sudo", daylight_binary(), "telemetry", action], start_new_session=True)
                else:
                    messagebox.showinfo("Daylight telemetry", "Run in a terminal:\n" + command, parent=self)
            ttk.Button(privacy, text=button_text[self.values["language"]],
                       command=toggle_telemetry).pack(anchor="w", pady=5)
        else:
            ttk.Label(privacy, text={"en": "Optional telemetry package is not installed.",
                                      "fr": "Le paquet facultatif de télémétrie n'est pas installé.",
                                      "de": "Das optionale Telemetriepaket ist nicht installiert."}[self.values["language"]],
                      style="Card.TLabel").pack(anchor="w", pady=5)
        ttk.Button(privacy,text={"en":"Review optional activation…",
                                 "fr":"Activer les statistiques (facultatif)…",
                                 "de":"Optionale Statistik aktivieren…"}[self.values["language"]],
                   command=lambda:self.show("telemetry")).pack(anchor="w",pady=9)
        card=theme.panel(self.content)
        card.pack(fill="x",pady=10)
        ttk.Label(card,text="A few useful shortcuts",style="Card.TLabel",font=("DejaVu Sans",14,"bold")).pack(anchor="w")
        shortcuts=(["Super + Space    Desktop menu", "Ctrl + F    Search inside Daylight", "Ctrl + Home    Daylight home", "Alt + Tab    Switch windows"] if state.session_kind()=="wayland" else ["Super + Enter    Terminal", "Super + Space    Search applications", "Ctrl + F    Search inside Daylight", "Super + P    Daylight library", "Super + E    Files", "Alt + Tab    Switch windows", "Right-click the desktop    Open the Fluxbox menu"])
        for line in shortcuts:
            ttk.Label(card,text=line,style="Card.TLabel",wraplength=440).pack(anchor="w",pady=4)
        never=tk.BooleanVar(value=True)
        ttk.Checkbutton(self.content,text=self.word("never"),variable=never).pack(anchor="w",pady=18)
        def finish():
            self.save({"welcome_completed":never.get()})
            self.show("home")
        ttk.Button(self.content,text=self.word("finish"),style="Accent.TButton",command=finish).pack(anchor="w")

    def change_language(self,language,page):
        self.save({"language":language})
        self.build_sidebar()
        self.show(page)

    def keyboard(self,layout,variant):
        if not state.valid_keyboard(layout,variant):
            raise ValueError("Unsupported keyboard layout or variant")
        executable=shutil.which("setxkbmap")
        if not executable:
            messagebox.showinfo("Keyboard","The base system's keyboard settings are available from System applications.",parent=self)
            return
        result=subprocess.run([executable,"-layout",layout,"-variant",variant],capture_output=True,text=True,timeout=5)
        if result.returncode:
            messagebox.showerror("Keyboard",result.stderr[:500] or "The layout could not be applied.",parent=self)
        else:
            self.save({"keyboard_layout":layout,"keyboard_variant":variant})

    def settings(self):
        ttk.Label(self.content,text=self.word("settings"),style="Title.TLabel",wraplength=500).pack(anchor="w",pady=(0,18))
        core=state.read_core()
        variables={k:tk.StringVar(value=core[k]) for k in ("monitor","fetch","profile")}
        controls=ttk.Frame(self.content)
        controls.pack(fill="x",pady=(0,16))
        for row,(key,title,options) in enumerate([("monitor","Desktop monitor",("on","off")),("fetch","Terminal system information",("on","off")),("profile","Conky profile",("balanced","minimal"))]):
            ttk.Label(controls,text=title,wraplength=480).grid(row=row*2,column=0,sticky="w",pady=(8,3))
            ttk.Combobox(controls,textvariable=variables[key],values=options,state="readonly",width=20).grid(row=row*2+1,column=0,sticky="w",pady=(0,8))
        ttk.Label(controls,text="Profiles update Daylight's standard monitor. Your custom conky.conf is preserved, including when you change profile.",style="Muted.TLabel",wraplength=480).grid(row=6,column=0,sticky="w",pady=(0,10))
        appearance=tk.StringVar(value=self.values["appearance"])
        wallpaper_mode=tk.StringVar(value=self.values["wallpaper_mode"])
        scale=tk.StringVar(value=str(self.values["text_scale"]))
        language=tk.StringVar(value=self.values["language"])
        for row,(title,var,options) in enumerate([("Appearance",appearance,("light","dark","automatic")),("Wallpaper mode",wallpaper_mode,("fixed","daylight")),("Text scale",scale,("0.9","1.0","1.15","1.3","1.5")),(self.word("language"),language,("en","fr","de"))],start=4):
            ttk.Label(controls,text=title,wraplength=480).grid(row=row*2,column=0,sticky="w",pady=(8,3))
            ttk.Combobox(controls,textvariable=var,values=options,state="readonly",width=20).grid(row=row*2+1,column=0,sticky="w",pady=(0,8))
        ttk.Label(self.content,text="Automatic appearance and daylight wallpaper follow the location saved in Sun & Moon. The default location is Fribourg, Switzerland.",style="Muted.TLabel",wraplength=490).pack(anchor="w",pady=(0,20))
        ttk.Label(self.content,text="Wallpaper",style="Heading.TLabel").pack(anchor="w",pady=(0,10))
        choices=ttk.Frame(self.content)
        choices.pack(fill="x")
        chosen=tk.StringVar(value=core["wallpaper"])
        for index,filename in enumerate(state.WALLPAPERS):
            cell=theme.panel(choices,padding=8)
            cell.grid(row=index//2,column=index%2,sticky="nsew",padx=(0,8),pady=(0,10))
            image_path=ROOT/"previews"/(Path(filename).stem+".png")
            if image_path.is_file():
                image=tk.PhotoImage(file=str(image_path))
                self.images.append(image)
                ttk.Label(cell,image=image,style="Card.TLabel").pack()
            else:
                preview=tk.Canvas(cell,width=175,height=92,bg="#292c49" if "night" in filename else "#d8decb",highlightthickness=0)
                preview.pack()
                theme.emblem(preview,88,45,45)
            ttk.Radiobutton(cell,text=Path(filename).stem.removeprefix("daylight-").title(),variable=chosen,value=filename).pack(anchor="w",pady=4)
        for col in range(2): choices.columnconfigure(col,weight=1)
        custom=tk.StringVar(value=self.values["custom_wallpaper"])
        ttk.Label(self.content,textvariable=custom,style="Muted.TLabel",wraplength=490).pack(anchor="w",pady=(4,8))
        actions=ttk.Frame(self.content)
        actions.pack(anchor="w",pady=(0,18))
        def select_custom():
            path=filedialog.askopenfilename(parent=self,title="Choose a wallpaper",filetypes=[("Pictures","*.png *.jpg *.jpeg *.webp *.bmp"),("All files","*")])
            if path: custom.set(path)
        ttk.Button(actions,text="Choose my picture…",command=select_custom).pack(anchor="w",pady=(0,8))
        ttk.Button(actions,text="Use selected Daylight wallpaper",command=lambda:custom.set("")).pack(anchor="w")
        status=tk.StringVar()
        def apply():
            try:
                previous=state.read_core()
                state.save_core({**{key:var.get() for key,var in variables.items()},"wallpaper":chosen.get()})
                if custom.get() and not Path(custom.get()).is_file(): raise ValueError("The selected picture is no longer available")
                self.save({"appearance":appearance.get(),"wallpaper_mode":wallpaper_mode.get(),"text_scale":float(scale.get()),"language":language.get(),"custom_wallpaper":custom.get()})
                state.ensure_session_manager()
                # The session appearance manager owns and refreshes its Conky process.
                theme.apply(self,effective_appearance(self.values),self.values["text_scale"])
                self.sidebar.configure(bg=theme.PALETTE["night"])
                self.canvas.configure(bg=theme.PALETTE["bg"])
                self.build_sidebar()
                self.show("settings")
                messagebox.showinfo("Daylight",self.word("saved"),parent=self)
            except (OSError,ValueError,subprocess.TimeoutExpired) as error:
                status.set(str(error))
        ttk.Button(self.content,text="Apply preferences",style="Accent.TButton",command=apply).pack(anchor="w")
        ttk.Label(self.content,textvariable=status,wraplength=490).pack(anchor="w",pady=10)
        ttk.Label(self.content,text="System settings",style="Heading.TLabel").pack(anchor="w",pady=(24,10))
        systems=ttk.Frame(self.content)
        systems.pack(anchor="w")
        for index,(title,candidates) in enumerate([("Sound",("pavucontrol","mate-volume-control","alsamixer")),("Network",("nm-connection-editor",)),("Bluetooth",("blueman-manager",)),("Displays",("arandr","lxrandr"))]):
            ttk.Button(systems,text=title,command=lambda t=title,c=candidates:self.system_tool(t,c)).grid(row=index//2,column=index%2,sticky="ew",padx=(0,8),pady=(0,8))

    def system_tool(self,title,candidates):
        command=next((shutil.which(c) for c in candidates if shutil.which(c)),None)
        if not command:
            messagebox.showinfo(title,"No compatible settings application is installed. Open your base system's settings from the application search.",parent=self)
            return
        if Path(command).name in ("alsamixer","raspi-config"):
            terminal=shutil.which("x-terminal-emulator") or shutil.which("xterm")
            if not terminal: return
            argv=[terminal,"-e",command]
        else: argv=[command]
        subprocess.Popen(argv,start_new_session=True)

    def launcher(self):
        ttk.Label(self.content,text=self.word("launcher"),style="Title.TLabel",wraplength=500).pack(anchor="w",pady=(0,18))
        query=tk.StringVar()
        entry=ttk.Entry(self.content,textvariable=query)
        entry.pack(fill="x",pady=(0,10))
        ttk.Label(self.content,text=self.word("search"),style="Muted.TLabel").pack(anchor="w",pady=(0,16))
        entries=launcher.discover(language=self.values["language"])
        shown=[]
        tree=ttk.Treeview(self.content,columns=("name","description"),show="headings",height=12,selectmode="browse")
        tree.heading("name",text="Application")
        tree.heading("description",text="Description")
        tree.column("name",width=180,minwidth=120,stretch=False)
        tree.column("description",width=260,minwidth=100)
        tree.pack(fill="both",expand=True)
        status=tk.StringVar()
        ttk.Label(self.content,textvariable=status,style="Muted.TLabel",wraplength=490).pack(anchor="w",pady=8)
        favorites=set(self.values["favorites"])
        def update(*_):
            tree.delete(*tree.get_children())
            terms=query.get().casefold().split()
            shown[:]=sorted((app for app in entries if all(term in (app.name+" "+app.description).casefold() for term in terms)),key=lambda app:(app.identifier not in favorites,app.name.casefold()))
            for index,app in enumerate(shown): tree.insert("","end",iid=str(index),values=(("★ " if app.identifier in favorites else "")+app.name,app.description))
            if shown: tree.selection_set("0")
            status.set(f"{len(shown)} applications · Enter to open · Ctrl+F to search")
        def selected():
            selection=tree.selection()
            return shown[int(selection[0])] if selection else None
        def launch(_=None):
            app=selected()
            if app:
                try: launcher.launch(app)
                except (OSError,RuntimeError) as error: messagebox.showerror("Application",str(error),parent=self)
        def favorite():
            app=selected()
            if app:
                if app.identifier in favorites: favorites.remove(app.identifier)
                else: favorites.add(app.identifier)
                self.save({"favorites":sorted(favorites)})
                update()
        actions=ttk.Frame(self.content)
        actions.pack(fill="x",pady=14)
        ttk.Button(actions,text=self.word("open"),style="Accent.TButton",command=launch).pack(side="left",padx=(0,8))
        ttk.Button(actions,text="☆  Toggle favourite",command=favorite).pack(side="left")
        query.trace_add("write",update)
        tree.bind("<Double-1>",launch)
        tree.bind("<Return>",launch)
        entry.bind("<Return>",launch)
        entry.bind("<Down>",lambda _:tree.focus_set())
        update()
        entry.focus_set()

    def telemetry(self):
        ttk.Label(self.content,text=self.word("telemetry"),style="Title.TLabel",wraplength=500).pack(anchor="w",pady=(0,18))
        ttk.Label(self.content,text=self.word("privacy"),wraplength=490).pack(anchor="w",pady=(0,16))
        values={}
        path=Path("/etc/daylight/telemetry.conf")
        try:
            for line in path.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    key,value=line.split("=",1); values[key.strip()]=value.strip()
        except OSError: pass
        panel=theme.panel(self.content)
        panel.pack(fill="x",pady=10)
        enabled=values.get("enabled")=="yes"
        ttk.Label(panel,text="Enabled" if enabled else "Disabled",style="Card.TLabel",font=("DejaVu Sans",24,"bold")).pack(anchor="w")
        ttk.Label(panel,text="Optional package installed" if path.is_file() else "Optional package not installed",style="Card.TLabel").pack(anchor="w",pady=8)
        if not path.is_file():
            ttk.Label(panel,text="To install: sudo apt install daylight-telemetry",style="Card.TLabel",wraplength=460).pack(anchor="w",pady=6)
        ttk.Label(self.content,text="The collector counts received boot events, not unique users. It does not receive your name, files, hostname, or a device identifier. The receiving web server can see your IP address.\n\nEnabling or disabling boot statistics is an administrator action. The command opens in a terminal so you can read it and enter your sudo password there.",wraplength=490,justify="left").pack(anchor="w",pady=20)
        command="sudo daylight telemetry off" if enabled else "sudo daylight telemetry on"
        ttk.Label(self.content,text=command,font=("DejaVu Sans Mono",12)).pack(anchor="w",pady=10)
        def change():
            if not path.is_file():
                messagebox.showinfo("Statistics","The optional telemetry package is not installed.\n\nInstall it with:\nsudo apt install daylight-telemetry\n\nInstallation does not enable telemetry automatically.",parent=self); return
            if not messagebox.askyesno("Boot statistics",f"Run this administrator command in a terminal?\n\n{command}",parent=self): return
            terminal=shutil.which("x-terminal-emulator") or shutil.which("xterm")
            if not terminal:
                messagebox.showinfo("Statistics",f"Open a terminal and run:\n{command}",parent=self); return
            subprocess.Popen([terminal,"-e","sudo",daylight_binary(),"telemetry","off" if enabled else "on"],start_new_session=True)
        ttk.Button(self.content,text="Disable boot statistics" if enabled else "Enable boot statistics…",command=change).pack(anchor="w",pady=8)
        ttk.Button(self.content,text="Refresh status",command=lambda:self.show("telemetry")).pack(anchor="w",pady=8)

    def shardturn(self):
        candidates=[RESOURCE_ROOT/"shardturn/Shardturn.py",ROOT.parent.parent/"shardturn/Shardturn.py",ROOT.parent/"desktop/shardturn/Shardturn.py"]
        path=next((p for p in candidates if p.is_file()),None)
        if not path: raise FileNotFoundError("Shardturn is not installed. Install daylight-games to add it.")
        ttk.Label(self.content,text="Shardturn",style="Title.TLabel",wraplength=500).pack(anchor="w",pady=12)
        ttk.Label(self.content,text=DESCRIPTIONS["shardturn"],wraplength=600).pack(anchor="w",pady=12)
        launch = ROOT / "shardturn_launcher.py"
        if not launch.is_file(): raise FileNotFoundError("The Daylight Shardturn launcher is not installed.")
        def play(): subprocess.Popen([sys.executable,str(launch)],start_new_session=True)
        ttk.Button(self.content,text="Play Shardturn",style="Accent.TButton",command=play).pack(anchor="w",pady=12)
        play()


def main(page="home",first_run=False):
    if first_run and state.load_ui()["welcome_completed"]:
        return 0
    application=Desktop("welcome" if first_run else page)
    application.mainloop()
    return 0
