"""Rules and conservation checks for the visual Daylight games."""
from collections import Counter
from pathlib import Path
import os
import json
import random
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "desktop"))
from daylight_ui.game_models import Battle, Card, Memory, RPS_BEATS, ScoreLedger, Tournament, rps_result


class BattleRules(unittest.TestCase):
    def test_repeated_battle_reveals_down_up_and_awards_whole_pot(self):
        a = [Card(rank, "♣") for rank in (10, 2, 7, 3, 14, 9)]
        b = [Card(rank, "♦") for rank in (10, 4, 7, 5, 13, 8)]
        battle = Battle(hands=(a, b))
        battle.advance()
        self.assertEqual(battle.phase, "battle")
        self.assertEqual(len(battle.pot), 2)
        battle.advance()
        self.assertEqual(battle.phase, "battle")
        self.assertEqual([up for owner, card, up in battle.table], [True, True, False, False, True, True])
        battle.advance()
        self.assertEqual(battle.phase, "collect")
        self.assertEqual(battle.pending_winner, 0)
        self.assertEqual(len(battle.pot), 10)
        self.assertEqual(battle.battles, 2)
        battle.advance()
        self.assertEqual([len(hand) for hand in battle.hands], [11, 1])
        self.assertEqual(len(battle.last_award), 10)
        self.assertEqual(battle.card_count(), 12)

    def test_ace_beats_king_and_suits_do_not_break_equal_rank(self):
        battle = Battle(hands=([Card(14, "♣")], [Card(13, "♥")]))
        battle.advance()
        self.assertEqual(battle.pending_winner, 0)
        battle.advance()
        self.assertEqual(battle.phase, "finished")
        self.assertEqual(battle.winner, 0)
        self.assertEqual(len(battle.hands[0]), 2)

    def test_one_card_left_is_last_faceup(self):
        battle = Battle(hands=([Card(10, "♣"), Card(14, "♣")],
                              [Card(10, "♦"), Card(2, "♦"), Card(13, "♦")]))
        battle.advance()
        battle.advance()
        self.assertEqual(battle.pending_winner, 0)
        self.assertEqual(len(battle.pot), 5)
        self.assertEqual([(owner, up) for owner, card, up in battle.table],
                         [(0, True), (1, True), (1, False), (0, True), (1, True)])
        battle.advance()
        self.assertEqual(battle.winner, 0)
        self.assertEqual(battle.card_count(), 5)

    def test_exhausted_player_forfeits_battle(self):
        battle = Battle(hands=([Card(10, "♣")], [Card(10, "♦"), Card(2, "♦")]))
        battle.advance()
        battle.advance()
        self.assertEqual(battle.pending_winner, 1)
        battle.advance()
        self.assertEqual(battle.winner, 1)
        self.assertEqual(battle.card_count(), 3)

    def test_simultaneous_exhausted_tie_is_draw_and_keeps_pot(self):
        battle = Battle(hands=([Card(10, "♣")], [Card(10, "♦")]))
        battle.advance()
        battle.advance()
        self.assertEqual(battle.phase, "finished")
        self.assertIsNone(battle.winner)
        self.assertEqual(len(battle.pot), 2)
        self.assertEqual(battle.card_count(), 2)

    def test_full_deck_and_long_seeded_play_conserve_each_card(self):
        expected = Counter(Card(rank, suit) for suit in "♣♦♥♠" for rank in range(2, 15))
        for seed in range(12):
            battle = Battle(random.Random(seed))
            for _ in range(2000):
                battle.advance()
                self.assertEqual(battle.card_count(), 52)
                actual = Counter(list(battle.hands[0])+list(battle.hands[1])+battle.pot)
                self.assertEqual(actual, expected)
                if battle.phase == "finished":
                    break


class TournamentRules(unittest.TestCase):
    def test_complete_cup_history_and_winners_are_consistent(self):
        teams = ["Team "+str(i) for i in range(16)]
        cup = Tournament(teams, random.Random(7))
        previous = teams
        while not cup.champion:
            matches = cup.advance()
            self.assertEqual([(m.home, m.away) for m in matches], list(zip(previous[::2], previous[1::2])))
            self.assertTrue(all(m.home_score != m.away_score for m in matches))
            previous = [m.winner for m in matches]
        self.assertEqual([len(r) for r in cup.rounds], [8, 4, 2, 1])
        self.assertIn(cup.champion, teams)
        self.assertEqual(cup.advance(), [])

    def test_invalid_sizes_names_and_duplicates(self):
        for teams in [[], ["A"], ["A", "B", "C"], ["a", "A"], ["", "B"], ["x"*41, "B"]]:
            with self.assertRaises(ValueError):
                Tournament(teams)
        with self.assertRaises(ValueError):
            Tournament(["A\x00B", "C"])
        self.assertEqual(Tournament([" A ", " B\n"]).initial, ["A", "B"])


