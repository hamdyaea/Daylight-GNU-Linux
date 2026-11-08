"""The Daylight playroom: small offline games with original vector artwork.

Developer: Hamdy Abou El Anein — GPL-3.0-only.
"""
import math
import random
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from .game_models import Battle, Card, Memory, RPS_NAMES, ScoreLedger, Tournament, rps_result
from .historical_sports import nba_stages, world_cup_stages

PAGE_NAMES = {
    "dice": "Dice", "coin": "Coin flip", "lottery": "Lottery simulator",
    "rpsls": "Rock · Paper · Scissors · Lizard · Spock", "cards": "Battle cards",
    "tournament": "2018 World Cup", "basketball": "NBA Playoffs", "memory": "Memory",
    "slots": "Slot simulator", "guess": "Guess the number",
}
BG, PAPER, INK = "#e9e6df", "#fcfaf5", "#292a43"
PANEL, ON_NIGHT, ENGRAVING = "#eeebe4", "#fcfaf5", "#292a43"
MUTED, LINE, ACCENT = "#66667b", "#d7d2c8", "#6548a3"
CORAL, AMBER, JADE, IRIS, NIGHT = "#ce6655", "#c79a36", "#358d7d", "#7c6fbb", "#292c49"
COLORS = (CORAL, AMBER, JADE, IRIS)
RNG = random.SystemRandom()


def rounded(c, x, y, w, h, fill=None, outline=None, radius=14, **kw):
    fill = PAPER if fill is None else fill
    outline = LINE if outline is None else outline
    r = min(radius, w / 2, h / 2)
    return c.create_polygon(x+r, y, x+w-r, y, x+w, y, x+w, y+r,
                            x+w, y+h-r, x+w, y+h,
                            x+w-r, y+h, x+r, y+h, x, y+h,
                            x, y+h-r, x, y+r, x, y, smooth=True,
                            fill=fill, outline=outline, **kw)


def emblem(c, name, x, y, radius, color=None, background=None, **kw):
    """Recognisable original pictures; no emoji font or downloaded assets."""
    r = radius
    color = ACCENT if color is None else color
    background = PAPER if background is None else background
    if name == "sun":
        for i in range(12):
            a = i * math.pi / 6
            c.create_line(x+math.cos(a)*r*.72, y+math.sin(a)*r*.72,
                          x+math.cos(a)*r, y+math.sin(a)*r, fill=color, width=3, **kw)
        c.create_oval(x-r*.5, y-r*.5, x+r*.5, y+r*.5, fill=color, outline="", **kw)
    elif name == "moon":
        c.create_oval(x-r*.8, y-r*.8, x+r*.8, y+r*.8, fill=color, outline="", **kw)
        c.create_oval(x-r*.2, y-r, x+r*1.05, y+r*.45, fill=background, outline="", **kw)
    elif name == "mountain":
        c.create_polygon(x-r, y+r*.7, x-r*.15, y-r, x+r*.3, y-r*.15,
                         x+r*.5, y-r*.55, x+r, y+r*.7, fill=color, outline="", **kw)
        c.create_polygon(x-r*.15, y-r, x-r*.5, y-r*.3, x-r*.18, y-r*.47,
                         x+r*.1, y-r*.3, fill=background, outline="", **kw)
    elif name == "star":
        points = []
        for i in range(10):
            a = -math.pi/2+i*math.pi/5
            rr = r if i % 2 == 0 else r*.43
            points.extend((x+math.cos(a)*rr, y+math.sin(a)*rr))
        c.create_polygon(*points, fill=color, outline="", **kw)
    elif name == "leaf":
        c.create_polygon(x-r*.85, y+r*.7, x-r*.7, y-r*.5, x+r*.85, y-r*.8,
                         x+r*.7, y+r*.5, smooth=True, fill=color, outline="", **kw)
        c.create_line(x-r*.6, y+r*.5, x+r*.55, y-r*.5, fill=background, width=3, **kw)
    elif name == "diamond":
        c.create_polygon(x, y-r, x+r*.8, y, x, y+r, x-r*.8, y, fill=color, outline="", **kw)
        c.create_line(x-r*.45, y, x+r*.45, y, x, y+r*.65, x, y-r*.65,
                      fill=background, width=2, **kw)
    elif name == "flower":
        for i in range(6):
            a = i*math.pi/3
            xx, yy = x+math.cos(a)*r*.5, y+math.sin(a)*r*.5
            c.create_oval(xx-r*.37, yy-r*.37, xx+r*.37, yy+r*.37,
                          fill=color, outline="", **kw)
        c.create_oval(x-r*.25, y-r*.25, x+r*.25, y+r*.25, fill=background, outline="", **kw)
    else:
        for j in range(3):
            points = []
            for k in range(17):
                xx = x-r+k*r/8
                yy = y+(j-1)*r*.5+math.sin(k*math.pi/4)*r*.2
                points.extend((xx, yy))
            c.create_line(*points, fill=color, smooth=True, width=4, **kw)


