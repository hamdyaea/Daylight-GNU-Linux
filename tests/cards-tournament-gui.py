#!/usr/bin/env python3
"""Regression checks for the packaged graphical card and tournament games."""
import runpy,sys
from pathlib import Path
from collections import deque
root=Path(sys.argv[1])
sys.path.insert(0,str(root/'cards'))
cards=runpy.run_path(str(root/'cards/game.py'))
Card=cards['Card']; game=cards['BattleWindow']();game.withdraw()
game.game.player=deque([Card(10,'Coeur'),Card(2,'Coeur'),Card(14,'Coeur')])
game.game.computer=deque([Card(10,'Piques'),Card(3,'Piques'),Card(13,'Piques')])
used=set(game.game.player)|set(game.game.computer)
rest=[Card(rank,suit) for suit in ('Carreaux','Coeur','Piques','treffles') for rank in range(2,15) if Card(rank,suit) not in used]
game.game.player.extend(rest[:23]);game.game.computer.extend(rest[23:])
game.play_button.invoke();game.update()
assert game.play_button.cget('text')=='Continue battle'
assert all(view.cget('image') for view,_ in game.card_views)
game.play_button.invoke();game.update()
assert all(label.cget('text')=='Face down' for _,label in game.card_views)
game.play_button.invoke();game.update()
assert len(game.game.player)==29 and len(game.game.computer)==23
assert len(game.prize_images)==6
assert len(game.gallery.find_all())==12
assert game.play_button.instate(['!disabled'])
game.new_game();assert len(game.game.player)==26 and game.steps is None
game.destroy();print('PASS illustrated Battle Cards, tie/hidden/reveal, six captured images, reset')
t=runpy.run_path(str(root/'tournament/game.py'))
for seed in range(100):
 stages=t['tournament_stages'](seed)
 assert [len(v) for _,v in stages[1:5]]==[8,4,2,1]
 assert stages[-1][1]==t['simulate'](seed)[0]
 for i in range(2,5):
  previous={w for a,b,w in stages[i-1][1]}
  assert {n for a,b,w in stages[i][1] for n in (a,b)}==previous
w=t['TournamentWindow'](42);w.withdraw()
assert w.index==-1
for i in range(6):
 w.next_button.invoke();w.update();assert w.index==i
 assert w.heading.cget('text')==w.stages[i][0]
assert w.next_button.instate(['disabled'])
assert str(w.art.cget('image'))==str(w.images[1])
w.reset();assert w.index==-1 and w.next_button.instate(['!disabled'])
w.destroy();print('PASS tournament progression, 15 matches, champion artwork, reset, 100 seeds')
