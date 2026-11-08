"""Non-regression tests for the restored Daylight sports games and artwork."""
import unittest
from pathlib import Path
from desktop.daylight_ui.historical_sports import (
    EAST, WEST, WORLD_CUP_2018, nba_stages, world_cup_stages
)

ROOT = Path(__file__).resolve().parents[1]


class HistoricalGamesTest(unittest.TestCase):
    def test_nba_roster(self):
        self.assertEqual(len(EAST), 15)
        self.assertEqual(len(WEST), 15)
        self.assertEqual(len(set(EAST + WEST)), 30)

    def test_nba_progression(self):
        stages = nba_stages(42)
        self.assertEqual([s["title"] for s in stages],
                         ["Playoff field", "First round", "Conference semifinals",
                          "Conference finals", "NBA Final", "NBA Champion"])
        self.assertEqual((len(stages[0]["east"]), len(stages[0]["west"])), (8, 8))
        self.assertEqual([len(s["matches"]) for s in stages[1:5]], [8, 4, 2, 1])
        for i in range(1, 5):
            for _, home, away, winner in stages[i]["matches"]:
                self.assertIn(winner, (home, away))
        self.assertEqual(stages[-1]["winner"], stages[-2]["matches"][0][3])
        self.assertEqual(nba_stages(42), stages)

    def test_world_cup_roster_and_bracket(self):
        self.assertEqual(len(WORLD_CUP_2018), 8)
        self.assertEqual(len({name for group in WORLD_CUP_2018.values()
                              for name in group}), 32)
        self.assertEqual(WORLD_CUP_2018["E"], ("Brazil", "Switzerland", "Costa Rica", "Serbia"))
        stages = world_cup_stages(42)
        self.assertEqual([s["title"] for s in stages],
                         ["2018 World Cup groups", "Round of 16", "Quarterfinals",
                          "Semifinals", "Final", "World Cup Champion"])
        self.assertEqual([len(s["matches"]) for s in stages[1:5]], [8, 4, 2, 1])
        ranking = dict(stages[0]["groups"])
        fixtures = [("A",0,"B",1),("C",0,"D",1),("E",0,"F",1),("G",0,"H",1),
                    ("B",0,"A",1),("D",0,"C",1),("F",0,"E",1),("H",0,"G",1)]
        for (g1, i1, g2, i2), (a, b, winner) in zip(fixtures, stages[1]["matches"]):
            self.assertEqual((a,b), (ranking[g1][i1], ranking[g2][i2]))
            self.assertIn(winner, (a,b))
        for stage in stages[2:5]:
            for home, away, winner in stage["matches"]:
                self.assertIn(winner, (home, away))
        self.assertEqual(stages[-1]["winner"], stages[-2]["matches"][0][2])
        self.assertEqual(world_cup_stages(42), stages)

    def test_original_coin_artwork_installed_source(self):
        from PIL import Image
        for file in ("face.png", "pile.png", "full.png"):
            path = ROOT / "desktop/game_assets/coin" / file
            self.assertTrue(path.is_file())
            with Image.open(path) as artwork:
                self.assertGreaterEqual(artwork.width, 200)
                artwork.verify()

    def test_shardturn_and_telemetry_opt_in(self):
        shell = (ROOT / "desktop/daylight_ui/shell.py").read_text()
        builder = (ROOT / "scripts/build-debs.py").read_text()
        self.assertIn('"shardturn": "Daylight Shardturn"', shell)
        self.assertIn('command=lambda:self.show("telemetry")', shell)
        self.assertIn('if not messagebox.askyesno("Boot statistics"', shell)
        self.assertRegex(builder, r'VERSION = "5\.0\.0~rc4-[0-9]+"')


if __name__ == "__main__":
    unittest.main()

    def test_sports_scrollbars_are_outside_canvas(self):
        from pathlib import Path
        source = (Path(__file__).resolve().parents[1] / "desktop/daylight_ui/games.py").read_text()
        self.assertIn("ttk.Scrollbar(self.board, orient=\"vertical\"", source)
        self.assertNotIn("ttk.Scrollbar(self.cv, orient=\"vertical\"", source)
