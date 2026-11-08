#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hamdy Abou El Anein
"""Shardturn — The Color Card Duel. Run with: python3 shardturn.py.

Vector interface and cards drawn with Tkinter, without external images.
Developer: Hamdy Abou El Anein
Contact: info@daylightlinux.ch
"""
from __future__ import annotations

import argparse
import math
import random
try:
    import tkinter as tk
    from tkinter import font as tkfont
except ImportError as exc:
    raise SystemExit("Tkinter is required.\n"
                     "Manjaro : sudo pacman -S tk\n"
                     "Debian/Ubuntu : sudo apt install python3-tk\n"
                     "Windows/macOS: install Python with Tcl/Tk.") from exc
from collections import Counter

# --- Rules engine ---
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Hamdy Abou El Anein
"""Shardturn two-player card-game rules, independent from the graphical interface.

The engine deliberately permits a Wild Draw Four bluff: its legality is only
revealed when the next player challenges it. No AI policy lives in this module.

Developer: Hamdy Abou El Anein
Contact: info@daylightlinux.ch
"""

from dataclasses import dataclass
from random import Random
from typing import List, Optional

COLORS = ("red", "yellow", "green", "blue")
COLOR_NAMES = {"red": "Coral", "yellow": "Amber", "green": "Jade", "blue": "Iris"}
VALUE_NAMES = {"skip": "Pause", "reverse": "Reverse", "draw2": "+2",
               "wild": "Wild", "wild4": "+4"}
PLAYER_NAMES = ("You", "The computer")


@dataclass(frozen=True)
class Card:
    color: Optional[str]
    value: str

    @property
    def label(self):
        name = VALUE_NAMES.get(self.value, self.value)
        return name if self.color is None else "{} {}".format(COLOR_NAMES[self.color], name)

    @property
    def points(self):
        if self.value.isdigit():
            return int(self.value)
        return 50 if self.color is None else 20


@dataclass(frozen=True)
class PendingWild4:
    attacker: int
    defender: int
    illegal: bool
    previous_color: str
    # Hand at the time of the play is the evidence required by the official rule.
    evidence: tuple


def make_deck():
    cards = []
    for color in COLORS:
        cards.append(Card(color, "0"))
        for value in [str(n) for n in range(1, 10)] + ["skip", "reverse", "draw2"]:
            cards.extend([Card(color, value), Card(color, value)])
    cards.extend(Card(None, "wild") for _ in range(4))
    cards.extend(Card(None, "wild4") for _ in range(4))
    return cards


