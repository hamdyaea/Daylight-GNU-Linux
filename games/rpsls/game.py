#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Rock, Paper, Scissors, Lizard, Spock with Tkinter and CLI."""
from __future__ import annotations
import argparse
import secrets
from pathlib import Path
import tkinter as tk
from tkinter import ttk

CHOICES = ("Rock", "Paper", "Scissors", "Lizard", "Spock")
# Each pair means the first choice beats the second, with a description.
RULES = {
    ("Scissors", "Paper"): "Scissors cuts Paper",
    ("Paper", "Rock"): "Paper covers Rock",
    ("Rock", "Lizard"): "Rock crushes Lizard",
    ("Lizard", "Spock"): "Lizard poisons Spock",
    ("Spock", "Scissors"): "Spock smashes Scissors",
    ("Scissors", "Lizard"): "Scissors decapitates Lizard",
    ("Lizard", "Paper"): "Lizard eats Paper",
    ("Paper", "Spock"): "Paper disproves Spock",
    ("Spock", "Rock"): "Spock vaporizes Rock",
    ("Rock", "Scissors"): "Rock crushes Scissors",
}

def outcome(player: str, computer: str) -> tuple[int, str]:
    if player not in CHOICES or computer not in CHOICES:
        raise ValueError("Unknown choice")
    if player == computer:
        return 0, "Tie"
    if (player, computer) in RULES:
        return 1, RULES[(player, computer)]
    return -1, RULES[(computer, player)]

class Game(ttk.Frame):
    def __init__(self, root: tk.Tk):
        super().__init__(root, padding=20)
        self.pack(fill="both", expand=True)
        self.player_score = 0
        self.computer_score = 0
        self.result = tk.StringVar(value="Choose your move")
        self.score = tk.StringVar(value="You 0 — Computer 0")
        ttk.Label(self, text="Rock · Paper · Scissors · Lizard · Spock").pack(pady=10)
        buttons = ttk.Frame(self)
        buttons.pack()
        folder = Path(__file__).resolve().parent / "images"
        self.images = {name: tk.PhotoImage(file=str(folder / (name.lower() + ".gif"))).subsample(3)
                       for name in CHOICES}
        for choice in CHOICES:
            ttk.Button(buttons, text=choice, image=self.images[choice], compound="top", command=lambda c=choice: self.play(c)).pack(side="left", padx=3)
        duel = ttk.Frame(self)
        duel.pack(pady=6)
        self.player_card = ttk.Label(duel, text="You", compound="top")
        self.computer_card = ttk.Label(duel, text="Computer", compound="top")
        self.player_card.pack(side="left", padx=12)
        self.computer_card.pack(side="left", padx=12)
        ttk.Label(self, textvariable=self.result, wraplength=500).pack(pady=16)
        ttk.Label(self, textvariable=self.score).pack(pady=6)
        ttk.Button(self, text="Reset scores", command=self.reset).pack(pady=12)

    def play(self, player: str) -> None:
        computer = secrets.choice(CHOICES)
        self.player_card.configure(image=self.images[player])
        self.computer_card.configure(image=self.images[computer])
        winner, explanation = outcome(player, computer)
        if winner > 0:
            self.player_score += 1
        elif winner < 0:
            self.computer_score += 1
        status = "You win" if winner > 0 else "Computer wins" if winner < 0 else "Tie"
        self.result.set(f"You: {player} | Computer: {computer}\n{status} — {explanation}")
        self.score.set(f"You {self.player_score} — Computer {self.computer_score}")

    def reset(self) -> None:
        self.player_card.configure(image="")
        self.computer_card.configure(image="")
        self.player_score = self.computer_score = 0
        self.result.set("Choose your move")
        self.score.set("You 0 — Computer 0")

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--choice", choices=CHOICES, help="Play one round in terminal")
    args = parser.parse_args()
    if args.choice:
        computer = secrets.choice(CHOICES)
        result, reason = outcome(args.choice, computer)
        print(f"You: {args.choice}; Computer: {computer}; Result: {result}; {reason}")
        return
    root = tk.Tk()
    root.title("Rock Paper Scissors Lizard Spock")
    Game(root)
    root.mainloop()

if __name__ == "__main__":
    main()
