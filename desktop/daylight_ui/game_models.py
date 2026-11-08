"""Offline game rules, separated from drawing and input handling.

Developer: Hamdy Abou El Anein — GPL-3.0-only.
"""
from collections import deque
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import random


class ScoreLedger:
    """Small local score book. Invalid or missing fields recover independently."""
    DEFAULTS = {
        "memory": {"best": 0}, "guess": {"best": 0},
        "rpsls": {"wins": 0, "losses": 0, "draws": 0},
        "cards": {"wins": 0, "losses": 0, "draws": 0},
        "slots": {"spins": 0, "matches": 0},
    }

    def __init__(self, path=None):
        from . import state
        self.path = Path(path) if path is not None else state.directory() / "game-scores.json"

    def read(self):
        scores = {game: dict(fields) for game, fields in self.DEFAULTS.items()}
        try:
            if self.path.stat().st_size > 16384:
                return scores
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, ValueError):
            return scores
        if not isinstance(data, dict):
            return scores
        for game, fields in scores.items():
            supplied = data.get(game)
            if not isinstance(supplied, dict):
                continue
            for key in fields:
                value = supplied.get(key)
                if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 1000000000:
                    fields[key] = value
        scores["slots"]["matches"] = min(scores["slots"]["matches"], scores["slots"]["spins"])
        return scores

    def record(self, game, outcome=None, value=None):
        from . import state
        if game not in self.DEFAULTS:
            raise ValueError("This game has no recorded score.")
        if game in ("memory", "guess"):
            if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 1000000:
                raise ValueError("A completed game needs a positive integer score.")
        elif game in ("cards", "rpsls"):
            if outcome not in ("win", "loss", "draw"):
                raise ValueError("Unknown match outcome.")
        elif outcome not in ("match", "miss"):
            raise ValueError("Unknown reel outcome.")
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(self.path.with_name(".game-scores.lock"), flags, 0o600)
        with os.fdopen(descriptor, "r+") as lock:
            # Separate Daylight windows must not overwrite one another's totals.
            fcntl.flock(lock, fcntl.LOCK_EX)
            scores = self.read()
            entry = scores[game]
            if game in ("memory", "guess"):
                entry["best"] = min(entry["best"], value) if entry["best"] else value
            elif game in ("cards", "rpsls"):
                key = {"win": "wins", "loss": "losses", "draw": "draws"}[outcome]
                entry[key] = min(1000000000, entry[key]+1)
            else:
                entry["spins"] = min(1000000000, entry["spins"]+1)
                entry["matches"] = min(1000000000, entry["matches"]+int(outcome == "match"))
            state.atomic(self.path, json.dumps(scores, indent=2) + "\n")
            return scores


@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    @property
    def label(self):
        return {11: "J", 12: "Q", 13: "K", 14: "A"}.get(self.rank, str(self.rank))


