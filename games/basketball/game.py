#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Historical NBA conference playoff simulator with Tkinter."""
from __future__ import annotations
import argparse
import random
from pathlib import Path
import tkinter as tk
from tkinter import ttk

EAST = (
    "Boston Celtics", "Toronto Raptors", "Cleveland Cavaliers", "Indiana Pacers",
    "Detroit Pistons", "Milwaukee Bucks", "Washington Wizards", "New York Knicks",
    "Miami Heat", "Philadelphia 76ers", "Brooklyn Nets", "Charlotte Hornets",
    "Orlando Magic", "Chicago Bulls", "Atlanta Hawks",
)
WEST = (
    "Houston Rockets", "Golden State Warriors", "San Antonio Spurs",
    "Minnesota Timberwolves", "Oklahoma City Thunder", "Denver Nuggets",
    "Portland Trail Blazers", "New Orleans Pelicans", "Utah Jazz",
    "Los Angeles Clippers", "Los Angeles Lakers", "Sacramento Kings",
    "Phoenix Suns", "Memphis Grizzlies", "Dallas Mavericks",
)

def championship(seed=None):
    """Yield one stage per click, advancing only the winners in each conference."""
    rng = random.Random(seed)
    east, west = rng.sample(EAST, 8), rng.sample(WEST, 8)
    yield "Playoff field", "nbaLogo.gif", [
        "Eastern Conference", *east, "", "Western Conference", *west
    ]
    for title in ("First round", "Conference semifinals", "Conference finals"):
        results = []
        for name, contenders in (("Eastern Conference", east), ("Western Conference", west)):
            results.append(name)
            winners = []
            for home, away in zip(contenders[::2], contenders[1::2]):
                winner = rng.choice((home, away))
                winners.append(winner)
                results.append(f"{home} vs {away}  →  {winner}")
            contenders[:] = winners
            results.append("")
        yield title, "nba-map.gif", results
    yield "NBA Final", "nbaFinal.gif", [f"{east[0]} vs {west[0]}"]
    champion = rng.choice((east[0], west[0]))
    yield "NBA Champion", "winneNBA.gif", [champion]


def simulate(seed: int | None = None) -> tuple[str, list[str]]:
    history = []
    for title, _, lines in championship(seed):
        history.extend([title, *lines, ""])
    return lines[0], history


class Playoffs(ttk.Frame):
    def __init__(self, root, seed=None):
        super().__init__(root, padding=12)
        self.pack(fill="both", expand=True)
        self.seed = seed
        folder = Path(__file__).resolve().parent / "images"
        self.images = {path.name: tk.PhotoImage(file=str(path)).subsample(2)
                       for path in folder.glob("*.gif")}
        self.heading = ttk.Label(self, font=("sans", 16, "bold"))
        self.heading.pack()
        self.image = ttk.Label(self)
        self.image.pack(pady=4)
        self.body = tk.Text(self, width=66, height=15, wrap="word", font=("sans", 11))
        scroll = ttk.Scrollbar(self, command=self.body.yview)
        self.body.configure(yscrollcommand=scroll.set)
        self.next = ttk.Button(self, command=self.advance)
        self.next.pack(side="bottom", pady=6)
        scroll.pack(side="right", fill="y")
        self.body.pack(fill="both", expand=True)
        self.restart()

    def restart(self):
        self.stages = championship(self.seed)
        self.next.configure(command=self.advance)
        self.advance()

    def advance(self):
        title, artwork, lines = next(self.stages)
        self.heading.configure(text=title)
        self.image.configure(image=self.images[artwork])
        self.body.configure(state="normal")
        self.body.delete("1.0", "end")
        self.body.insert("1.0", "\n".join(lines))
        self.body.configure(state="disabled")
        if title == "NBA Champion":
            self.next.configure(text="New championship", command=self.restart)
        else:
            self.next.configure(text="Reveal champion" if title == "NBA Final" else "Next round")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.text:
        print("\n".join(simulate(args.seed)[1]))
        return
    root = tk.Tk()
    root.title("NBA Simulator — Historical Playoffs")
    Playoffs(root, args.seed)
    root.mainloop()

if __name__ == "__main__":
    main()