class GamePage(tk.Frame):
    def __init__(self, parent, name, context=None):
        super().__init__(parent, bg=BG)
        self.name = name
        self.context = context or {}
        self.font_scale = float(self.context.get("state", {}).get("text_scale", 1.0))
        self.scores = ScoreLedger()
        self.score_data = self.scores.read()
        self.alive = True
        self.pending = set()
        self.fonts = []
        self.scene = lambda: None
        self.pack(fill="both", expand=True)
        self.bind("<Destroy>", self._destroy, add="+")
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", pady=(0, 12))
        self.heading = tk.Label(header, text=PAGE_NAMES[name], bg=BG, fg=INK,
                                font=("DejaVu Sans", round(23*self.font_scale), "bold"), anchor="w", justify="left")
        self.heading.pack(fill="x")
        self.description = tk.Label(header, bg=BG, fg=MUTED, anchor="w", justify="left",
                                    font=("DejaVu Sans", round(10*self.font_scale)), wraplength=780)
        self.description.pack(fill="x", pady=(5, 0))
        header.bind("<Configure>", lambda e: self.wrap_header(e.width))
        self.controls = tk.Frame(self, bg=BG)
        self.controls.pack(fill="x", pady=(0, 12))
        self.footer = tk.Frame(self, bg=BG)
        self.footer.pack(fill="x", pady=(0, 10))
        self.sports_page = name in ("basketball", "tournament")
        self.cv = tk.Canvas(self, bg=BG, height=520 if self.sports_page else 390, highlightthickness=0, takefocus=True)
        self.cv.pack(fill="x" if self.sports_page else "both", expand=not self.sports_page)
        self.cv.bind("<Configure>", lambda _e: self.redraw())
        self.cv.bind("<Button-1>", lambda _e: self.cv.focus_set(), add="+")
        self.status = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status, bg=BG, fg=INK, anchor="w", justify="left",
                                     wraplength=820, font=("DejaVu Sans", round(11*self.font_scale)))
        self.status_label.pack(fill="x", pady=(12, 0))
        self.score_label = tk.Label(self, bg=BG, fg=MUTED, anchor="w", justify="left",
                                    font=("DejaVu Sans", round(10*self.font_scale)), wraplength=820)
        getattr(self, "setup_"+name)()
        self.show_record()
        self.later(0, self.redraw)

    def show_record(self, refresh=True):
        if refresh:
            self.score_data = self.scores.read()
        entry = self.score_data.get(self.name)
        if entry is None:
            return
        if self.name in ("memory", "guess"):
            unit = "moves" if self.name == "memory" else "guesses"
            text = f"Local best: {entry['best']} {unit}" if entry["best"] else "Local best: complete a game to record your first score."
        elif self.name == "slots":
            text = f"Local record: {entry['spins']} spins · {entry['matches']} picture matches"
        else:
            text = f"Local record: {entry['wins']} wins · {entry['losses']} losses · {entry['draws']} draws"
        self.score_label.configure(text=text)
        self.score_label.pack(fill="x", pady=(5, 0))

    def save_score(self, game, outcome=None, value=None):
        try:
            self.score_data = self.scores.record(game, outcome, value)
            self.show_record(refresh=False)
        except OSError:
            self.score_label.configure(text="The game continues, but the local score could not be saved.")
            self.score_label.pack(fill="x", pady=(5, 0))

    def wrap_header(self, width):
        self.heading.configure(wraplength=max(200, width-8))
        self.description.configure(wraplength=max(200, width-8))

    def _destroy(self, event):
        if event.widget is self:
            self.alive = False
            for item in self.pending:
                try:
                    self.after_cancel(item)
                except tk.TclError:
                    pass
            self.pending.clear()

    def later(self, ms, callback):
        def invoke():
            self.pending.discard(job)
            if self.alive:
                callback()
        job = self.after(ms, invoke)
        self.pending.add(job)
        return job

    def button(self, text, command, primary=False, parent=None):
        b = ttk.Button(parent or self.footer, text=text, command=command,
                       style="Accent.TButton" if primary else "TButton")
        b.pack(side="left", padx=(0, 8), pady=3)
        return b

    def field(self, label, value, width=10, parent=None):
        parent = parent or self.controls
        tk.Label(parent, text=label, bg=BG, fg=MUTED, font=("DejaVu Sans", 10)).pack(side="left", padx=(0, 6))
        var = tk.StringVar(value=value)
        entry = ttk.Entry(parent, textvariable=var, width=width)
        entry.pack(side="left", padx=(0, 15), ipady=4)
        return var, entry

    def text(self, x, y, value, size=15, fill=None, weight="normal", **kw):
        size = max(8, round(size*self.font_scale))
        item = self.cv.create_text(x, y, text=value, fill=INK if fill is None else fill,
                                   font=("DejaVu Sans", size, weight), **kw)
        self.fonts.append((item, size, weight))
        return item

    def redraw(self):
        if not self.alive:
            return
        self.cv.delete("all")
        self.fonts.clear()
        self.scene()
        if self.sports_page:
            # This game lives inside the shell's scrollable frame: expanding a
            # canvas there can collapse it to the height of a single line.
            # Give the board its own stable viewport and scale horizontally.
            width = max(self.cv.winfo_width(), 200)
            scale = min(1.0, width / 900)
            if scale != 1.0:
                self.cv.scale("all", 0, 0, scale, scale)
                for item, size, weight in self.fonts:
                    self.cv.itemconfigure(item, font=("DejaVu Sans", max(9, round(size * scale)), weight))
            bounds = self.cv.bbox("all")
            if bounds:
                self.cv.configure(scrollregion=(0, 0, max(width, bounds[2] + 16), max(520, bounds[3] + 20)))
            return
        w, h = max(self.cv.winfo_width(), 200), max(self.cv.winfo_height(), 200)
        desired_height = max(240, min(390, round(w*440/900)))
        if int(self.cv.cget("height")) != desired_height:
            self.cv.configure(height=desired_height)
        self.status_label.configure(wraplength=max(200, w-8))
        self.score_label.configure(wraplength=max(200, w-8))
        scale = min(w/900, h/440)
        self.cv.scale("all", 0, 0, scale, scale)
        self.cv.move("all", (w-900*scale)/2, (h-440*scale)/2)
        for item, size, weight in self.fonts:
            self.cv.itemconfigure(item, font=("DejaVu Sans", max(8, round(size*scale)), weight))

    def art_card(self, card, x, y, width=100, height=145, face_up=True, tag=None):
        tags = (tag,) if tag else ()
        rounded(self.cv, x+3, y+5, width, height, fill=LINE, outline="", tags=tags)
        rounded(self.cv, x, y, width, height, fill=PAPER if face_up else NIGHT, tags=tags)
        if not face_up:
            self.cv.create_polygon(x+width/2, y+height*.18, x+width*.82, y+height/2,
                                   x+width/2, y+height*.82, x+width*.18, y+height/2,
                                   fill="", outline=IRIS, width=2, tags=tags)
            emblem(self.cv, "sun", x+width/2, y+height/2, width*.18, AMBER, NIGHT, tags=tags)
            return
        color = CORAL if card.suit in ("♥", "♦") else INK
        self.text(x+13, y+18, card.label, 17, color, "bold", tags=tags)
        self.text(x+width-13, y+height-18, card.label, 17, color, "bold", tags=tags)
        self.text(x+width/2, y+height/2+2, card.suit, 40, color, tags=tags)

    def setup_dice(self):
        self.description.configure(text="Roll a handful of dice. Six-sided dice use hand-drawn pips; other shapes show their value.")
        self.sides, e = self.field("Sides", "6", 6)
        self.count, e = self.field("Dice", "2", 6)
        self.values = [1, 6]
        self.button("Roll dice", self.roll_dice, True)
        self.cv.bind("<space>", lambda _e: self.roll_dice())
        self.scene = self.draw_dice
        self.status.set("Space rolls again · No stake, just chance.")

    def roll_dice(self):
        try:
            sides, count = int(self.sides.get()), int(self.count.get())
            if not 2 <= sides <= 1000000 or not 1 <= count <= 12:
                raise ValueError
        except ValueError:
            self.status.set("Use 2–1,000,000 sides and 1–12 dice.")
            return
        self.values = [RNG.randrange(1, sides+1) for _ in range(count)]
        self.status.set(f"Total {sum(self.values)} · {len(self.values)} dice · {sides} sides")
        self.redraw()

    def draw_dice(self):
        n = len(self.values)
        columns = min(n, 6)
        rows = math.ceil(n/columns)
        size, gap = 108, 22
        for i, value in enumerate(self.values):
            row, col = divmod(i, columns)
            row_count = min(columns, n-row*columns)
            x = (900-row_count*(size+gap)+gap)/2+col*(size+gap)
            y = (440-rows*(size+gap)+gap)/2+row*(size+gap)
            rounded(self.cv, x+3, y+6, size, size, fill=LINE, outline="")
            rounded(self.cv, x, y, size, size, fill=PAPER, outline=IRIS, radius=18, width=2)
            try:
                six = int(self.sides.get()) == 6
            except ValueError:
                six = False
            if six and value <= 6:
                positions = {1:[(1,1)],2:[(0,0),(2,2)],3:[(0,0),(1,1),(2,2)],
                             4:[(0,0),(2,0),(0,2),(2,2)],5:[(0,0),(2,0),(1,1),(0,2),(2,2)],
                             6:[(0,0),(0,1),(0,2),(2,0),(2,1),(2,2)]}[value]
                for px, py in positions:
                    xx, yy = x+26+px*28, y+26+py*28
                    self.cv.create_oval(xx-6, yy-6, xx+6, yy+6, fill=INK, outline="")
            else:
                self.text(x+size/2, y+size/2, str(value), 25 if value < 1000 else 16, ACCENT, "bold")

    def setup_coin(self):
        self.description.configure(text="Flip a real coin image: the original heads and tails artwork, preserved from the classic game.")
        self.coin = "Ready"
        self.flips = [0, 0]
        assets = Path("/usr/share/daylight/game_assets/coin")
        if not assets.is_dir():
            assets = Path(__file__).resolve().parents[1] / "game_assets/coin"
        self.coin_faces = {
            side: tk.PhotoImage(file=str(assets / filename))
            for side, filename in (("Ready", "full.png"), (0, "face.png"), (1, "pile.png"))
        }
        self.button("Flip coin", self.flip_coin, True)
        self.button("Reset", self.reset_coin)
        self.cv.bind("<space>", lambda _e: self.flip_coin())
        self.scene = self.draw_coin
        self.status.set("Heads or tails? Ready to flip.")

    def reset_coin(self):
        self.coin = "Ready"
        self.flips = [0, 0]
        self.status.set("Ready to flip.")
        self.redraw()

    def flip_coin(self):
        self.coin = RNG.randrange(2)
        self.flips[self.coin] += 1
        self.status.set(f"{'Heads' if self.coin == 0 else 'Tails'} · Heads {self.flips[0]} · Tails {self.flips[1]}")
        self.redraw()

    def draw_coin(self):
        art = self.coin_faces[self.coin]
        rounded(self.cv, 275, 40, 350, 295, fill=PAPER, radius=23)
        self.cv.create_image(450, 192, image=art)
        label = "FLIP THE COIN" if self.coin == "Ready" else "HEADS" if self.coin == 0 else "TAILS"
        self.text(450, 367, label, 26, INK, "bold")

    def setup_lottery(self):
        self.description.configure(text="Five different numbers from 1–50 and two stars from 1–12. An offline entertainment simulation.")
        self.lottery_values = sorted(RNG.sample(range(1, 51), 5))
        self.stars = sorted(RNG.sample(range(1, 13), 2))
        self.button("Draw again", self.draw_lottery_values, True)
        self.scene = self.draw_lottery
        self.status.set("Random combinations do not predict lottery results. No money is involved.")

    def draw_lottery_values(self):
        self.lottery_values = sorted(RNG.sample(range(1, 51), 5))
        self.stars = sorted(RNG.sample(range(1, 13), 2))
        self.redraw()

    def draw_lottery(self):
        self.text(450, 58, "YOUR DRAW", 13, MUTED, "bold")
        for i, value in enumerate(self.lottery_values):
            x = 190+i*130
            self.cv.create_oval(x-49, 115, x+49, 213, fill=PAPER, outline=LINE, width=2)
            self.cv.create_arc(x-49, 115, x+49, 213, start=25, extent=130, outline=IRIS, style="arc", width=4)
            self.text(x, 164, value, 31, INK, "bold")
        self.text(450, 266, "LUCKY STARS", 12, MUTED, "bold")
        for i, value in enumerate(self.stars):
            x = 390+i*120
            emblem(self.cv, "star", x, 341, 48, AMBER)
            self.text(x, 341, value, 18, ENGRAVING, "bold")

    def setup_rpsls(self):
        self.description.configure(text="Choose a shape. Each choice beats two others. The computer chooses independently.")
        self.rps_choice, self.rps_opponent = None, None
        self.rps_scores = [0, 0, 0]
        choices = [ttk.Button(self.controls, text=name, command=lambda n=i: self.play_rps(n))
                   for i, name in enumerate(RPS_NAMES)]
        def arrange(event=None):
            width = self.controls.winfo_width()
            columns = 5 if width > 670 else 3 if width > 390 else 2
            for i, button in enumerate(choices):
                button.grid(row=i//columns, column=i%columns, padx=(0, 6), pady=3, sticky="ew")
            for i in range(5):
                self.controls.columnconfigure(i, weight=1 if i < columns else 0)
        self.controls.bind("<Configure>", arrange)
        arrange()
        self.scene = self.draw_rps
        self.status.set("Rock crushes scissors and lizard · Paper covers rock and disproves Spock.")

    def play_rps(self, choice):
        self.rps_choice, self.rps_opponent = choice, RNG.randrange(5)
        result = rps_result(self.rps_choice, self.rps_opponent)
        self.rps_scores[{"You win":0, "Computer wins":1, "Draw":2}[result]] += 1
        self.save_score("rpsls", {"You win":"win", "Computer wins":"loss", "Draw":"draw"}[result])
        self.status.set(f"{result} · You {self.rps_scores[0]} · Computer {self.rps_scores[1]} · Draws {self.rps_scores[2]}")
        self.redraw()

    def rps_art(self, choice, x, y):
        if choice is None:
            self.text(x, y, "?", 75, IRIS, "bold")
        elif choice == 0:
            self.cv.create_polygon(x-56,y+26,x-45,y-33,x-8,y-53,x+40,y-30,x+60,y+18,x+17,y+52,
                                   fill=MUTED, outline=INK, width=3)
            self.cv.create_line(x-45,y-33,x-4,y-5,x+40,y-30, fill=PAPER, width=3)
        elif choice == 1:
            rounded(self.cv,x-42,y-62,84,124,PAPER,IRIS,8,width=3)
            for yy in range(-35, 46, 16):
                self.cv.create_line(x-24,y+yy,x+24,y+yy,fill=IRIS,width=2)
        elif choice == 2:
            for yy in (-31, 31):
                self.cv.create_oval(x-57,y+yy-18,x-19,y+yy+18,outline=CORAL,width=8)
                self.cv.create_line(x-21,y+yy,x+60,y-yy,fill=INK,width=9)
            self.cv.create_oval(x-6,y-6,x+6,y+6,fill=AMBER,outline="")
        elif choice == 3:
            self.cv.create_oval(x-44,y-16,x+35,y+18,fill=JADE,outline="")
            self.cv.create_oval(x+20,y-28,x+62,y+10,fill=JADE,outline="")
            self.cv.create_oval(x+47,y-23,x+52,y-18,fill=INK,outline="")
            self.cv.create_line(x-37,y,x-62,y-20,x-80,y-6,fill=JADE,width=9,smooth=True)
            for sign in (-1,1):
                for xx in (-20,20):
                    self.cv.create_line(x+xx,y+sign*10,x+xx-12,y+sign*39,x+xx+5,y+sign*43,fill=JADE,width=6)
        else:
            self.cv.create_polygon(x-36,y+54,x-60,y-4,x-44,y-17,x-22,y+9,x-28,y-61,x-13,y-65,
                                   x,y-12,x+17,y-68,x+33,y-64,x+18,y+3,x+43,y-33,x+58,y-25,x+37,y+46,
                                   fill=IRIS,outline=ACCENT,width=2)

    def draw_rps(self):
        for x, choice, label in [(260,self.rps_choice,"YOU"),(640,self.rps_opponent,"COMPUTER")]:
            rounded(self.cv,x-140,65,280,285)
            self.text(x,102,label,12,MUTED,"bold")
            self.rps_art(choice,x,208)
            if choice is not None:
                self.text(x,313,RPS_NAMES[choice],19,INK,"bold")
        self.text(450,211,"VS",17,MUTED,"bold")

    def setup_cards(self):
        self.description.configure(text="Full 52-card battle · A > K > Q > J > 10 … 2 · Equal ranks start a battle: face down, then face up.")
        self.battle = Battle()
        self.battle_recorded = False
        self.next_battle = self.button("Reveal cards", self.advance_battle, True)
        self.button("New game", self.new_battle)
        self.cv.bind("<space>", lambda _e: self.advance_battle())
        self.scene = self.draw_battle
        self.status.set(self.battle.message)

    def new_battle(self):
        self.battle = Battle()
        self.battle_recorded = False
        self.next_battle.configure(state="normal", text="Reveal cards")
        self.status.set(self.battle.message)
        self.show_record()
        self.redraw()

    def advance_battle(self):
        self.battle.advance()
        b = self.battle
        if b.phase == "finished" and not self.battle_recorded:
            self.battle_recorded = True
            self.save_score("cards", "win" if b.winner == 0 else "loss" if b.winner == 1 else "draw")
        self.status.set(b.message)
        self.next_battle.configure(text={"battle":"Continue battle", "collect":f"Collect {len(b.pot)} cards", "ready":"Next pair", "finished":"Game finished"}[b.phase],
                                   state="disabled" if b.phase == "finished" else "normal")
        self.redraw()

    def draw_battle(self):
        b = self.battle
        self.text(26,23,f"YOU  ·  {len(b.hands[0])} cards",14,JADE,"bold",anchor="w")
        self.text(874,23,f"COMPUTER  ·  {len(b.hands[1])} cards",14,CORAL,"bold",anchor="e")
        self.text(450,23,f"Round {b.rounds}  ·  Battles {b.battles}",11,MUTED)
        rounded(self.cv,20,55,860,270,fill=PANEL,outline=LINE)
        for owner in (0,1):
            cards = [(card, up) for who,card,up in b.table if who == owner]
            shown = cards[-8:]
            width, gap = (92,39) if len(shown)>3 else (110,65)
            left = 70 if owner == 0 else 500
            if not shown:
                self.art_card(Card(2,"♠"),left+96,105,110,160,False)
            else:
                for j,(card,up) in enumerate(shown):
                    self.art_card(card,left+j*gap,110,width,155,up)
                if len(cards)>8:
                    self.text(left,297,f"+ {len(cards)-8} earlier cards in this battle",10,MUTED,anchor="w")
        if b.phase == "collect":
            self.text(450,348,("YOU" if b.pending_winner == 0 else "COMPUTER")+f" TAKE {len(b.pot)} CARDS",15,ACCENT,"bold")
            columns = min(26, len(b.pot))
            gap = min(35, 810/max(columns, 1))
            x0 = (900-(columns-1)*gap)/2
            for i, card in enumerate(b.pot):
                row, col = divmod(i, columns)
                self.text(x0+col*gap,385+row*31,card.label+card.suit,11,
                          CORAL if card.suit in "♥♦" else INK,"bold")
        elif b.phase == "battle":
            self.text(450,373,"BATTLE",28,CORAL,"bold")
            self.text(450,412,f"{len(b.pot)} cards on the table · Space continues",11,MUTED)
        elif b.phase == "finished":
            emblem(self.cv,"star",450,374,22,AMBER)
            self.text(450,418,"YOU WIN" if b.winner == 0 else "DRAW" if b.winner is None else "COMPUTER WINS",18,ACCENT,"bold")
        else:
            self.text(450,377,f"{b.card_count()} cards accounted for · Space reveals the next pair",12,MUTED)

    def setup_tournament(self):
        self.description.configure(text="FIFA World Cup 2018: the real 32 national teams in their original eight groups, followed by the original knockout bracket. Match results are simulated.")
        self.tournament_stages = []
        self.tournament_index = 0
        self.button("New 2018 World Cup", self.new_tournament)
        self.tournament_next = self.button("Next stage", self.advance_tournament, True)
        self.tournament_scroll = ttk.Scrollbar(self.cv, orient="vertical", command=self.cv.yview)
        self.tournament_scroll.pack(side="right", fill="y")
        self.cv.configure(yscrollcommand=self.tournament_scroll.set)
        self.scene = self.draw_tournament
        self.new_tournament()

    def new_tournament(self):
        self.tournament_stages = world_cup_stages()
        self.tournament_index = 0
        self.tournament_next.configure(state="normal", text="Play round of 16")
        self.status.set("World Cup 2018 · Eight real groups of four teams · Top two in each group advance. Simulated results.")
        self.cv.yview_moveto(0)
        self.redraw()

    def advance_tournament(self):
        if self.tournament_index >= len(self.tournament_stages) - 1:
            return
        self.tournament_index += 1
        stage = self.tournament_stages[self.tournament_index]
        self.status.set("2018 World Cup · " + stage["title"] + " · Fictional simulation, not historical results.")
        if stage["kind"] == "champion":
            self.tournament_next.configure(text="Tournament complete", state="disabled")
        else:
            upcoming = self.tournament_stages[self.tournament_index + 1]["title"]
            self.tournament_next.configure(text="Show " + upcoming, state="normal")
        self.cv.yview_moveto(0)
        self.redraw()

    def draw_tournament(self):
        if not self.tournament_stages:
            return
        stage = self.tournament_stages[self.tournament_index]
        self.text(24, 25, stage["title"].upper(), 19, ACCENT, "bold", anchor="w")
        if stage["kind"] == "world_groups":
            self.cv.configure(scrollregion=(0, 0, 900, 885))
            for i, (group, names) in enumerate(stage["groups"]):
                x, y = 22 + i % 2 * 448, 55 + i // 2 * 204
                rounded(self.cv, x, y, 421, 189, fill=PAPER, radius=14)
                self.text(x+17, y+25, "GROUP " + group, 14, ACCENT, "bold", anchor="w")
                for j, name in enumerate(names):
                    self.text(x+19, y+59+j*31, name, 13, INK if j < 2 else MUTED,
                              "bold" if j < 2 else "normal", anchor="w")
                    if j < 2:
                        self.text(x+395, y+59+j*31, "Q", 11, JADE, "bold", anchor="e")
        elif stage["kind"] == "champion":
            self.cv.configure(scrollregion=(0, 0, 900, 420))
            emblem(self.cv, "star", 450, 165, 68, AMBER)
            self.text(450, 280, stage["winner"], 27, INK, "bold")
            self.text(450, 332, "2018 WORLD CUP WINNER · SIMULATION", 12, MUTED)
        else:
            matches = stage["matches"]
            self.cv.configure(scrollregion=(0, 0, 900, max(420, 74 + len(matches)*87)))
            for i, (a, b, winner) in enumerate(matches):
                x, y = 45, 64 + i*87
                rounded(self.cv, x, y, 805, 74, fill=PAPER, radius=12)
                self.text(x+16, y+20, f"Match {i+1}: {a}  vs  {b}", 14, INK, "bold", anchor="w")
                self.text(x+16, y+52, "Winner: " + winner, 12, JADE, "bold", anchor="w")

    def setup_basketball(self):
        self.description.configure(text="NBA historical 30-team roster · 15 East and 15 West · Eight playoff teams per conference, three elimination rounds, NBA Final and champion. Results are fictional.")
        self.nba_stages = []
        self.nba_index = 0
        self.button("New NBA championship", self.reset_basketball)
        self.nba_next = self.button("Next round", self.advance_basketball, True)
        self.nba_scroll = ttk.Scrollbar(self.cv, orient="vertical", command=self.cv.yview)
        self.nba_scroll.pack(side="right", fill="y")
        self.cv.configure(yscrollcommand=self.nba_scroll.set)
        self.scene = self.draw_basketball
        self.reset_basketball()

    def reset_basketball(self):
        self.nba_stages = nba_stages()
        self.nba_index = 0
        self.nba_next.configure(state="normal", text="Play first round")
        self.status.set("NBA playoff field · 8 Eastern and 8 Western teams qualified from the 30-team historical roster.")
        self.cv.yview_moveto(0)
        self.redraw()

    def advance_basketball(self):
        if self.nba_index >= len(self.nba_stages)-1:
            return
        self.nba_index += 1
        stage = self.nba_stages[self.nba_index]
        self.status.set("NBA · " + stage["title"] + " · Simulated competition.")
        if stage["kind"] == "champion":
            self.nba_next.configure(state="disabled", text="Championship complete")
        else:
            self.nba_next.configure(state="normal", text="Show " + self.nba_stages[self.nba_index+1]["title"])
        self.cv.yview_moveto(0)
        self.redraw()

    def draw_basketball(self):
        if not self.nba_stages:
            return
        stage = self.nba_stages[self.nba_index]
        self.text(24, 25, stage["title"].upper(), 19, ACCENT, "bold", anchor="w")
        if stage["kind"] == "nba_field":
            self.cv.configure(scrollregion=(0, 0, 900, 525))
            for i, (label, names) in enumerate((("EASTERN CONFERENCE", stage["east"]), ("WESTERN CONFERENCE", stage["west"]))):
                x = 18 + 445*i
                rounded(self.cv, x, 54, 426, 455, fill=PAPER, radius=15)
                self.text(x+19, 84, label, 15, ACCENT, "bold", anchor="w")
                for n, name in enumerate(names):
                    self.text(x+22, 130+n*43, f"{n+1}. {name}", 12, INK, anchor="w")
        elif stage["kind"] == "champion":
            self.cv.configure(scrollregion=(0, 0, 900, 420))
            emblem(self.cv, "star", 450, 155, 70, AMBER)
            self.text(450, 277, stage["winner"], 25, INK, "bold")
            self.text(450, 335, "NBA CHAMPION · SIMULATION", 12, MUTED)
        else:
            matches = stage["matches"]
            self.cv.configure(scrollregion=(0, 0, 900, max(420, 75 + len(matches)*80)))
            for i, (conference, a, b, winner) in enumerate(matches):
                x, y = 35, 53 + i*80
                rounded(self.cv, x, y, 830, 73, fill=PAPER, radius=10)
                self.text(x+14, y+15, conference, 10, ACCENT, "bold", anchor="w")
                self.text(x+14, y+37, f"{a}  vs  {b}", 13, INK, "bold", anchor="w")
                self.text(x+14, y+60, "Winner: " + winner, 11, JADE, "bold", anchor="w")

    def setup_memory(self):
        self.description.configure(text="Find eight pairs of original Daylight pictures. Click a card, or focus the board with Tab and use the arrow keys and Enter.")
        self.memory = Memory()
        self.memory_recorded = False
        self.memory_focus = 0
        def move(delta):
            self.memory_focus = (self.memory_focus+delta) % 16
            self.redraw()
            return "break"
        for key, delta in (("Left", -1), ("Right", 1), ("Up", -4), ("Down", 4)):
            self.cv.bind("<"+key+">", lambda _e, d=delta: move(d))
        self.cv.bind("<Return>", lambda _e: self.reveal_memory(self.memory_focus))
        self.cv.bind("<space>", lambda _e: self.reveal_memory(self.memory_focus))
        self.cv.bind("<FocusIn>", lambda _e: self.redraw())
        self.cv.bind("<FocusOut>", lambda _e: self.redraw())
        self.button("New game",self.new_memory,True)
        self.scene = self.draw_memory
        self.status.set("Choose the first card.")

    def new_memory(self):
        self.memory = Memory()
        self.memory_recorded = False
        self.memory_focus = 0
        self.status.set("Choose the first card.")
        self.show_record()
        self.redraw()

    def reveal_memory(self,index):
        self.memory_focus = index
        if not self.memory.reveal(index):
            return
        self.redraw()
        if self.memory.completed:
            if not self.memory_recorded:
                self.memory_recorded = True
                self.save_score("memory", value=self.memory.moves)
            self.status.set(f"All eight pairs found in {self.memory.moves} moves. Well played!")
        elif len(self.memory.open)==2:
            self.status.set(("A matching pair!" if self.memory.open[0] in self.memory.matched else "Different pictures. Try to remember them.")+f" · {self.memory.moves} moves")
            current = self.memory
            def close():
                if self.memory is current:
                    self.memory.close_pair()
                    self.redraw()
            self.later(1100,close)
        else:
            self.status.set("Choose another card.")

    def draw_memory(self):
        m = self.memory
        pictures = ("sun","moon","mountain","star","leaf","diamond","flower","waves")
        for i,value in enumerate(m.deck):
            row,col = divmod(i,4)
            x,y = 160+col*150,8+row*106
            tag = f"memory-{i}"
            visible = i in m.matched or i in m.open
            focused = self.cv.focus_get() is self.cv and self.memory_focus == i
            rounded(self.cv,x,y,130,94,fill=PAPER if visible else NIGHT,
                    outline=ACCENT if focused else JADE if i in m.matched else LINE,
                    radius=12,width=4 if focused else 2,tags=(tag,))
            if visible:
                emblem(self.cv,pictures[value],x+65,y+46,27,COLORS[value%4],PAPER,tags=(tag,))
            else:
                self.cv.create_polygon(x+65,y+15,x+96,y+47,x+65,y+79,x+34,y+47,outline=IRIS,fill="",width=2,tags=(tag,))
                self.text(x+65,y+47,str(i+1),14,ON_NIGHT,"bold",tags=(tag,))
            self.cv.tag_bind(tag,"<Button-1>",lambda _e,n=i:self.reveal_memory(n))
            self.cv.tag_bind(tag,"<Enter>",lambda _e:self.cv.configure(cursor="hand2"))
            self.cv.tag_bind(tag,"<Leave>",lambda _e:self.cv.configure(cursor=""))

    def setup_slots(self):
        self.description.configure(text="A small picture-matching machine. Spin the reels to find three matching symbols. No wagers or money.")
        self.reels = [0,1,2]
        self.spinning = False
        self.spins = 0
        self.slot_wins = 0
        self.spin_button = self.button("Spin reels",self.spin,True)
        self.cv.bind("<space>",lambda _e:self.spin())
        self.scene = self.draw_slots
        self.status.set("Sun · Mountain · Star · Moon")

    def spin(self):
        if self.spinning:
            return
        self.spinning = True
        self.spin_button.configure(state="disabled")
        self.animate_spin(0)

    def animate_spin(self,step):
        self.reels = [RNG.randrange(4) for _ in range(3)]
        self.redraw()
        if step<9:
            self.later(50+step*10,lambda:self.animate_spin(step+1))
        else:
            self.spinning = False
            self.spin_button.configure(state="normal")
            self.spins += 1
            win = len(set(self.reels))==1
            self.slot_wins += int(win)
            self.save_score("slots", "match" if win else "miss")
            self.status.set(("Three matching pictures!" if win else "Try another spin.")+f" · Spins {self.spins} · Matches {self.slot_wins}")

    def draw_slots(self):
        rounded(self.cv,95,40,710,325,fill=NIGHT,outline="")
        self.text(450,77,"DAYLIGHT PICTURE REELS",13,ON_NIGHT,"bold")
        symbols = ("sun","mountain","star","moon")
        for i,value in enumerate(self.reels):
            x = 150+i*210
            rounded(self.cv,x,111,180,196,fill=PAPER,outline=IRIS,radius=12,width=2)
            emblem(self.cv,symbols[value],x+90,201,54,COLORS[value])
            self.text(x+90,284,symbols[value].upper(),11,MUTED,"bold")
        self.text(450,342,"SPACE TO SPIN",10,"#c8bfd8","bold")

    def setup_guess(self):
        self.description.configure(text="Find the secret number from 1 to 100. Each guess narrows the highlighted range.")
        self.guess_value,self.guess_entry = self.field("Your guess","50",9)
        self.guess_entry.bind("<Return>",lambda _e:self.make_guess())
        self.guess_button = self.button("Try number",self.make_guess,True)
        self.button("New game",self.new_guess)
        self.scene = self.draw_guess
        self.new_guess()

    def new_guess(self):
        self.target = RNG.randrange(1,101)
        self.guesses = []
        self.low,self.high = 1,100
        self.found = False
        self.guess_button.configure(state="normal")
        self.status.set("The number is between 1 and 100.")
        self.show_record()
        self.redraw()

    def make_guess(self):
        if self.found:
            return
        try:
            n = int(self.guess_value.get())
            if not 1<=n<=100:
                raise ValueError
        except ValueError:
            self.status.set("Enter a whole number from 1 to 100.")
            return
        self.guesses.append(n)
        if n==self.target:
            self.found = True
            self.save_score("guess", value=len(self.guesses))
            self.guess_button.configure(state="disabled")
            self.status.set(f"Correct! You found {n} in {len(self.guesses)} guesses.")
        elif n<self.target:
            self.low = max(self.low,n+1)
            self.status.set(f"Higher than {n} · {len(self.guesses)} guesses")
        else:
            self.high = min(self.high,n-1)
            self.status.set(f"Lower than {n} · {len(self.guesses)} guesses")
        self.redraw()

    def draw_guess(self):
        rounded(self.cv,110,45,680,260)
        self.text(450,90,"SECRET NUMBER",12,MUTED,"bold")
        self.text(450,185,str(self.target) if self.found else "?",83,JADE if self.found else ACCENT,"bold")
        self.text(450,267,f"Possible range: {self.low} – {self.high}" if not self.found else "FOUND",15,INK,"bold")
        y=357
        self.cv.create_line(110,y,790,y,fill=LINE,width=12,capstyle="round")
        self.cv.create_line(110+(self.low-1)*680/99,y,110+(self.high-1)*680/99,y,
                            fill=JADE if self.found else IRIS,width=12,capstyle="round")
        for n in self.guesses:
            x = 110+(n-1)*680/99
            self.cv.create_oval(x-4,y-4,x+4,y+4,fill=ACCENT,outline=PAPER)
        self.text(110,389,"1",12,MUTED)
        self.text(790,389,"100",12,MUTED)
        if self.guesses:
            self.text(450,420,"Your guesses: "+", ".join(map(str,self.guesses[-15:])),10,MUTED)


def build(parent, name, context=None):
    from . import theme
    global BG, PANEL, PAPER, INK, MUTED, LINE, ACCENT, NIGHT, CORAL, AMBER, JADE, IRIS, COLORS
    p = theme.PALETTE
    BG, PANEL, PAPER, INK = p["bg"], p["panel"], p["card"], p["ink"]
    MUTED, LINE, ACCENT, NIGHT = p["muted"], p["line"], p["accent"], p["night"]
    CORAL, AMBER, JADE, IRIS = p["coral"], p["amber"], p["jade"], p["iris"]
    COLORS = (CORAL, AMBER, JADE, IRIS)
    if name not in PAGE_NAMES:
        raise ValueError("Unknown game: "+name)
    return GamePage(parent,name,context)

[executed on device: hamdy-LinuxManjro (d2fadeb0-3f51-4b03-90ee-3f2bf0b8b7db)]