class Battle:
    """Full-deck battle; every tied pair is followed by down/up cards.

    When only one card remains during a battle, it is the last face-up card.
    A player with no cards to continue forfeits the pot. If both run out on
    an equal last pair, the match ends in a draw with the pot on the table.
    Cards never disappear, including an exhausted simultaneous battle.
    """
    def __init__(self, rng=None, hands=None):
        self.rng = rng or random.SystemRandom()
        if hands is None:
            cards = [Card(rank, suit) for suit in "♣♦♥♠" for rank in range(2, 15)]
            self.rng.shuffle(cards)
            hands = (cards[:26], cards[26:])
        self.hands = [deque(hands[0]), deque(hands[1])]
        self.total = sum(map(len, self.hands))
        self.pot = []
        self.table = []
        self.last_award = []
        self.phase = "ready"
        self.winner = None
        self.pending_winner = None
        self.rounds = 0
        self.battles = 0
        self.message = "Reveal the first pair of cards."

    def card_count(self):
        return sum(map(len, self.hands)) + len(self.pot)

    def _take(self, owner, face_up):
        card = self.hands[owner].popleft()
        self.pot.append(card)
        self.table.append((owner, card, face_up))
        return card

    def _award(self, winner):
        self.pending_winner = winner
        self.phase = "collect"
        self.message = ("You win" if winner == 0 else "Computer wins") + f" {len(self.pot)} cards. Collect to continue."

    def advance(self):
        if self.phase == "finished":
            return
        if self.phase == "collect":
            self.last_award = list(self.pot)
            self.hands[self.pending_winner].extend(self.pot)
            self.pot.clear()
            if not all(self.hands):
                self.winner = self.pending_winner
                self.phase = "finished"
                self.message = "You collected the whole deck!" if self.winner == 0 else "Computer collected the whole deck."
            else:
                self.phase = "ready"
                self.message = f"Collected {len(self.last_award)} cards. Ready for the next pair."
            return
        if self.phase == "ready":
            self.table.clear()
            self.last_award.clear()
            self.rounds += 1
        if not all(self.hands):
            if not self.hands[0] and not self.hands[1]:
                self.winner = None
                self.phase = "finished"
                self.message = "A draw: both last cards are equal. The remaining cards stay on the table."
            elif self.pot:
                self._award(0 if self.hands[0] else 1)
            else:
                self.winner = 0 if self.hands[0] else 1
                self.phase = "finished"
            return
        if self.phase == "battle":
            for owner in (0, 1):
                if len(self.hands[owner]) >= 2:
                    self._take(owner, False)
        pair = [self._take(owner, True) for owner in (0, 1)]
        if pair[0].rank == pair[1].rank:
            self.phase = "battle"
            self.battles += 1
            self.message = "BATTLE! Continue: one card face down, then one face up. Last remaining cards are played face up."
        else:
            self._award(0 if pair[0].rank > pair[1].rank else 1)


@dataclass(frozen=True)
class Match:
    home: str
    away: str
    home_score: int
    away_score: int

    @property
    def winner(self):
        return self.home if self.home_score > self.away_score else self.away


class Tournament:
    def __init__(self, teams, rng=None):
        teams = [x.strip() for x in teams]
        if len(teams) < 2 or len(teams) > 64 or len(teams) & (len(teams) - 1):
            raise ValueError("Enter 2, 4, 8, 16, 32 or 64 teams.")
        if any(not t or len(t) > 40 or any(ord(c) < 32 for c in t) for t in teams):
            raise ValueError("Each team needs a name of 1–40 characters.")
        if len({t.casefold() for t in teams}) != len(teams):
            raise ValueError("Please give every team a different name.")
        self.rng = rng or random.SystemRandom()
        self.initial = list(teams)
        self.current = list(teams)
        self.rounds = []

    @property
    def champion(self):
        return self.current[0] if len(self.current) == 1 else None

    def advance(self):
        if self.champion:
            return []
        games = []
        for home, away in zip(self.current[::2], self.current[1::2]):
            a, b = self.rng.randrange(6), self.rng.randrange(6)
            if a == b:
                if self.rng.randrange(2):
                    a += 1
                else:
                    b += 1
            games.append(Match(home, away, a, b))
        self.rounds.append(games)
        self.current = [m.winner for m in games]
        return games


class Memory:
    def __init__(self, pairs=8, rng=None):
        self.deck = list(range(pairs)) * 2
        (rng or random.SystemRandom()).shuffle(self.deck)
        self.matched = set()
        self.open = []
        self.moves = 0

    def reveal(self, index):
        if not 0 <= index < len(self.deck) or index in self.matched or index in self.open or len(self.open) >= 2:
            return False
        self.open.append(index)
        if len(self.open) == 2:
            self.moves += 1
            if self.deck[self.open[0]] == self.deck[self.open[1]]:
                self.matched.update(self.open)
        return True

    def close_pair(self):
        if len(self.open) == 2:
            self.open.clear()

    @property
    def completed(self):
        return len(self.matched) == len(self.deck)


RPS_NAMES = ("Rock", "Paper", "Scissors", "Lizard", "Spock")
RPS_BEATS = ((2, 3), (0, 4), (1, 3), (1, 4), (0, 2))


def rps_result(player, computer):
    if player == computer:
        return "Draw"
    return "You win" if computer in RPS_BEATS[player] else "Computer wins"