class MemoryRules(unittest.TestCase):
    def test_mismatches_stay_visible_until_closed(self):
        memory = Memory(4, random.Random(1))
        a = 0
        b = next(i for i, value in enumerate(memory.deck) if value != memory.deck[a])
        self.assertTrue(memory.reveal(a))
        self.assertFalse(memory.reveal(a))
        self.assertTrue(memory.reveal(b))
        self.assertEqual(memory.moves, 1)
        self.assertFalse(memory.matched)
        self.assertFalse(memory.reveal(7))
        memory.close_pair()
        self.assertEqual(memory.open, [])

    def test_all_pairs_solve_exactly_once(self):
        memory = Memory(8, random.Random(8))
        for value in range(8):
            for i in [i for i, v in enumerate(memory.deck) if v == value]:
                self.assertTrue(memory.reveal(i))
            memory.close_pair()
        self.assertTrue(memory.completed)
        self.assertEqual(memory.moves, 8)
        self.assertFalse(memory.reveal(0))


class RpsRules(unittest.TestCase):
    def test_each_choice_beats_two_and_loses_to_two(self):
        for a in range(5):
            results = Counter(rps_result(a, b) for b in range(5))
            self.assertEqual(results, {"Draw": 1, "You win": 2, "Computer wins": 2})
            for b in RPS_BEATS[a]:
                self.assertNotIn(a, RPS_BEATS[b])


class LocalScores(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "daylight" / "game-scores.json"
        self.ledger = ScoreLedger(self.path)

    def test_scores_survive_reopening_and_keep_the_best_completed_score(self):
        for moves in (12, 15, 9):
            self.ledger.record("memory", value=moves)
        self.ledger.record("guess", value=3)
        self.ledger.record("guess", value=5)
        self.ledger.record("rpsls", "win")
        self.ledger.record("rpsls", "loss")
        self.ledger.record("cards", "draw")
        self.ledger.record("slots", "match")
        self.ledger.record("slots", "miss")
        values = ScoreLedger(self.path).read()
        self.assertEqual(values["memory"]["best"], 9)
        self.assertEqual(values["guess"]["best"], 3)
        self.assertEqual(values["rpsls"], {"wins": 1, "losses": 1, "draws": 0})
        self.assertEqual(values["cards"]["draws"], 1)
        self.assertEqual(values["slots"], {"spins": 2, "matches": 1})
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_corruption_recovers_individual_fields_and_next_write(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"memory": {"best": True}, "guess": {"best": -1},
                                         "cards": {"wins": 7, "losses": "oops"},
                                         "slots": {"spins": 2, "matches": 900}}))
        data = self.ledger.read()
        self.assertEqual(data["memory"]["best"], 0)
        self.assertEqual(data["guess"]["best"], 0)
        self.assertEqual(data["cards"], {"wins": 7, "losses": 0, "draws": 0})
        self.assertEqual(data["slots"], {"spins": 2, "matches": 2})
        self.path.write_text("truncated {")
        self.assertEqual(self.ledger.read(), ScoreLedger.DEFAULTS)
        self.ledger.record("cards", "win")
        self.assertEqual(json.loads(self.path.read_text())["cards"]["wins"], 1)
        self.path.write_text(" "*17000)
        self.assertEqual(self.ledger.read(), ScoreLedger.DEFAULTS)

    def test_invalid_events_do_not_create_a_score_file(self):
        for game, outcome, value in [("dice", "win", None), ("memory", None, 0),
                                     ("guess", None, True), ("cards", "maybe", None),
                                     ("slots", "money", None)]:
            with self.assertRaises(ValueError):
                self.ledger.record(game, outcome, value)
        self.assertFalse(self.path.exists())

    def test_separate_windows_and_parallel_updates_do_not_lose_totals(self):
        from concurrent.futures import ThreadPoolExecutor
        self.ledger.record("rpsls", "win")
        second_window = ScoreLedger(self.path)
        self.ledger.record("cards", "win")
        second_window.record("rpsls", "draw")
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(lambda _: ScoreLedger(self.path).record("rpsls", "win"), range(20)))
        data = self.ledger.read()
        self.assertEqual(data["rpsls"], {"wins": 21, "losses": 0, "draws": 1})
        self.assertEqual(data["cards"]["wins"], 1)

    def test_default_path_honors_the_user_config_directory(self):
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": self.temporary.name}):
            self.assertEqual(ScoreLedger().path, self.path)


