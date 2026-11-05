#!/usr/bin/env python3
# Developer: Hamdy Abou El Anein <info@daylightlinux.ch>
"""Exercise the six Tk games under an isolated graphical display."""
import argparse
import runpy
import time
import tkinter as tk
from pathlib import Path
from unittest.mock import patch


def children(widget):
    for child in widget.winfo_children():
        yield child
        yield from children(child)


def button(root, label):
    return next(w for w in children(root) if w.winfo_class() in ("Button", "TButton")
                and w.cget("text") == label)


def pump(root, seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        root.update()
        time.sleep(.01)


def check(games):
    def load(name):
        return runpy.run_path(str(games / name / "game.py"))

    module = load("dice")
    root = module["DiceApp"]()
    for value in (1, 2, 3, 4, 5, 6, 5):
        with patch("secrets.randbelow", return_value=value - 1):
            button(root, "Roll again").invoke()
        assert root.result.get() == str(value)
        assert str(root.face.cget("image")) == str(root.faces[value])
    root.destroy()

    root = load("coin")["CoinApp"]()
    for index, name in enumerate(("Heads", "Tails")):
        with patch("secrets.randbelow", return_value=index):
            button(root, "Flip coin").invoke()
        assert str(root.coin.cget("image")) == str(root.faces[name])
    assert root.count == 2 and root.heads == 1
    root.destroy()

    module = load("rpsls")
    root = tk.Tk()
    game = module["Game"](root)
    for player in module["CHOICES"]:
        for computer in module["CHOICES"]:
            with patch("secrets.choice", return_value=computer):
                button(root, player).invoke()
            assert tuple(game.player_card.cget("image")) == (str(game.images[player]),)
            assert tuple(game.computer_card.cget("image")) == (str(game.images[computer]),)
            assert module["outcome"](player, computer)[1] in game.result.get()
    assert game.player_score == game.computer_score == 10
    root.destroy()

    module = load("memory")
    with patch.object(tk.Tk, "mainloop", lambda self: None), patch.object(
        module["secrets"].SystemRandom, "shuffle", lambda self, deck: None
    ):
        module["main"]()
    root = tk._default_root
    cards = [w for w in children(root) if w.winfo_class() == "TButton" and w.cget("image")]
    assert len(cards) == 6
    backs = [w.cget("image") for w in cards]
    cards[0].invoke()
    assert cards[0].cget("image") != backs[0]
    cards[1].invoke()
    cards[2].invoke()
    assert cards[2].cget("image") == backs[2]
    pump(root, 1)
    assert [w.cget("image") for w in cards] == backs
    for i in range(3):
        cards[i].invoke()
        cards[i + 3].invoke()
        assert cards[i].cget("image") == cards[i + 3].cget("image")
    assert any("All pairs found!" in str(w.cget("text")) for w in children(root)
               if w.winfo_class() == "TLabel")
    button(root, "New game").invoke()
    assert [w.cget("image") for w in cards] == backs
    root.destroy()

    module = load("slots")
    root = tk.Tk()
    game = module["ClassicSlots"](root)
    for result, balance in [(("BAR", "BAR", "BAR"), 400),
                            (("SEVEN", "CHERRY", "SEVEN"), 600),
                            (("CHERRY", "SEVEN", "BAR"), 0)]:
        picks = iter(result)
        with patch("shutil.which", return_value=None), patch(
            "secrets.choice", side_effect=lambda seq: next(picks, "BAR")
        ):
            game.spin_button.invoke()
            pump(root, 1)
        assert game.winnings == balance
        assert [tuple(w.cget("image")) for w in game.reels] == [(str(game.faces[x]),) for x in result]
    assert game.staked == 300
    root.destroy()

    module = load("basketball")
    root = tk.Tk()
    game = module["Playoffs"](root, seed=11)
    for index, (stage, _, lines) in enumerate(module["championship"](11)):
        if index:
            game.next.invoke()
        assert game.heading.cget("text") == stage
        assert game.body.get("1.0", "end-1c").splitlines() == "\n".join(lines).splitlines()
    assert game.body.get("1.0", "end-1c") == module["simulate"](11)[0]
    game.next.invoke()
    assert game.heading.cget("text") == "Playoff field"
    root.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("games", type=Path, nargs="?", default=Path(__file__).resolve().parents[1] / "games")
    check(parser.parse_args().games.resolve())
    print("PASS: six graphical games, full rounds, matching images and replay.")
