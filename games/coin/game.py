#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-or-later
"""A lightweight, accessible coin toss application using Tkinter."""
from __future__ import annotations

import argparse
import secrets
from pathlib import Path
import tkinter as tk
from tkinter import ttk


def toss() -> str:
    """Return a fair cryptographically independent coin toss."""
    return ("Heads", "Tails")[secrets.randbelow(2)]


class CoinApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Coin Flip · Hamdy Abou El Anein")
        self.geometry("430x370")
        self.minsize(360, 310)
        self.configure(bg="#101827")
        self.count = 0
        self.heads = 0
        self.result = tk.StringVar(value="Ready to flip?")
        self.statistics = tk.StringVar(value="0 flips · 0 heads · 0 tails")

        body = tk.Frame(self, bg="#101827", padx=32, pady=24)
        body.pack(expand=True, fill="both")
        tk.Label(body, text="COIN FLIP", font=("DejaVu Sans", 13, "bold"),
                 fg="#8bd6c1", bg="#101827").pack(pady=(0, 14))
        images = Path(__file__).resolve().parent / "images"
        self.faces = {key: tk.PhotoImage(file=str(images / name)) for key, name in
                      (("Heads", "face.gif"), ("Tails", "pile.gif"), ("Ready", "full.gif"))}
        self.coin = tk.Label(body, image=self.faces["Ready"], bg="#101827")
        self.coin.pack()
        tk.Label(body, textvariable=self.result, font=("DejaVu Sans", 21, "bold"),
                 fg="#f7fafc", bg="#101827").pack(pady=(6, 12))
        tk.Label(body, textvariable=self.statistics, font=("DejaVu Sans", 10),
                 fg="#bac8d9", bg="#101827").pack()
        actions = tk.Frame(body, bg="#101827")
        actions.pack(pady=25)
        tk.Button(actions, text="Flip coin", command=self.flip, bg="#7ddcc0",
                  fg="#10211c", activebackground="#a8f0d9", font=("DejaVu Sans", 11, "bold"),
                  relief="flat", padx=20, pady=10).pack(side="left", padx=6)
        tk.Button(actions, text="Reset", command=self.reset, bg="#2a3a51",
                  fg="#ffffff", activebackground="#435672", relief="flat",
                  padx=16, pady=10).pack(side="left", padx=6)
        self.bind("<space>", lambda _event: self.flip())

    def flip(self) -> None:
        value = toss()
        self.count += 1
        self.heads += value == "Heads"
        self.coin.config(image=self.faces[value])
        self.result.set(value)
        self.statistics.set(f"{self.count} flips · {self.heads} heads · {self.count - self.heads} tails")

    def reset(self) -> None:
        self.count = self.heads = 0
        self.coin.config(image=self.faces["Ready"])
        self.result.set("Ready to flip?")
        self.statistics.set("0 flips · 0 heads · 0 tails")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flip", action="store_true", help="Toss once in the terminal")
    args = parser.parse_args()
    if args.flip:
        print(toss())
    else:
        CoinApp().mainloop()


if __name__ == "__main__":
    main()