@unittest.skipUnless(os.environ.get("DISPLAY"), "Native game drawing needs X/Xvfb")
class NativeGamePages(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        patch = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temporary.name})
        patch.start()
        self.addCleanup(patch.stop)

    def test_every_game_draws_and_responds_to_its_main_action(self):
        import tkinter as tk
        from daylight_ui.games import PAGE_NAMES, build
        root = tk.Tk()
        root.geometry("1050x780")
        errors = []
        root.report_callback_exception = lambda *args: errors.append(args)
        actions = {
            "dice": lambda p: p.roll_dice(), "coin": lambda p: p.flip_coin(),
            "lottery": lambda p: p.draw_lottery_values(), "rpsls": lambda p: p.play_rps(4),
            "cards": lambda p: p.advance_battle(), "tournament": lambda p: p.advance_tournament(),
            "basketball": lambda p: p.play_quarter(), "memory": lambda p: p.reveal_memory(0),
            "slots": lambda p: p.spin(), "guess": lambda p: p.make_guess(),
        }
        try:
            for name in PAGE_NAMES:
                with self.subTest(game=name):
                    page = build(root, name)
                    root.update()
                    actions[name](page)
                    root.update()
                    self.assertGreater(len(page.cv.find_all()), 2)
                    self.assertFalse(errors, errors)
                    page.destroy()
                    root.update()
        finally:
            root.destroy()

    def test_memory_cards_accept_mouse_and_keyboard_after_resize(self):
        import tkinter as tk
        from daylight_ui.games import build
        root = tk.Tk()
        root.geometry("800x600")
        try:
            page = build(root, "memory")
            root.update()
            bounds = page.cv.bbox("memory-0")
            page.cv.event_generate("<Button-1>", x=(bounds[0]+bounds[2])//2,
                                   y=(bounds[1]+bounds[3])//2)
            root.update()
            self.assertEqual(page.memory.open, [0])
            page.new_memory()
            page.cv.focus_force()
            root.update()
            page.cv.event_generate("<Right>")
            page.cv.event_generate("<Return>")
            root.update()
            self.assertEqual(page.memory.open, [1])
            self.assertEqual(page.memory_focus, 1)
        finally:
            root.destroy()

    def test_only_completed_games_update_local_records_once(self):
        import tkinter as tk
        from daylight_ui.games import build
        root = tk.Tk()
        try:
            page = build(root, "memory")
            page.reveal_memory(0)
            page.destroy()
            self.assertEqual(ScoreLedger().read()["memory"]["best"], 0)
            page = build(root, "memory")
            for picture in range(8):
                pair = [i for i, value in enumerate(page.memory.deck) if value == picture]
                for index in pair:
                    page.reveal_memory(index)
                page.memory.close_pair()
            page.reveal_memory(0)
            self.assertEqual(ScoreLedger().read()["memory"]["best"], 8)
            page.destroy()
            page = build(root, "guess")
            page.guess_value.set(str(page.target))
            page.make_guess()
            page.make_guess()
            self.assertEqual(ScoreLedger().read()["guess"]["best"], 1)
            page.destroy()
            page = build(root, "cards")
            page.battle = Battle(hands=([Card(14, "♣")], [Card(13, "♥")]))
            page.advance_battle()
            self.assertEqual(ScoreLedger().read()["cards"]["wins"], 0)
            page.advance_battle()
            page.advance_battle()
            self.assertEqual(ScoreLedger().read()["cards"]["wins"], 1)
            page.destroy()
            page = build(root, "slots")
            page.spin()
            page.destroy()
            self.assertEqual(ScoreLedger().read()["slots"]["spins"], 0)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
