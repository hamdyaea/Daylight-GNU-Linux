#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Simple six-card memory matching game for children."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
from pathlib import Path
import tkinter as tk
from tkinter import ttk

SYMBOLS = ("child", "cop", "girl")

def shuffled_cards() -> list[str]:
    cards = list(SYMBOLS) * 2
    secrets.SystemRandom().shuffle(cards)
    return cards

@dataclass
class MemoryGame:
    cards: list[str] = field(default_factory=shuffled_cards)
    revealed: list[int] = field(default_factory=list)
    matched: set[int] = field(default_factory=set)
    moves: int = 0

    def select(self, index: int) -> str:
        if not 0 <= index < len(self.cards):
            raise ValueError("Card index out of range")
        if index in self.matched or index in self.revealed or len(self.revealed) >= 2:
            return "ignored"
        self.revealed.append(index)
        if len(self.revealed) < 2:
            return "first"
        self.moves += 1
        first, second = self.revealed
        if self.cards[first] == self.cards[second]:
            self.matched.update((first, second))
            self.revealed.clear()
            return "match"
        return "mismatch"

    def hide_unmatched(self) -> None:
        self.revealed.clear()

    @property
    def won(self) -> bool:
        return len(self.matched) == len(self.cards)

def main() -> None:
    root = tk.Tk()
    root.title("Memory Game for Children")
    game = MemoryGame()
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)
    info = tk.StringVar(value="Find the three matching pairs!")
    ttk.Label(frame, textvariable=info).pack(pady=10)
    board = ttk.Frame(frame)
    board.pack()
    images = Path(__file__).resolve().parent / "images"
    faces = {name: tk.PhotoImage(file=str(images / f"{name}.gif")) for name in SYMBOLS}
    backs = [tk.PhotoImage(file=str(images / f"back{i}.gif")) for i in range(1, 7)]
    buttons = []
    waiting = False
    def render() -> None:
        for i, button in enumerate(buttons):
            show = i in game.revealed or i in game.matched
            button.configure(image=faces[game.cards[i]] if show else backs[i])
    def click(index: int) -> None:
        nonlocal waiting
        if waiting:
            return
        result = game.select(index)
        render()
        if result == "match":
            info.set("Well done! " + ("All pairs found!" if game.won else f"Moves: {game.moves}"))
        elif result == "mismatch":
            info.set("Try again!")
            waiting = True
            def hide() -> None:
                nonlocal waiting
                game.hide_unmatched()
                waiting = False
                render()
            root.after(900, hide)
        elif result == "first":
            info.set("Find its matching card")
    for i in range(6):
        button = ttk.Button(board, image=backs[i], command=lambda n=i: click(n))
        button.grid(row=i // 3, column=i % 3, padx=4, pady=6)
        buttons.append(button)
    def restart() -> None:
        nonlocal game, waiting
        if waiting:
            return
        game = MemoryGame()
        info.set("Find the three matching pairs!")
        render()
    ttk.Button(frame, text="New game", command=restart).pack(pady=12)
    root.mainloop()

if __name__ == "__main__":
    main()
