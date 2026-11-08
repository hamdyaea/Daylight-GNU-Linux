"""Original Daylight NBA and 2018 World Cup competition formats.
Copyright (C) 2026 Hamdy Abou El Anein. SPDX-License-Identifier: GPL-3.0-only
"""
import random

NBA = {'Eastern Conference': ['Boston Celtics', 'Toronto Raptors', 'Cleveland Cavaliers', 'Indiana Pacers', 'Detroit Pistons', 'Milwaukee Bucks', 'Washington Wizards', 'New York Knicks', 'Miami Heat', 'Philadelphia 76ers', 'Brooklyn Nets', 'Charlotte Hornets', 'Orlando Magic', 'Chicago Bulls', 'Atlanta Hawks'], 'Western Conference': ['Houston Rockets', 'Golden State Warriors', 'San Antonio Spurs', 'Minnesota Timberwolves', 'Oklahoma City Thunder', 'Denver Nuggets', 'Portland Trail Blazers', 'New Orleans Pelicans', 'Utah Jazz', 'Los Angeles Clippers', 'Los Angeles Lakers', 'Sacramento Kings', 'Phoenix Suns', 'Memphis Grizzlies', 'Dallas Mavericks']}
WORLD_CUP_2018 = {'A': ['Russia', 'Saudi Arabia', 'Egypt', 'Uruguay'], 'B': ['Portugal', 'Spain', 'Morocco', 'Iran'], 'C': ['France', 'Australia', 'Peru', 'Denmark'], 'D': ['Argentina', 'Iceland', 'Croatia', 'Nigeria'], 'E': ['Brazil', 'Switzerland', 'Costa Rica', 'Serbia'], 'F': ['Germany', 'Mexico', 'Sweden', 'South Korea'], 'G': ['Belgium', 'Panama', 'Tunisia', 'England'], 'H': ['Poland', 'Colombia', 'Senegal', 'Japan']}

class Competition:
    def __init__(self, sport, rng=None):
        if sport not in ("nba", "worldcup"):
            raise ValueError("Unknown competition")
        self.sport = sport
        self.rng = rng or random.SystemRandom()
        self.groups = {key: list(value) for key, value in
                       (NBA if sport == "nba" else WORLD_CUP_2018).items()}
        self.stage = "Teams" if sport == "nba" else "Groups · World Cup 2018"
        self.matches = {}
        self.history = []
        self.champion = None
        self.qualified = False

    def advance(self):
        if self.champion:
            return
        if not self.qualified:
            ranked = {key: self.rng.sample(value, len(value))
                      for key, value in self.groups.items()}
            if self.sport == "nba":
                self.groups = {key: value[:8] for key, value in ranked.items()}
                order = (0, 7, 3, 4, 2, 5, 1, 6)
                self.matches = {key: [(value[order[i]], value[order[i+1]])
                                     for i in range(0, 8, 2)]
                                for key, value in self.groups.items()}
                self.stage = "Conference first round · Top 8"
            else:
                self.groups = ranked
                order = (("A","B"), ("C","D"), ("E","F"), ("G","H"),
                         ("B","A"), ("D","C"), ("F","E"), ("H","G"))
                self.matches = {"World Cup": [(ranked[a][0], ranked[b][1]) for a,b in order]}
                self.stage = "Round of 16"
            self.qualified = True
            return
        results = {key: [(a, b, self.rng.choice((a, b))) for a,b in matches]
                   for key,matches in self.matches.items()}
        self.history.append((self.stage, results))
        winners = {key: [winner for a,b,winner in games] for key,games in results.items()}
        if self.sport == "nba" and len(winners) == 2 and all(len(v)==1 for v in winners.values()):
            self.matches = {"NBA Finals": [(winners["Eastern Conference"][0], winners["Western Conference"][0])]}
            self.stage = "NBA Finals"
        elif len(winners) == 1 and len(next(iter(winners.values()))) == 1:
            self.champion = next(iter(winners.values()))[0]
            self.matches = {}
            self.stage = "NBA champion" if self.sport == "nba" else "World Cup champion"
        else:
            self.matches = {key: list(zip(value[::2], value[1::2])) for key,value in winners.items()}
            count = sum(map(len, self.matches.values()))
            self.stage = (("Conference semifinals" if count == 4 else "Conference finals")
                          if self.sport == "nba" else
                          {4:"Quarterfinals", 2:"Semifinals", 1:"Final"}[count])
