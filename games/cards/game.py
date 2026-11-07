#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: hamdy.aea@protonmail.com
# SPDX-License-Identifier: GPL-3.0-or-later
"""Modern Tkinter card game (War / Battle) using the original card artwork."""
from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from battle_core import BattleGame, Card

ROOT = Path(__file__).resolve().parent
PICTURES = ROOT / "Pictures"


def image_filename(card: Card) -> str:
    """Map modern card model to historical filenames (including old typos)."""
    suit = card.suit
    if card.rank == 14:
        return {"Carreaux": "AsDeCaraux.jpg", "Coeur": "AsDeCoeur.jpg",
                "Piques": "AsDePique.jpg", "treffles": "AsDeTreffles.jpg"}[suit]
    face = {11: "Valet", 12: "Reine", 13: "Roi"}.get(card.rank, str(card.rank))
    if card.rank == 5 and suit == "Coeur":
        return "5coeur.jpg"
    if card.rank in (11, 12, 13) and suit == "treffles":
        return f"{face}Treffles.jpg"
    return f"{face}{suit}.jpg"


class BattleWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Battle Cards — War")
        self.geometry("780x710")
        self.minsize(640, 640)
        self.configure(bg="#132236")
        self.game = BattleGame()
        self.steps = None
        self.images: list[object] = []
        self._setup()
        self._update_scores()

    def _setup(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="Battle Cards", font=("Sans", 24, "bold")).pack(pady=(0, 10))
        ttk.Label(frame, text="Ace high. On a tie, play one card face down and one face up.").pack()
        self.scores = ttk.Label(frame, font=("Sans", 14, "bold"))
        self.scores.pack(pady=12)
        cards = ttk.Frame(frame)
        cards.pack(expand=True, fill="both")
        cards.columnconfigure((0, 1), weight=1)
        self.card_views = []
        for col, label in enumerate(("You", "Computer")):
            cell = ttk.Frame(cards, padding=12)
            cell.grid(row=0, column=col, sticky="nsew")
            ttk.Label(cell, text=label, font=("Sans", 14)).pack()
            image = ttk.Label(cell, text="?", anchor="center")
            image.pack(expand=True, pady=8)
            name = ttk.Label(cell, text="Face down")
            name.pack()
            self.card_views.append((image, name))
        self.message = ttk.Label(frame, text="Click Play round to start",
                                 font=("Sans", 12), anchor="center")
        self.message.pack(pady=12)
        controls = ttk.Frame(frame)
        controls.pack()
        self.play_button = ttk.Button(controls, text="Play round", command=self.play_round)
        self.play_button.pack(side="left", padx=8)
        ttk.Button(controls, text="New game", command=self.new_game).pack(side="left", padx=8)
        self.counter = ttk.Label(frame, text="Round 0")
        self.counter.pack(pady=4)
        self.gallery = tk.Canvas(frame, height=110, highlightthickness=0)
        self.gallery.pack(fill="x")
        self.scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.gallery.xview)
        self.scroll.pack(fill="x")
        self.gallery.configure(xscrollcommand=self.scroll.set)
        self.prize_images = []


    def _show_card(self, card: Card | None, label: ttk.Label, name: ttk.Label):
        if card is None:
            label.configure(image="", text="—")
            name.configure(text="No card")
            return
        name.configure(text=card.name)
        filename = PICTURES / image_filename(card)
        try:
            from PIL import Image, ImageTk
            with Image.open(filename) as source:
                source.thumbnail((190, 260))
                photo = ImageTk.PhotoImage(source.copy())
            label.configure(image=photo, text="")
            self.images.append(photo)
            self.images = self.images[-4:]
        except (ImportError, OSError):
            label.configure(image="", text=card.name)

    def _update_scores(self):
        self.scores.configure(text=f"You: {len(self.game.player)} cards  |  "
                                   f"Computer: {len(self.game.computer)} cards")
        self.counter.configure(text=f"Round {self.game.rounds}")

    def _clear_prize(self):
        self.gallery.delete("all")
        self.gallery.xview_moveto(0)
        self.prize_images.clear()
        self.gallery.configure(scrollregion=(0, 0, 0, 110))

    def _show_prize(self, cards):
        for index, card in enumerate(cards):
            x = 65 + index * 130
            try:
                from PIL import Image, ImageTk
                with Image.open(PICTURES / image_filename(card)) as source:
                    source.thumbnail((64, 80))
                    photo = ImageTk.PhotoImage(source.copy())
                self.prize_images.append(photo)
                self.gallery.create_image(x, 42, image=photo)
            except (ImportError, OSError):
                pass
            self.gallery.create_text(x, 96, text=card.name)
        self.gallery.configure(scrollregion=(0, 0, len(cards) * 130, 110))

    def play_round(self):
        if self.steps is None:
            if self.game.winner is not None:
                return
            self._clear_prize()
            self.steps = self.game.round_steps()
        outcome = next(self.steps)
        for card, (image, label) in zip(
            (outcome.player_card, outcome.computer_card), self.card_views
        ):
            if card is None:
                image.configure(image="", text="🂠", font=("DejaVu Sans", 90))
                label.configure(text="Face down")
            else:
                self._show_card(card, image, label)
        if outcome.winner is None:
            self.play_button.configure(text="Continue battle")
            action = ("Tie! Continue the battle." if outcome.player_card
                      else "One card each, face down.")
            self.message.configure(text=f"{action}   Cards in pile: {outcome.cards_at_stake}")
        else:
            self.steps = None
            who = {"player": "You won", "computer": "Computer won",
                   "draw": "Both players split"}[outcome.winner]
            ending = " Game over." if outcome.game_over else ""
            self.message.configure(text=f"{who} the pile of {outcome.cards_at_stake} cards.{ending}")
            self.play_button.configure(text="Play round", state="disabled" if outcome.game_over else "normal")
            self._show_prize(outcome.collected)
        self._update_scores()

    def new_game(self):
        self.game = BattleGame()
        self.steps = None
        self._clear_prize()
        self.images.clear()
        for image, label in self.card_views:
            image.configure(image="", text="?", font="TkDefaultFont")
            label.configure(text="Face down")
        self.message.configure(text="Click Play round to start")
        self.play_button.configure(text="Play round", state="normal")
        self._update_scores()


if __name__ == "__main__":
    BattleWindow().mainloop()