class ShardturnGame:
    """A round. Players 0 (human) and 1 (computer); a match is managed by the UI.

    Public action methods raise ValueError for invalid input. `draw()` draws one
    card and offers it only if playable; otherwise the turn advances at once.
    A playable drawn card can be played or retained using `pass_turn()`.
    """

    def __init__(self, seed=None, dealer=None):
        self.rng = Random(seed)
        self.dealer = self.rng.randrange(2) if dealer is None else dealer
        if self.dealer not in (0, 1):
            raise ValueError("Invalid dealer.")
        self.hands = [[], []]
        self.draw_pile = make_deck()
        self.rng.shuffle(self.draw_pile)
        for _ in range(7):
            self.hands[1 - self.dealer].append(self.draw_pile.pop())
            self.hands[self.dealer].append(self.draw_pile.pop())
        while self.draw_pile[-1].value == "wild4":
            self.rng.shuffle(self.draw_pile)
        self.discard_pile = [self.draw_pile.pop()]
        self.current = 1 - self.dealer
        self.current_color = self.top.color
        self.phase = "play"
        self.drawn_index = None
        self.pending_wild4 = None
        self.pending_draw2 = None
        self.uno_vulnerable = None
        self.winner = None
        self.round_points = 0
        self.messages = []
        self.last_drawn = None
        self.last_challenge = None
        self.empty_draw_turns = 0
        self._log("Seven cards each. Starting card: {}.".format(self.top.label))
        if self.top.value == "wild":
            self.phase = "opening_color"
            self._log("{}: choose the starting color.".format(PLAYER_NAMES[self.current]))
        elif self.top.value == "draw2":
            self._take_cards(self.current, 2)
            self._log("The starting +2 makes the first player draw two cards and skip a turn.")
            self.current = self.dealer
        elif self.top.value in ("skip", "reverse"):
            self.current = self.dealer
            self._log("The starting action card skips the first player's turn.")

    @property
    def top(self):
        return self.discard_pile[-1]

    def _log(self, message):
        self.messages.append(message)

    def _require_turn(self):
        if self.phase not in ("play", "drawn"):
            raise ValueError("This action is not available right now.")

    def _begin_action(self):
        # The missed-LAST CARD window closes when the next player actually acts.
        if self.uno_vulnerable is not None and self.uno_vulnerable != self.current:
            self.uno_vulnerable = None
        self.last_challenge = None

    def _next(self):
        self.current = 1 - self.current
        self.phase = "play"
        self.drawn_index = None

    def _take_cards(self, player, count):
        taken = []
        for _ in range(count):
            if not self.draw_pile and len(self.discard_pile) > 1:
                self.draw_pile = self.discard_pile[:-1]
                self.discard_pile = [self.discard_pile[-1]]
                self.rng.shuffle(self.draw_pile)
                self._log("The discard pile is shuffled to refill the draw pile.")
            if not self.draw_pile:
                break
            card = self.draw_pile.pop()
            self.hands[player].append(card)
            taken.append(card)
        if self.uno_vulnerable == player and len(self.hands[player]) != 1:
            self.uno_vulnerable = None
        return taken

    def choose_opening_color(self, color):
        if self.phase != "opening_color" or color not in COLORS:
            raise ValueError("Choose one of the four colors.")
        self.current_color = color
        self.phase = "play"
        self._log("Starting color: {}.".format(COLOR_NAMES[color]))

    def is_playable(self, index, allow_bluff=True):
        if self.phase not in ("play", "drawn"):
            return False
        if not isinstance(index, int) or isinstance(index, bool):
            return False
        hand = self.hands[self.current]
        if not 0 <= index < len(hand):
            return False
        if self.phase == "drawn" and index != self.drawn_index:
            return False
        card = hand[index]
        if card.value == "wild4":
            return allow_bluff or not any(c.color == self.current_color for c in hand)
        return (card.color is None or card.color == self.current_color
                or card.value == self.top.value)

    def legal_indices(self, allow_bluff=True):
        return [i for i in range(len(self.hands[self.current])) if self.is_playable(i, allow_bluff)]

    def _either_hand_can_play(self):
        # A voluntary empty draw does not prove that its player has no move.
        # Inspect both hands, independently of current turn/drawn-card state.
        return any(card.color is None or card.color == self.current_color
                   or card.value == self.top.value
                   for hand in self.hands for card in hand)

    def play(self, index, color=None, announce_uno=False):
        self._require_turn()
        if not self.is_playable(index):
            raise ValueError("This card cannot be played right now.")
        hand = self.hands[self.current]
        card = hand[index]
        if card.color is None and color not in COLORS:
            raise ValueError("A Wild card needs a chosen color.")
        if card.color is not None and color is not None:
            raise ValueError("Only Wild cards let you choose a color.")
        actor = self.current
        old_color = self.current_color
        illegal = card.value == "wild4" and any(c.color == old_color for c in hand)
        evidence = tuple(c for i, c in enumerate(hand) if i != index)
        self._begin_action()
        hand.pop(index)
        self.discard_pile.append(card)
        self.current_color = card.color if card.color is not None else color
        self.phase = "play"
        self.drawn_index = None
        self.empty_draw_turns = 0
        self._log("{}: {}{}.".format(PLAYER_NAMES[actor], card.label,
                  " → " + COLOR_NAMES[color] if card.color is None else ""))
        if len(hand) == 1:
            self.uno_vulnerable = None if announce_uno else actor
            if announce_uno:
                self._log("{}: LAST CARD!".format(PLAYER_NAMES[actor]))
        elif self.uno_vulnerable == actor:
            self.uno_vulnerable = None
        if card.value == "wild4":
            self.pending_wild4 = PendingWild4(actor, 1 - actor, illegal, old_color, evidence)
            self.current = 1 - actor
            self.phase = "wild4"
            self._log("{} must accept four cards or challenge the +4.".format(PLAYER_NAMES[self.current]))
            return
        if card.value == "draw2":
            # Resolve as a separate next-player action so a missed LAST CARD announcement can be
            # caught before that player starts drawing the forced penalty.
            self.pending_draw2 = actor
            self.current = 1 - actor
            self.phase = "draw2"
            self._log("{} must draw two cards and skip a turn.".format(PLAYER_NAMES[self.current]))
            return
        elif card.value in ("skip", "reverse"):
            self._log("With two players, {} skips the opponent's turn.".format(card.label))
        else:
            self._next()
        if not hand:
            self._finish_round(actor)

    def draw(self):
        if self.phase != "play":
            raise ValueError("You cannot draw right now.")
        self._begin_action()
        actor = self.current
        taken = self._take_cards(actor, 1)
        if not taken:
            self.empty_draw_turns += 1
            self._log("{}: empty draw pile, turn passed.".format(PLAYER_NAMES[actor]))
            self._next()
            if self.empty_draw_turns >= 2 and not self._either_hand_can_play():
                self.phase = "stalled"
                self._log("No card can be played. The round is a draw.")
            return None
        self.empty_draw_turns = 0
        self.last_drawn = (actor, taken[0])
        self.drawn_index = len(self.hands[actor]) - 1
        self.phase = "drawn"
        self._log("{}: one card drawn.".format(PLAYER_NAMES[actor]))
        if not self.is_playable(self.drawn_index):
            self._next()
        return taken[0]

    def pass_turn(self):
        if self.phase != "drawn":
            raise ValueError("Draw a card before passing.")
        self._begin_action()
        self._log("{}: drawn card kept, turn passed.".format(PLAYER_NAMES[self.current]))
        self._next()

    def resolve_wild4(self, challenge=False):
        if self.phase != "wild4" or self.pending_wild4 is None:
            raise ValueError("There is no +4 penalty to resolve.")
        pending = self.pending_wild4
        self._begin_action()
        self.pending_wild4 = None
        self.phase = "play"
        if challenge and pending.illegal:
            self._take_cards(pending.attacker, 4)
            self.current = pending.defender
            self.last_challenge = {"success": True, "evidence": pending.evidence,
                                   "color": pending.previous_color, "attacker": pending.attacker}
            self._log("Challenge won! The +4 was illegal: its player draws four cards.")
        else:
            count = 6 if challenge else 4
            self._take_cards(pending.defender, count)
            self.current = pending.attacker
            if challenge:
                self.last_challenge = {"success": False, "evidence": pending.evidence,
                                       "color": pending.previous_color, "attacker": pending.attacker}
                self._log("Challenge lost: draw six cards and skip your turn.")
            else:
                self._log("+4 accepted: draw four cards and skip your turn.")
        if not self.hands[pending.attacker]:
            self._finish_round(pending.attacker)

    def resolve_draw2(self):
        if self.phase != "draw2" or self.pending_draw2 is None:
            raise ValueError("There is no +2 penalty to resolve.")
        attacker = self.pending_draw2
        defender = 1 - attacker
        self._begin_action()
        self._take_cards(defender, 2)
        self.pending_draw2 = None
        self.current = attacker
        self.phase = "play"
        self.drawn_index = None
        self._log("{}: two cards drawn, turn skipped.".format(PLAYER_NAMES[defender]))
        if not self.hands[attacker]:
            self._finish_round(attacker)

    def call_uno(self, player=0):
        if player not in (0, 1) or len(self.hands[player]) != 1:
            raise ValueError("Announce LAST CARD when you have one card left.")
        if self.uno_vulnerable != player:
            raise ValueError("LAST CARD is already announced or the catch window has closed.")
        self.uno_vulnerable = None
        self._log("{}: LAST CARD!".format(PLAYER_NAMES[player]))

    def catch_uno(self, catcher=None):
        catcher = self.current if catcher is None else catcher
        if (catcher not in (0, 1) or self.uno_vulnerable is None
                or self.uno_vulnerable == catcher or self.phase in ("round_over", "stalled")):
            raise ValueError("There is no missed LAST CARD announcement to catch.")
        offender = self.uno_vulnerable
        self.uno_vulnerable = None
        self._take_cards(offender, 2)
        self._log("{}: missed LAST CARD, two penalty cards drawn.".format(PLAYER_NAMES[offender]))

    def _finish_round(self, winner):
        self.winner = winner
        self.round_points = sum(c.points for c in self.hands[1 - winner])
        self.phase = "round_over"
        self.drawn_index = None
        self.uno_vulnerable = None
        self._log("{}: round won, {} points scored.".format(PLAYER_NAMES[winner], self.round_points))

