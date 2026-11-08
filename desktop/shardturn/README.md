# SHARDTURN

![Shardturn — The Color Card Duel](assets/shardturn-logo.svg)

**THE COLOR CARD DUEL**

A Python card game for playing against the computer, with an English interface and original vector artwork. The visual design combines warm ivory, graphite and geometric cards: Coral circles, Amber diamonds, Jade triangles and Iris squares. The card backs carry a lattice of facets and the Shardturn emblem.

The computer's cards stay hidden throughout the game. Shardturn works offline using Python's standard library. No account, external service or image download is required.

**Developer: Hamdy Abou El Anein**  
**Contact: [info@daylightlinux.ch](mailto:info@daylightlinux.ch)**

Read the [visual identity guide](VISUAL_IDENTITY.md), browse the [vector assets](assets/), or view the [game screenshot](screenshot.png).

## Getting started

You need **Python 3.9 or newer with Tkinter**.

Clone the repository and launch the standalone edition:

```bash
git clone https://github.com/hamdyaea/Shardturn.git
cd Shardturn
python3 Shardturn.py
```

If you downloaded the project instead, extract it and run `python3 Shardturn.py` from its folder.

On Windows:

```powershell
py -3 Shardturn.py
```

The `play.sh` and `play.bat` launchers run the same standalone file. On macOS, use `python3 Shardturn.py`; Python.org installers include a Tkinter option.

If Tkinter is missing on Linux:

```bash
# Manjaro / Arch Linux
sudo pacman -S python tk

# Debian / Ubuntu / Raspberry Pi OS
sudo apt install python3 python3-tk
```

For the separate-source edition, keep `shardturn.py` and `shardturn_engine.py` in the same folder and run `python3 shardturn.py`. The `build_standalone.py` script rebuilds the standalone edition.

## How to play

Play a card that matches the discard pile's active color, number or symbol, or play a Wild. Playable cards are highlighted. Each color also has a distinctive shape. A Wild opens the color picker.

You may draw even if you already hold a playable card. After drawing, you may play only the card you just drew, or keep it and pass. Use the arrows to browse a large hand.

When you have two cards, activate **LAST CARD!** before playing to prepare your announcement. If you forget, you can still announce your last card before the opponent starts acting. Being caught in time adds a two-card penalty. Watch for the computer forgetting its own announcement, too.

| Control | Action |
| --- | --- |
| Click a card | Play that card |
| `D` | Draw a card |
| `Space` | Draw, or keep the drawn card and pass |
| `L` | Prepare or make the “LAST CARD!” announcement |
| `C` | Catch the computer's missing announcement |
| `←` / `→` | Browse the previous / next page of your hand |
| `1`–`9`, then `0` | Play the 1st–10th card on the current page |
| `H` | Open the rules and help |
| `N` | Request a new game |

Use the **CHALLENGE THE +4** button to challenge a Wild Draw Four. Choose colors and confirm dialogs with the mouse.

## Rules

- **108 cards**, with seven cards dealt to each player.
- In a two-player game, **Pause** and **Reverse** let their player take another turn. A **+2** or **+4** makes the opponent draw and skip their turn.
- **+2/+4 penalties do not stack.** Play one card at a time.
- A **+4** is legal only if its player has no card matching the active color before playing it. A matching number or symbol in another color does not prevent a +4.
- You can bluff with a +4. A successful challenge makes its player draw four cards; a failed challenge makes the challenger draw six and lose their turn.
- An opening action card applies its effect. An opening +4 is shuffled back into the deck.
- When the draw pile runs out, the discard pile is shuffled while its top card stays in place.
- The first player to empty their hand wins the round. A final +2/+4 applies its penalty before scoring.
- The round winner scores the cards left in the opponent's hand: number cards at face value, colored action cards at 20 points, and Wilds at 50 points. The first player to **500 points** wins the game.

The initial dealer is chosen at random, then alternates between rounds. A +4 challenge is checked automatically without revealing the hand, so the computer's cards always stay hidden. Its ordinary decisions do not inspect your hand.

Scores are kept in memory for the current session. Closing the game resets them.

## Development and checks

The tests cover game rules, interface interactions, announcements, challenges and computer decisions. Seeded simulations check card conservation and prevent the computer player from inspecting hidden cards.

```bash
python3 -m unittest discover -s tests -v
```

Graphical tests require a desktop session or Xvfb. Engine and computer-player tests run without opening a window.

## License and references

Copyright (C) 2026 Hamdy Abou El Anein.

Shardturn's source code and original vector assets are free software under the **GNU General Public License, version 3 or (at your option) any later version** (`GPL-3.0-or-later`). See the complete license in [LICENSE](LICENSE).

This software is provided without warranty; see the license for details.

Shardturn is an independent project and is not affiliated with Mattel. Its name, cards and interface use their own visual identity.

Documentation used as a reference for the classic mechanics: [Mattel UNO W2085 instructions](https://service.mattel.com/instruction_sheets/W2085-Eng.pdf) and [Mattel two-player rules](https://service.mattel.com/instruction_sheets/42001pr.pdf).
