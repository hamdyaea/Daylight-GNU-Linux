#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein
# Contact: info@daylightlinux.ch
# SPDX-License-Identifier: GPL-3.0-only
"""Entertainment-only simulator using the 2018 World Cup group roster."""
from __future__ import annotations
from pathlib import Path
import argparse
import random
import tkinter as tk
from tkinter import ttk

GROUPS = {
    "A": ("Russia", "Saudi Arabia", "Egypt", "Uruguay"),
    "B": ("Portugal", "Spain", "Morocco", "Iran"),
    "C": ("France", "Australia", "Peru", "Denmark"),
    "D": ("Argentina", "Iceland", "Croatia", "Nigeria"),
    "E": ("Brazil", "Switzerland", "Costa Rica", "Serbia"),
    "F": ("Germany", "Mexico", "Sweden", "South Korea"),
    "G": ("Belgium", "Panama", "Tunisia", "England"),
    "H": ("Poland", "Colombia", "Senegal", "Japan"),
}

def simulate(seed: int | None = None) -> tuple[str, list[str]]:
    rng = random.Random(seed)
    if len({team for group in GROUPS.values() for team in group}) != 32:
        raise ValueError("Expected 32 distinct teams")
    lines = ["2018 World Cup fictional simulation", ""]
    qualifiers = {}
    for name, teams in GROUPS.items():
        order = rng.sample(teams, len(teams))
        qualifiers[name] = order[:2]
        lines.append(f"Group {name}: {order[0]} / {order[1]} qualify")
    keys = list(GROUPS)
    bracket = []
    for i in range(0, 8, 2):
        left, right = keys[i], keys[i + 1]
        bracket.extend([(qualifiers[left][0], qualifiers[right][1]),
                        (qualifiers[right][0], qualifiers[left][1])])
    for round_name in ("Round of 16", "Quarterfinals", "Semifinals", "Final"):
        lines.extend(("", round_name))
        winners = []
        for a, b in bracket:
            winner = rng.choice((a, b))
            winners.append(winner)
            lines.append(f"{a} vs {b} -> {winner}")
        bracket = list(zip(winners[::2], winners[1::2]))
    return winners[0], lines

def tournament_stages(seed=None):
    """Preserve the historical roster and advance one knockout round at a time."""
    rng = random.Random(seed)
    groups = {name: rng.sample(teams, len(teams)) for name, teams in GROUPS.items()}
    stages = [("Group qualifiers", [(name, order) for name, order in groups.items()])]
    keys = list(groups)
    bracket = []
    for i in range(0, 8, 2):
        a, b = groups[keys[i]], groups[keys[i + 1]]
        bracket.extend([(a[0], b[1]), (b[0], a[1])])
    for title in ("Round of 16", "Quarterfinals", "Semifinals", "Final"):
        matches = [(a, b, rng.choice((a, b))) for a, b in bracket]
        stages.append((title, matches))
        winners = [match[2] for match in matches]
        bracket = list(zip(winners[::2], winners[1::2]))
    stages.append(("Champion", winners[0]))
    return stages


class TournamentWindow(tk.Tk):
    def __init__(self, seed=None):
        super().__init__()
        self.seed = seed
        self.title("2018 World Cup Simulator")
        self.geometry("900x760")
        self.minsize(680, 600)
        self.configure(bg="#102335")
        self.images = [tk.PhotoImage(file=str(Path(__file__).resolve().parent / "images" / name))
                       for name in ("beginIMG-ui.png", "winnerIMG-ui.png")]
        self.heading = ttk.Label(self, font=("Sans", 22, "bold"), anchor="center")
        self.heading.pack(fill="x", pady=(14, 4))
        ttk.Label(self, text="Historical 2018 teams · Fictional random simulation", anchor="center").pack(fill="x")
        self.art = tk.Label(self, bg="#102335", image=self.images[0])
        self.art.pack(pady=8)
        self.canvas = tk.Canvas(self, bg="#102335", highlightthickness=0)
        self.scroll = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scroll.set)
        self.controls = ttk.Frame(self, padding=10)
        self.controls.pack(side="bottom", fill="x")
        self.next_button = ttk.Button(self.controls, command=self.advance)
        self.next_button.pack(side="right", padx=10)
        ttk.Button(self.controls, text="New tournament", command=self.reset).pack(side="left")
        self.progress = ttk.Label(self.controls)
        self.progress.pack(side="left", padx=20)
        self.canvas.pack(fill="both", expand=True, padx=16)
        self.board = ttk.Frame(self.canvas, padding=8)
        self.board_id = self.canvas.create_window(0, 0, anchor="nw", window=self.board)
        self.board.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda event: self.canvas.itemconfigure(self.board_id, width=event.width))
        self.reset()

    def reset(self):
        self.stages = tournament_stages(self.seed)
        self.index = -1
        self.render()

    def advance(self):
        if self.index < len(self.stages) - 1:
            self.index += 1
            self.render()

    def render(self):
        for child in self.board.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)
        self.board.columnconfigure((0, 1), weight=1)
        title, data = ("World Cup 2018", None) if self.index < 0 else self.stages[self.index]
        self.heading.configure(text=title)
        self.art.configure(image=self.images[1 if title == "Champion" else 0])
        self.progress.configure(text="Start" if self.index < 0 else f"Stage {self.index + 1} / {len(self.stages)}")
        if self.index < 0:
            ttk.Label(self.board, text="32 teams. Eight groups. One champion.\nReveal the qualifiers, then play each round.",
                      font=("Sans", 15), justify="center", anchor="center").grid(row=0, column=0, columnspan=2, sticky="ew", pady=25)
        elif title == "Group qualifiers":
            for i, (group, teams) in enumerate(data):
                box = ttk.LabelFrame(self.board, text="Group " + group, padding=12)
                box.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
                for rank, team in enumerate(teams):
                    ttk.Label(box, text=f"{rank + 1}. {team}" + ("  — Qualified" if rank < 2 else ""),
                              font=("Sans", 12, "bold" if rank < 2 else "normal")).pack(anchor="w", pady=3)
        elif title == "Champion":
            ttk.Label(self.board, text=data, font=("Sans", 30, "bold"), anchor="center").grid(row=0, column=0, columnspan=2, sticky="ew", pady=25)
            ttk.Label(self.board, text="World Cup winner", font=("Sans", 16), anchor="center").grid(row=1, column=0, columnspan=2, sticky="ew")
        else:
            for i, (a, b, winner) in enumerate(data):
                box = ttk.LabelFrame(self.board, text=f"Match {i + 1}", padding=14)
                box.grid(row=i // 2, column=i % 2, sticky="nsew", padx=6, pady=6)
                ttk.Label(box, text=a + "  vs  " + b, font=("Sans", 13), wraplength=300).pack(pady=5)
                ttk.Label(box, text="Winner: " + winner, font=("Sans", 13, "bold"), foreground="#167344").pack(pady=5)
        next_label = "Reveal group qualifiers" if self.index < 0 else ("Show " + self.stages[self.index + 1][0] if self.index < len(self.stages) - 1 else "Tournament complete")
        self.next_button.configure(text=next_label, state="disabled" if title == "Champion" else "normal")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", action="store_true")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.text:
        winner, lines = simulate(args.seed)
        print("\n".join(lines + ["", f"Champion: {winner}"]))
    else:
        TournamentWindow(args.seed).mainloop()


if __name__ == "__main__":
    main()