# --- Graphical interface ---

__author__ = "Hamdy Abou El Anein"
__email__ = "info@daylightlinux.ch"


COLORS_UI = {"red": "#ce6655", "yellow": "#c79a36", "green": "#358d7d", "blue": "#7c6fbb"}
COLOR_NAMES_UI = {"red": "CORAL", "yellow": "AMBER", "green": "JADE", "blue": "IRIS"}
BG = "#e9e6df"
TABLE = "#faf8f2"
PANEL = "#eeebe4"
MUTED = "#66667b"
INK = "#292a43"
ACCENT = "#6548a3"
NIGHT = "#292c49"
PAPER = "#fcfaf5"
HAIRLINE = "#d7d2c8"
FONT_FAMILY = "DejaVu Sans"

RULES = """SHARDTURN · THE COLOR CARD DUEL

Developer: Hamdy Abou El Anein
Contact: info@daylightlinux.ch

GOAL
Empty your hand. The round winner scores the cards left in the other
player's hand. The first player to reach 500 points wins the match.
Numbers: face value; Pause / Reverse / +2: 20; Wild / +4: 50.

YOUR TURN
Play a card matching the active color, number, or action symbol.
A Wild can always be played. Choose a color when you play a Wild.
You may draw even when you already hold a playable card.
After drawing, only the card just drawn may be played: play it or choose
Keep / pass. Drawing an unplayable card automatically passes your turn.

ACTION CARDS IN A TWO-PLAYER GAME
Pause: your opponent skips a turn, so you play again.
Reverse: works like Pause with two players; you play again.
+2: your opponent draws two and skips a turn; you play again.
Wild: choose a color, then your opponent plays.
+4: choose a color; your opponent draws four and skips a turn.
Draw penalties cannot be stacked. You cannot answer a +2 or +4 with
another draw card to pass the penalty on.

CHALLENGING A +4
A +4 is legal only when its player held no card of the active color
before playing it. A matching number or symbol in another color does
not prevent a legal +4. You may still try an illegal +4 as a bluff.
If your challenge succeeds, the other player draws four and you play.
If it fails, you draw six and skip your turn.
The game checks challenges automatically. The computer's cards always
stay hidden, including during a challenge. In the physical card game,
the challenged hand would be shown to the challenger.

CALLING LAST CARD!
When you have two cards, enable LAST CARD! BEFORE playing a card.
The button lights up: your next play calls LAST CARD! if it leaves one
card. You may also call just after playing, before the computer acts.
A missed call caught in time costs two cards. The computer may forget
too: choose Missed call! before starting your next action.

STARTING AND ENDING A ROUND
Seven cards each, from a 108-card deck. The first dealer is chosen at
random and dealers alternate between rounds. An opening action card
has its effect; an opening +4 is shuffled back into the deck.
A final +2 or +4 applies its penalty before the score is calculated.
When the draw pile runs out, the discard pile is shuffled into it,
keeping the visible top card. If neither player can make progress,
the round is redealt without awarding points.

CONTROLS
Click an outlined card to play. Hover over a card for its description.
D: draw · Space: draw / keep · L: LAST CARD! · C: catch a missed call.
H: help · N: new match · Escape: cancel a color choice.
1 to 9, then 0: play the ten displayed cards. Left / Right: hand pages.

VISUAL IDENTITY
Four families: Coral (circle), Amber (diamond), Jade (triangle), and
Iris (square). Shapes accompany colors to help identify each family.
Wild cards carry a mosaic of four facets.
Shardturn is an independent project, not affiliated with Mattel.
"""


