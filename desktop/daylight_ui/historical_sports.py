"""Historical NBA and FIFA 2018 rosters; fictional offline simulations.

The tournament formats, conference structure, teams and World Cup group
assignments match their historical competitions. Results are random and are
never presented as actual historical scores.
SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations
import random

EAST = (
    "Boston Celtics", "Toronto Raptors", "Cleveland Cavaliers",
    "Indiana Pacers", "Detroit Pistons", "Milwaukee Bucks",
    "Washington Wizards", "New York Knicks", "Miami Heat",
    "Philadelphia 76ers", "Brooklyn Nets", "Charlotte Hornets",
    "Orlando Magic", "Chicago Bulls", "Atlanta Hawks",
)
WEST = (
    "Houston Rockets", "Golden State Warriors", "San Antonio Spurs",
    "Minnesota Timberwolves", "Oklahoma City Thunder", "Denver Nuggets",
    "Portland Trail Blazers", "New Orleans Pelicans", "Utah Jazz",
    "Los Angeles Clippers", "Los Angeles Lakers", "Sacramento Kings",
    "Phoenix Suns", "Memphis Grizzlies", "Dallas Mavericks",
)
WORLD_CUP_2018 = {
    "A": ("Russia", "Saudi Arabia", "Egypt", "Uruguay"),
    "B": ("Portugal", "Spain", "Morocco", "Iran"),
    "C": ("France", "Australia", "Peru", "Denmark"),
    "D": ("Argentina", "Iceland", "Croatia", "Nigeria"),
    "E": ("Brazil", "Switzerland", "Costa Rica", "Serbia"),
    "F": ("Germany", "Mexico", "Sweden", "South Korea"),
    "G": ("Belgium", "Panama", "Tunisia", "England"),
    "H": ("Poland", "Colombia", "Senegal", "Japan"),
}

def _rng(seed):
    return random.SystemRandom() if seed is None else random.Random(seed)

def _play(pairs, rng):
    """Return (home, away, winning team) for each fixture."""
    return [(a, b, rng.choice((a, b))) for a, b in pairs]

def nba_stages(seed=None):
    rng = _rng(seed)
    east = rng.sample(EAST, 8)
    west = rng.sample(WEST, 8)
    stages = [{"title": "Playoff field", "kind": "nba_field",
               "east": tuple(east), "west": tuple(west)}]
    for title in ("First round", "Conference semifinals", "Conference finals"):
        matches = []
        for label, teams in (("Eastern Conference", east), ("Western Conference", west)):
            results = _play(zip(teams[::2], teams[1::2]), rng)
            matches.extend((label, a, b, w) for a, b, w in results)
            teams[:] = [result[2] for result in results]
        stages.append({"title": title, "kind": "nba_matches", "matches": matches})
    final = _play([(east[0], west[0])], rng)
    stages.append({"title": "NBA Final", "kind": "nba_matches",
                   "matches": [("NBA Finals", *final[0])]})
    stages.append({"title": "NBA Champion", "kind": "champion", "winner": final[0][2]})
    return stages

def world_cup_stages(seed=None):
    rng = _rng(seed)
    qualifiers = {}
    groups = []
    for name, teams in WORLD_CUP_2018.items():
        order = rng.sample(teams, 4)
        qualifiers[name] = order[:2]
        groups.append((name, order))
    stages = [{"title": "2018 World Cup groups", "kind": "world_groups",
               "groups": groups}]
    # FIFA 2018 knockout bracket: A1/B2, C1/D2, E1/F2, G1/H2,
    # B1/A2, D1/C2, F1/E2, H1/G2. Adjacent winners meet.
    fixtures = [
        ("A", 0, "B", 1), ("C", 0, "D", 1),
        ("E", 0, "F", 1), ("G", 0, "H", 1),
        ("B", 0, "A", 1), ("D", 0, "C", 1),
        ("F", 0, "E", 1), ("H", 0, "G", 1),
    ]
    pairs = [(qualifiers[a][i], qualifiers[b][j]) for a, i, b, j in fixtures]
    for title in ("Round of 16", "Quarterfinals", "Semifinals", "Final"):
        matches = _play(pairs, rng)
        stages.append({"title": title, "kind": "world_matches", "matches": matches})
        winners = [winner for _, _, winner in matches]
        pairs = list(zip(winners[::2], winners[1::2]))
    stages.append({"title": "World Cup Champion", "kind": "champion",
                   "winner": winners[0]})
    return stages
