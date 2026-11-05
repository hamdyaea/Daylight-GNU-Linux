#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Virtual-credit slot machine demonstration; no real-money betting."""
from __future__ import annotations
import argparse
from dataclasses import dataclass
import secrets
import shutil
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk

SYMBOLS = ("BAR", "CHERRY", "SEVEN")
STARTING_CREDITS = 100
STAKE = 10

def payout(reels: tuple[str, str, str]) -> int:
    if len(reels) != 3 or any(x not in SYMBOLS for x in reels):
        raise ValueError("Invalid reel symbols")
    if len(set(reels)) == 1:
        return 50
    if len(set(reels)) == 2:
        return 20
    return 0

@dataclass
class Game:
    credits: int = STARTING_CREDITS
    rounds: int = 0

    def spin(self, reels: tuple[str, str, str] | None = None) -> tuple[tuple[str, str, str], int]:
        if self.credits < STAKE:
            raise ValueError("Insufficient virtual credits")
        if reels is None:
            reels = tuple(secrets.choice(SYMBOLS) for _ in range(3))
        reward = payout(reels)
        self.credits += reward - STAKE
        self.rounds += 1
        return reels, reward

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true", help="Play one spin in terminal")
    args = parser.parse_args()
    game = Game()
    if args.text:
        reels, reward = game.spin()
        print(f"{' | '.join(reels)}; payout {reward}; balance {game.credits} virtual credits")
        return
    root = tk.Tk()
    root.title("Casino Slot Machine")
    ClassicSlots(root)
    root.mainloop()


class ClassicSlots(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=16)
        self.pack()
        folder = Path(__file__).resolve().parent
        artwork = {"BAR": "bar", "CHERRY": "cherry", "SEVEN": "lucky-seven"}
        self.faces = {symbol: tk.PhotoImage(file=str(folder / "images" / (name + ".gif"))).subsample(3)
                      for symbol, name in artwork.items()}
        self.sound = folder / "sounds" / "SlotMachine.wav"
        self.audio = None
        self.timer = None
        ttk.Label(self, text="Casino Slot Machine", font=("sans", 18, "bold")).pack()
        reels = ttk.Frame(self)
        reels.pack(pady=12)
        self.reels = []
        for symbol in SYMBOLS:
            reel = ttk.Label(reels, image=self.faces[symbol], relief="ridge")
            reel.pack(side="left", padx=2)
            self.reels.append(reel)
        self.info = tk.StringVar()
        ttk.Label(self, textvariable=self.info, justify="center").pack()
        ttk.Label(self, text="Pair: +200   •   Triple: +300   •   All different: winnings reset").pack(pady=6)
        self.spin_button = ttk.Button(self, text="Spin · 100 play credits", command=self.spin)
        self.spin_button.pack(pady=5)
        ttk.Button(self, text="New game", command=self.reset).pack()
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.reset()

    def reset(self):
        self.cancel_spin()
        self.winnings, self.staked = STARTING_CREDITS, 0
        self.display(SYMBOLS)
        self.info.set("Winnings: 100   •   Total staked: 0")
        self.spin_button.state(["!disabled"])

    def display(self, symbols):
        for reel, symbol in zip(self.reels, symbols):
            reel.configure(image=self.faces[symbol])

    def spin(self):
        if self.timer is not None:
            return
        self.spin_button.state(["disabled"])
        self.staked += 100
        result = tuple(secrets.choice(SYMBOLS) for _ in self.reels)
        player = shutil.which("paplay") or shutil.which("aplay")
        if player and self.sound.is_file():
            self.audio = subprocess.Popen([player, str(self.sound)], stderr=subprocess.DEVNULL)
        def advance(frame):
            if frame < 8:
                self.display(tuple(secrets.choice(SYMBOLS) for _ in self.reels))
                self.timer = self.after(85, advance, frame + 1)
                return
            self.timer = None
            self.display(result)
            count = len(set(result))
            if count == 3:
                self.winnings = 0
                message = "All different"
            else:
                self.winnings += 300 if count == 1 else 200
                message = "Three of a kind!" if count == 1 else "Pair!"
            self.info.set(f"{message}   •   Winnings: {self.winnings}   •   Total staked: {self.staked}")
            self.spin_button.state(["!disabled"])
        advance(0)

    def cancel_spin(self):
        if self.timer is not None:
            self.after_cancel(self.timer)
            self.timer = None
        if self.audio is not None and self.audio.poll() is None:
            self.audio.terminate()

    def close(self):
        self.cancel_spin()
        self.master.destroy()


if __name__ == "__main__":
    main()