class Painter:
    """Small canvas adapter: all layout uses a 1200 × 820 coordinate system."""

    def __init__(self, canvas: tk.Canvas, scale: float, ox: float, oy: float):
        self.c, self.s, self.ox, self.oy = canvas, scale, ox, oy

    def coords(self, values):
        return [(v * self.s + (self.ox if i % 2 == 0 else self.oy)) for i, v in enumerate(values)]

    def rect(self, x, y, w, h, fill, outline="", width=1, radius=12):
        r = min(radius, w / 2, h / 2)
        p = [x+r,y, x+w-r,y, x+w,y, x+w,y+r, x+w,y+h-r,
             x+w,y+h, x+w-r,y+h, x+r,y+h, x,y+h, x,y+h-r,
             x,y+r, x,y]
        return self.c.create_polygon(self.coords(p), smooth=True, splinesteps=24,
                                     fill=fill, outline=outline, width=width*self.s)

    def oval(self, x, y, w, h, fill, outline="", width=1):
        return self.c.create_oval(*self.coords([x,y,x+w,y+h]), fill=fill,
                                  outline=outline, width=width*self.s)

    def line(self, points, fill, width=2, **kw):
        return self.c.create_line(*self.coords(points), fill=fill, width=width*self.s, **kw)

    def text(self, x, y, text, size=14, fill=INK, bold=False, anchor="center", **kw):
        return self.c.create_text(*self.coords([x,y]), text=text, fill=fill, anchor=anchor,
                                  font=(FONT_FAMILY, -max(8, round(size*self.s)),
                                        "bold" if bold else "normal"), **kw)

    def polygon(self, points, fill, outline="", width=1):
        return self.c.create_polygon(self.coords(points), fill=fill, outline=outline, width=width*self.s)

    def emblem(self, cx, cy, radius):
        """Four independent, rotating facets: Shardturn's geometric signature."""
        for i,color in enumerate(COLORS_UI.values()):
            angle=i*math.pi/2
            points=[]
            for x,y in ((0,-1),(.86,-.18),(.12,-.09),(-.34,-.5)):
                points.extend((cx+radius*(x*math.cos(angle)-y*math.sin(angle)),
                               cy+radius*(x*math.sin(angle)+y*math.cos(angle))))
            self.polygon(points,color)

    def family(self, cx, cy, radius, color, fill=None):
        fill=fill or COLORS_UI[color]
        if color=="red":
            self.oval(cx-radius,cy-radius,2*radius,2*radius,fill)
        elif color=="yellow":
            self.polygon([cx,cy-radius,cx+radius,cy,cx,cy+radius,cx-radius,cy],fill)
        elif color=="green":
            self.polygon([cx,cy-radius,cx+radius,cy+radius*.8,cx-radius,cy+radius*.8],fill)
        else:
            self.rect(cx-radius*.85,cy-radius*.85,radius*1.7,radius*1.7,fill,radius=1)

    def card(self, x, y, w=84, h=126, card=None, back=False, active=False, selected=False):
        self.rect(x+2,y+5,w,h,"#d5d0c8",radius=9)
        if active:
            self.rect(x-3,y-3,w+6,h+6,ACCENT,radius=11)
        self.rect(x,y,w,h,NIGHT if back else PAPER,outline="#b8b3b0" if back else HAIRLINE,radius=8)
        cx, cy = x+w/2, y+h/2
        if back:
            # Faceted lattice, with no diagonal oval or commercial wordmark.
            for row in range(4):
                for col in range(3):
                    px=x+w*(.2+col*.3)
                    py=y+h*(.16+row*.22)
                    r=w*.12
                    self.polygon([px,py-r,px+r,py,px,py+r,px-r,py],"",outline="#484b68",width=.6)
            self.rect(x+w*.16,y+h*.23,w*.68,h*.54,NIGHT,outline="#64637a",radius=5)
            self.emblem(cx,cy-h*.025,w*.27)
            self.text(cx,y+h*.72,"S T",w*.12,"#f8f3e7",True)
            return
        val = card.value
        face=COLORS_UI.get(card.color,ACCENT)
        self.rect(x+w*.08,y+h*.065,w*.84,h*.035,face,radius=1)
        if card.color:
            self.family(x+w*.21,y+h*.21,w*.065,card.color)
        else:
            self.emblem(x+w*.21,y+h*.21,w*.08)
        short={"skip":"II","reverse":"R","draw2":"+2","wild":"W","wild4":"+4"}.get(val,val)
        self.text(x+w*.80,y+h*.21,short,w*.13,INK,True)
        if val in ("wild", "wild4"):
            self.emblem(cx,cy-h*.045,w*.28)
            self.text(cx,y+h*.74,"+4" if val=="wild4" else "WILD",w*.20 if val=="wild4" else w*.115,INK,True)
        elif val=="skip":
            self.rect(cx-w*.19,cy-h*.14,w*.13,h*.28,face,radius=2)
            self.rect(cx+w*.06,cy-h*.14,w*.13,h*.28,face,radius=2)
            self.text(cx,y+h*.75,"PAUSE",w*.115,INK,True)
        elif val=="reverse":
            self.line([cx+w*.22,cy+h*.1,cx+w*.22,cy-h*.09,cx-w*.19,cy-h*.09],face,w*.06,
                      arrow="last",arrowshape=(w*.13,w*.16,w*.09),joinstyle="round")
            self.text(cx,y+h*.75,"REVERSE",w*.105,INK,True)
        elif val=="draw2":
            self.rect(cx-w*.21,cy-h*.15,w*.24,h*.22,PAPER,outline=face,width=2,radius=2)
            self.rect(cx-w*.015,cy-h*.10,w*.24,h*.22,face,radius=2)
            self.text(cx,y+h*.73,"+2",w*.25,INK,True)
        else:
            self.text(cx,cy+h*.015,val,w*.65,INK,True)
        if card.color:
            self.family(x+w*.24,y+h*.90,w*.045,card.color)
            self.text(x+w*.62,y+h*.90,COLOR_NAMES_UI[card.color],w*.081,MUTED,True)
        else:
            for i,color in enumerate(COLORS_UI):
                self.family(x+w*(.26+i*.16),y+h*.90,w*.035,color)
        if selected:
            self.rect(x+w*.12,y+h+10,w*.76,23,ACCENT,radius=5)
            self.text(cx,y+h+21,"DRAWN",9,"white",True)


