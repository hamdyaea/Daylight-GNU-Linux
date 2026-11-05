#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-or-later
"""A minimal dice roller with configurable dice and a Tkinter interface."""
from __future__ import annotations

import argparse
import secrets
from pathlib import Path
import tkinter as tk


def roll(sides: int = 6, count: int = 1) -> tuple[int, ...]:
    if not 2 <= sides <= 1000:
        raise ValueError("sides must be between 2 and 1000")
    if not 1 <= count <= 20:
        raise ValueError("count must be between 1 and 20")
    return tuple(secrets.randbelow(sides) + 1 for _ in range(count))


class DiceApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Dice Simulator · Hamdy Abou El Anein")
        self.configure(bg="#101827", padx=24, pady=20)
        images = Path(__file__).resolve().parent / "images"
        self.faces = {n: tk.PhotoImage(file=str(images / f"dice{n}.gif")) for n in range(1, 7)}
        self.face = tk.Label(self, bg="#101827")
        self.face.pack()
        self.result = tk.StringVar()
        tk.Label(self, textvariable=self.result, bg="#101827", fg="#f2c879",
                 font=("DejaVu Sans", 15, "bold")).pack(pady=10)
        tk.Button(self, text="Roll again", command=self.throw, padx=14, pady=6).pack()
        self.throw()
        self.bind("<space>", lambda _event: self.throw())

    def throw(self) -> None:
        value, = roll()
        self.face.configure(image=self.faces[value])
        self.result.set(str(value))



def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roll", action="store_true", help="Roll in the terminal")
    parser.add_argument("--sides", type=int, default=6)
    parser.add_argument("--count", type=int, default=1)
    args = parser.parse_args()
    if args.roll:
        print(" ".join(map(str, roll(args.sides, args.count))))
    else:
        DiceApp().mainloop()


if __name__ == "__main__":
    main()