class ShardturnApp:
    def __init__(self, root: tk.Tk, seed=None):
        global FONT_FAMILY
        families = {name.lower() for name in tkfont.families(root)}
        FONT_FAMILY = "DejaVu Sans" if "dejavu sans" in families else "Helvetica"
        self.root = root
        self.rng = random.Random(seed)
        self.root.title("Shardturn — The Color Card Duel")
        self.root.geometry("1200x820")
        self.root.minsize(960, 680)
        self.root.configure(bg=BG)
        self.canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda e:self.change_page(-1))
        self.canvas.bind("<Button-5>", lambda e:self.change_page(1))
        self.root.bind("<Key>", self.on_key)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.ai_job = None
        self.uno_job = None
        self.resize_job = None
        self.help_window = None
        self.overlay = None
        self.hover = None
        self.page = 0
        self.uno_armed = False
        self.scores = [0,0]
        self.round_number = 0
        self.dealer = self.rng.randrange(2)
        self.status = ""
        self.regions = []
        self.scale, self.ox, self.oy = 1,0,0
        self.new_round()

    def close(self):
        self.cancel_ai()
        self.root.destroy()

    def cancel_ai(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None
        if self.uno_job is not None:
            self.root.after_cancel(self.uno_job)
            self.uno_job = None

    def new_round(self, reset=False):
        self.cancel_ai()
        if reset:
            self.scores = [0,0]
            self.round_number = 0
            self.dealer = self.rng.randrange(2)
        elif self.round_number:
            self.dealer = 1-self.dealer
        self.round_number += 1
        self.game = ShardturnGame(seed=self.rng.randrange(2**32), dealer=self.dealer)
        self.scored = False
        self.overlay = None
        self.page, self.hover = 0,None
        self.uno_armed = False
        self.status = ""
        self.refresh()

    def on_resize(self, _event):
        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(25,self.render)

    def region(self, x,y,w,h,action,payload=None,enabled=True):
        if enabled:
            self.regions.append((x,y,x+w,y+h,action,payload))

    def button(self,p,x,y,w,h,text,action,payload=None,enabled=True,primary=False):
        p.rect(x,y,w,h,ACCENT if primary and enabled else ("#e1dce9" if enabled else "#e9e5df"),radius=8)
        p.text(x+w/2,y+h/2,text,12,"white" if primary and enabled else (INK if enabled else "#9d98a3"),True)
        self.region(x,y,w,h,action,payload,enabled)

    def human_play(self):
        return self.game.current==0 and self.game.phase in ("play","drawn") and self.overlay is None

    def render(self):
        self.resize_job = None
        c=self.canvas
        c.delete("all")
        self.regions=[]
        w,h=max(c.winfo_width(),960),max(c.winfo_height(),680)
        self.scale=min(w/1200,h/820)
        self.ox,self.oy=(w-1200*self.scale)/2,(h-820*self.scale)/2
        p=Painter(c,self.scale,self.ox,self.oy)
        self.p=p
        g=self.game
        p.rect(22,22,1156,776,TABLE,outline=HAIRLINE,radius=18)
        p.emblem(75,53,24)
        p.text(116,45,"SHARDTURN",25,INK,True,anchor="w")
        p.text(117,69,"THE COLOR CARD DUEL",10,MUTED,True,anchor="w")
        p.text(600,45,f"ROUND {self.round_number:02d}",11,MUTED,True)
        p.text(600,68,"Target: 500 points",11,MUTED)
        p.rect(803,33,230,42,PANEL,radius=8)
        p.text(918,54,f"YOU  {self.scores[0]}    ·    AI  {self.scores[1]}",12,INK,True)
        self.button(p,1048,33,42,42,"?","help")
        self.button(p,1100,33,51,42,"N","new_match")
        p.line([52,89,1148,89],HAIRLINE,1)

        n=len(g.hands[1])
        p.rect(301,101,598,143,NIGHT,radius=14)
        p.text(600,115,"COMPUTER",10,"#e4deef",True)
        count=min(n,13)
        bw,bh=61,89
        step=min(40,530/max(1,count-1))
        start=600-(bw+max(0,count-1)*step)/2
        for i in range(count):
            p.card(start+i*step,135,bw,bh,back=True)
        if n==0:
            p.text(600,176,"No cards left",15,MUTED)
        p.rect(920,151,139,47,PANEL,radius=14)
        p.text(989,175,f"{n} card{'s' if n!=1 else ''}",14,INK,True)
        if n==1:
            p.text(990,214,"LAST CARD!" if g.uno_vulnerable!=1 else "Missed call?",14,ACCENT,True)

        title,subtitle=self.turn_text()
        p.text(600,267,title,23,ACCENT if g.current==0 else INK,True)
        p.text(600,297,subtitle,12,MUTED)
        p.rect(335,315,530,176,PANEL,outline=HAIRLINE,radius=14)
        p.polygon([335,315,420,315,335,400],"#e7e1da")
        p.polygon([865,491,780,491,865,406],"#e4deec")
        for dy in (6,3):
            p.rect(458+dy,334-dy,92,134,"#b6b0bb",radius=9)
        p.card(458,334,92,134,back=True)
        if self.human_play() and g.phase=="play":
            self.region(453,329,104,146,"draw")
        p.card(641,334,92,134,card=g.discard_pile[-1])
        p.text(504,493,f"DRAW PILE · {len(g.draw_pile)}",10,MUTED,True)
        p.text(687,493,"DISCARD",10,MUTED,True)
        if g.current_color:
            p.family(596,402,14,g.current_color)
        else:
            p.emblem(596,402,19)
        p.text(596,436,COLOR_NAMES_UI.get(g.current_color,"CHOOSE"),9,INK,True)

        p.rect(61,328,231,169,PANEL,radius=18)
        p.text(80,352,"QUICK RULES",10,ACCENT,True,anchor="w")
        p.text(80,383,"Match the color, number,\nor action symbol.",12,INK,anchor="w",justify="left")
        p.text(80,433,"Two players: Pause /\nReverse let you play again.",11,MUTED,anchor="w",justify="left")
        p.text(80,474,"No stacking +2 / +4 cards.",11,MUTED,anchor="w")
        p.rect(909,328,231,169,PANEL,radius=18)
        p.text(928,352,"LAST ACTION",10,ACCENT,True,anchor="w")
        last=self.status or (g.messages[-1] if g.messages else "The match begins.")
        p.text(928,378,last,12,INK,anchor="nw",width=round(192*self.scale),justify="left")

        take_two=g.phase=="draw2" and g.current==0 and self.overlay is None
        can_draw=(self.human_play() and g.phase=="play") or take_two
        self.button(p,329,524,168,46,"DRAW 2  ·  D" if take_two else "DRAW  ·  D","draw",enabled=can_draw,primary=take_two)
        can_uno=(len(g.hands[0])==2 and self.human_play()) or g.uno_vulnerable==0
        uno_label="CALL READY" if self.uno_armed else "LAST CARD!  ·  L"
        self.button(p,509,524,168,46,uno_label,"uno",enabled=can_uno,primary=True)
        self.button(p,689,524,183,46,"KEEP / PASS","pass",enabled=self.human_play() and g.phase=="drawn")
        if g.uno_vulnerable==1:
            self.button(p,925,524,201,46,"MISSED CALL!  +2","catch",primary=True)

        p.line([52,600,1148,600],HAIRLINE,1)
        p.text(65,623,"YOUR HAND",12,INK,True,anchor="w")
        p.text(1135,623,f"{len(g.hands[0])} card{'s' if len(g.hands[0])!=1 else ''}",11,MUTED,anchor="e")
        total=len(g.hands[0])
        pages=max(1,(total+9)//10)
        self.page=max(0,min(self.page,pages-1))
        visible=list(enumerate(g.hands[0]))[self.page*10:(self.page+1)*10]
        cw,ch=78,113
        step=91
        x0=600-(len(visible)*step-(step-cw))/2
        for offset,(i,card) in enumerate(visible):
            playable=self.human_play() and g.is_playable(i,allow_bluff=True)
            raised=self.hover==i and self.overlay is None
            x,y=x0+offset*step,650-(13 if raised else 0)
            p.card(x,y,cw,ch,card=card,active=playable,selected=g.phase=="drawn" and i==g.drawn_index)
            if playable:
                self.region(x-2,y-2,cw+4,ch+4,"card",i)
            self.region(x,y,cw,ch,"hover_card",i)
            p.text(x+cw/2,y+ch+10,str((offset+1)%10),9,MUTED)
        if pages>1:
            self.button(p,59,694,42,40,"‹","page",-1,enabled=self.page>0)
            self.button(p,1099,694,42,40,"›","page",1,enabled=self.page<pages-1)
            p.text(1090,774,f"{self.page+1} / {pages}",10,MUTED)
        if self.hover is not None and self.hover<total and not self.overlay:
            desc=self.describe_card(g.hands[0][self.hover])
            p.text(600,799,desc,11,ACCENT)
        else:
            p.text(600,799,"Outlined cards are playable  ·  Enable LAST CARD! before playing your second-to-last card.",10,MUTED)
        p.text(600,813,f"Developer: {__author__}  ·  Contact: {__email__}",9,MUTED)

        if self.overlay:
            self.draw_overlay(p)
        elif g.phase=="opening_color" and g.current==0:
            self.draw_color_picker(p,"CHOOSE THE OPENING COLOR",opening=True)
        elif g.phase=="wild4" and g.current==0:
            self.draw_challenge(p)
        elif g.phase in ("round_over","stalled"):
            self.draw_result(p)

    def turn_text(self):
        g=self.game
        if self.overlay and self.overlay[0]=="color":
            return "CHOOSE A COLOR","Your Wild will be played after you choose."
        if g.phase=="round_over":
            return ("YOU WON THE ROUND!" if g.winner==0 else "THE COMPUTER WINS THE ROUND"),"Cards left in the losing hand determine the score."
        if g.phase=="stalled":
            return "NO MOVES REMAIN","The draw pile is empty and neither player can play."
        if g.phase=="draw2":
            return ("YOU MUST DRAW 2 CARDS" if g.current==0 else "THE COMPUTER MUST DRAW 2 CARDS"),"Apply the penalty; the player who played +2 takes the next turn."
        if g.phase=="wild4":
            return ("ACCEPT OR CHALLENGE?" if g.current==0 else "THE COMPUTER IS CONSIDERING YOUR +4"),"A +4 is legal only without a card of the previous active color."
        if g.phase=="opening_color":
            return "AN OPENING WILD","The first player chooses a color."
        if g.current==1:
            return "THE COMPUTER IS THINKING…","Its cards stay hidden."
        if g.phase=="drawn":
            return "PLAY THE CARD YOU DREW?","Play the outlined card, or keep it and pass your turn."
        return "YOUR TURN","Play an outlined card or draw one card."

    def shade(self,p):
        self.canvas.create_rectangle(*p.coords([22,90,1178,795]),fill=NIGHT,stipple="gray50",outline="")
        self.regions=[]

    def draw_color_picker(self,p,title,opening=False):
        self.shade(p)
        p.rect(319,284,562,251,PAPER,outline=HAIRLINE,radius=16)
        p.text(600,320,title,18,INK,True)
        p.text(600,353,"The chosen color applies to the next turn.",12,MUTED)
        for i,(color,fill) in enumerate(COLORS_UI.items()):
            x=356+i*127
            p.rect(x,385,106,83,TABLE,outline=HAIRLINE,radius=8)
            p.family(x+53,411,13,color)
            p.text(x+53,446,COLOR_NAMES_UI[color],12,INK,True)
            self.region(x,385,106,83,"opening_color" if opening else "color",color)
        if not opening:
            p.text(600,504,"Cancel  ·  Escape",11,MUTED)
            self.region(490,485,220,38,"cancel_overlay")

    def draw_challenge(self,p):
        self.shade(p)
        p.rect(295,280,610,325 if self.game.uno_vulnerable==1 else 275,PAPER,radius=24)
        p.text(600,320,"THE COMPUTER PLAYED A +4",21,INK,True)
        p.text(600,376,"Did it hold a card of the previous active color?\nChallenge won: it draws 4 and you play.\nChallenge lost: you draw 6 and skip your turn.",13,MUTED,justify="center")
        p.text(600,438,"Its hand stays hidden; the game checks the rule.",11,MUTED)
        self.button(p,340,478,249,47,"ACCEPT · DRAW 4","accept4")
        self.button(p,609,478,249,47,"CHALLENGE THE +4","challenge4",primary=True)
        if self.game.uno_vulnerable==1:
            self.button(p,442,542,316,42,"FIRST: MISSED CALL!  +2","catch",primary=True)

    def draw_result(self,p):
        self.shade(p)
        g=self.game
        p.rect(327,279,546,285,PAPER,radius=24)
        match_over=max(self.scores)>=500
        if g.phase=="stalled":
            p.text(600,328,"REDEAL THE CARDS",21,INK,True)
            p.text(600,382,"Neither player can make progress.\nNo points are awarded.",14,MUTED)
        else:
            title=("YOU WON THE MATCH!" if g.winner==0 else "THE COMPUTER WINS") if match_over else ("WELL PLAYED!" if g.winner==0 else "ROUND OVER")
            p.text(600,324,title,24,INK,True)
            who="You score" if g.winner==0 else "The computer scores"
            p.text(600,369,f"{who} {g.round_points} points.",16,MUTED)
            p.text(600,411,f"YOU  {self.scores[0]}    —    COMPUTER  {self.scores[1]}",17,INK,True)
            p.text(600,449,"First to 500 points wins.",12,MUTED)
        self.button(p,436,487,328,48,"NEW MATCH" if match_over else "NEXT ROUND","reset" if match_over else "next_round",primary=True)

    def draw_overlay(self,p):
        if self.overlay[0]=="color":
            self.draw_color_picker(p,"CHOOSE YOUR COLOR")
        elif self.overlay[0]=="confirm":
            self.shade(p)
            p.rect(340,310,520,215,PAPER,radius=24)
            p.text(600,351,"START A NEW MATCH?",20,INK,True)
            p.text(600,392,"Your current scores will be reset.",13,MUTED)
            self.button(p,380,447,200,44,"CONTINUE","cancel_overlay")
            self.button(p,610,447,210,44,"START OVER","reset",primary=True)

    def point(self,event):
        return (event.x-self.ox)/self.scale,(event.y-self.oy)/self.scale

    def at(self,x,y,hover=False):
        for a,b,c,d,action,payload in reversed(self.regions):
            if a<=x<=c and b<=y<=d and ((action=="hover_card") if hover else action!="hover_card"):
                return action,payload
        return None

    def on_motion(self,event):
        x,y=self.point(event)
        hit=self.at(x,y,hover=True)
        hover=hit[1] if hit else None
        if hover!=self.hover:
            self.hover=hover
            self.render()
        self.canvas.configure(cursor="hand2" if self.at(x,y) else "")

    def on_leave(self,_event):
        if self.hover is not None:
            self.hover=None
            self.render()

    def on_click(self,event):
        self.canvas.focus_set()
        hit=self.at(*self.point(event))
        if hit:
            self.dispatch(*hit)

    def on_wheel(self,event):
        self.change_page(-1 if event.delta>0 else 1)

    def change_page(self,delta):
        if not self.overlay and self.game.phase not in ("wild4","round_over","stalled","opening_color"):
            self.page=max(0,min(self.page+delta,max(0,(len(self.game.hands[0])-1)//10)))
            self.hover=None
            self.render()

    def on_key(self,event):
        if self.help_window:
            return
        k=event.keysym.lower()
        if k=="escape" and self.overlay:
            self.dispatch("cancel_overlay")
        elif k=="h":
            self.show_help()
        elif k=="n" and self.overlay is None:
            self.dispatch("new_match")
        elif k in ("l","u") and self.game.uno_vulnerable==0 and self.overlay is None:
            self.dispatch("uno")
        elif k=="c" and self.game.uno_vulnerable==1 and self.overlay is None:
            self.dispatch("catch")
        elif self.overlay or self.game.phase in ("wild4","opening_color","round_over","stalled"):
            return
        elif k in ("d","p","space"):
            self.dispatch("pass" if k=="space" and self.game.phase=="drawn" else "draw")
        elif k in ("l","u"):
            self.dispatch("uno")
        elif k in ("left","right"):
            self.change_page(-1 if k=="left" else 1)
        elif k in "1234567890" and len(k)==1:
            i=self.page*10+(int(k)-1)%10
            if i<len(self.game.hands[0]):
                self.dispatch("card",i)

    def dispatch(self,action,payload=None):
        g=self.game
        try:
            if action=="help":
                self.show_help(); return
            if action=="page":
                self.change_page(payload); return
            if action=="new_match":
                self.cancel_ai(); self.overlay=("confirm",); self.render(); return
            if action=="cancel_overlay":
                self.overlay=None; self.refresh(); return
            if action in ("next_round","reset"):
                self.new_round(reset=action=="reset"); return
            if action=="uno":
                if g.uno_vulnerable==0:
                    g.call_uno(0)
                    self.status="You call LAST CARD!"
                elif self.human_play() and len(g.hands[0])==2:
                    self.uno_armed=not self.uno_armed
                    self.render(); return
                else:
                    return
            elif action=="catch":
                if g.uno_vulnerable!=1:
                    return
                g.catch_uno(catcher=0)
                self.status="Missed call: the computer draws 2 cards."
            elif action=="card":
                if not self.human_play() or not g.is_playable(payload,allow_bluff=True):
                    return
                if g.hands[0][payload].color is None:
                    self.overlay=("color",payload); self.hover=None; self.render(); return
                g.play(payload,announce_uno=self.uno_armed)
                self.uno_armed=False
                self.status=""
            elif action=="color":
                if not self.overlay or self.overlay[0]!="color":
                    return
                index=self.overlay[1]
                g.play(index,color=payload,announce_uno=self.uno_armed)
                self.overlay=None
                self.uno_armed=False
                self.status=""
            elif action=="opening_color":
                if g.current!=0 or g.phase!="opening_color":
                    return
                g.choose_opening_color(payload)
                self.status=""
            elif action=="draw":
                if g.phase=="draw2" and g.current==0 and self.overlay is None:
                    g.resolve_draw2()
                    self.uno_armed=False
                    self.status="You draw 2 cards and skip your turn."
                    self.refresh(); return
                if not self.human_play() or g.phase!="play":
                    return
                drawn=g.draw()
                self.uno_armed=False
                if drawn is not None:
                    self.page=(len(g.hands[0])-1)//10
                    self.status="You drew: {}.{}".format(drawn.label,
                        " You can play it or keep it." if g.phase=="drawn" else " It cannot be played.")
                else:
                    self.status="The draw pile is empty."
            elif action=="pass":
                if not self.human_play() or g.phase!="drawn":
                    return
                g.pass_turn()
                self.uno_armed=False
                self.status="You keep the card you drew."
            elif action in ("accept4","challenge4"):
                if g.current!=0 or g.phase!="wild4":
                    return
                g.resolve_wild4(challenge=action=="challenge4")
                self.status=""
            else:
                return
            self.hover=None
            self.refresh()
        except ValueError as exc:
            self.status=str(exc)
            self.render()

    def refresh(self):
        g=self.game
        if g.phase=="round_over" and not self.scored:
            self.scores[g.winner]+=g.round_points
            self.scored=True
        self.render()
        if g.uno_vulnerable==0 and g.current==0 and g.phase not in ("round_over","stalled") and not self.overlay and not self.help_window and self.uno_job is None:
            self.uno_job=self.root.after(1450,self.ai_catch_uno)
        elif g.uno_vulnerable!=0 and self.uno_job is not None:
            self.root.after_cancel(self.uno_job)
            self.uno_job=None
        if g.current==1 and g.phase not in ("round_over","stalled") and not self.overlay and not self.help_window and self.ai_job is None:
            # Also leaves a fair, visible window in which a late human announcement can be called.
            self.ai_job=self.root.after(1450,self.ai_step)

    def ai_catch_uno(self):
        self.uno_job=None
        if self.game.uno_vulnerable==0 and not self.overlay and not self.help_window:
            self.game.catch_uno(catcher=1)
            self.uno_armed=False
            self.status="The computer caught your missed call: draw 2 cards."
            self.refresh()

    def ai_color(self,exclude=None):
        cards=self.game.hands[1]
        counts=Counter(c.color for i,c in enumerate(cards) if c.color and i!=exclude)
        return max(COLORS_UI,key=lambda c:(counts[c],self.rng.random()))

    def ai_step(self):
        self.ai_job=None
        g=self.game
        if g.current!=1 or self.overlay or self.help_window or g.phase in ("round_over","stalled"):
            return
        # The opponent chooses with its own hand and public information only.
        if g.uno_vulnerable==0:
            g.catch_uno(catcher=1)
            self.uno_armed=False
            self.status="The computer caught your missed call: draw 2 cards."
            self.refresh(); return
        if g.phase=="opening_color":
            g.choose_opening_color(self.ai_color())
        elif g.phase=="draw2":
            g.resolve_draw2()
        elif g.phase=="wild4":
            # A bluff is suspected sometimes; no inspection of your hand is used.
            challenge=self.rng.random()<.25
            g.resolve_wild4(challenge=challenge)
        else:
            legal=g.legal_indices(allow_bluff=False)
            # Infrequent, contestable +4 bluffs make the challenge rule useful.
            if g.phase=="play" and self.rng.random()<.08:
                bluff=[i for i,c in enumerate(g.hands[1]) if c.value=="wild4"]
                if bluff:
                    legal=bluff
            if legal:
                counts=Counter(c.color for c in g.hands[1] if c.color)
                def rank(i):
                    c=g.hands[1][i]
                    action={"skip":26,"reverse":26,"draw2":30,"wild":-14,"wild4":-18}.get(c.value, int(c.value) if c.value.isdigit() else 0)
                    return action+counts[c.color]*3+self.rng.random()*4
                index=max(legal,key=rank)
                card=g.hands[1][index]
                color=self.ai_color(index) if card.color is None else None
                g.play(index,color=color,announce_uno=self.rng.random()>.12)
            elif g.phase=="drawn":
                g.pass_turn()
            else:
                g.draw()
                if g.phase=="drawn" and g.current==1:
                    self.status="The computer drew a card it can play."
                    self.refresh(); return
        self.status=""
        self.hover=None
        self.refresh()

    def describe_card(self,card):
        color=COLOR_NAMES_UI.get(card.color,"").lower()
        desc={"skip":"Pause: you play again.","reverse":"Reverse: with two players, you play again.",
              "draw2":"+2: your opponent draws two and skips a turn.",
              "wild":"Wild: choose the next color.",
              "wild4":"+4: choose a color; a bluff can be challenged."}.get(card.value,f"{card.value} {color}: match the color or number.")
        return (f"{color.capitalize()} · " if color and not card.value.isdigit() else "")+desc

    def show_help(self):
        if self.help_window:
            self.help_window.lift(); return
        self.cancel_ai()
        top=tk.Toplevel(self.root)
        self.help_window=top
        top.title("Rules and controls · Shardturn")
        top.geometry("760x690")
        top.configure(bg=BG)
        top.transient(self.root)
        bar=tk.Scrollbar(top)
        bar.pack(side="right",fill="y")
        text=tk.Text(top,bg=BG,fg=INK,font=(FONT_FAMILY,11),wrap="word",padx=24,pady=24,
                     relief="flat",yscrollcommand=bar.set,selectbackground="#446c70")
        text.pack(fill="both",expand=True)
        bar.config(command=text.yview)
        text.insert("1.0",RULES)
        text.configure(state="disabled")
        def closed():
            self.help_window=None
            top.destroy()
            self.refresh()
        top.protocol("WM_DELETE_WINDOW",closed)
        top.bind("<Escape>",lambda e:closed())
        top.grab_set()


def main():
    parser=argparse.ArgumentParser(description="Shardturn: an offline color card duel against the computer.")
    parser.add_argument("--seed",type=int,help="Reproducible shuffle seed, for testing.")
    args=parser.parse_args()
    try:
        root=tk.Tk()
    except tk.TclError as exc:
        raise SystemExit("Cannot open the window. Run the game in a graphical desktop session.\n"
                         "Debian/Ubuntu: sudo apt install python3-tk\n"
                         "Manjaro: sudo pacman -S tk\n"+str(exc)) from exc
    ShardturnApp(root,seed=args.seed)
    root.mainloop()


if __name__=="__main__":
    main()
