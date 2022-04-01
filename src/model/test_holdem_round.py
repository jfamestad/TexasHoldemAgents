from model.holdem_round import HoldemRound
# from model.table import Table
# from model.player import Player
from players.floyd_folds import Floyd
from players.callie_calls import Callie

players = [
    Floyd("Josh", 100),
    Callie("Madi", 100),
    Floyd("Cody", 100),
    Floyd("Michelle", 100),
    Floyd("Sophia", 100),
    Floyd("Beezie", 100)
]

round = HoldemRound(
    players=players,
    blind=1
)

def test_deal():
    round.deal()
    assert round.table.flop == None
    assert round.table.turn == None
    assert round.table.river == None
    for player in players:
        assert len(player.hole) == 2

round_2 = HoldemRound(
    players=players,
    blind=1
)

def test_play():
    round_2.play()

round_3 = HoldemRound(
    players=players,
    blind=1
)

def test_play_detailed():
    round_3.deal()
    assert round_3.table.flop is None
    round_3.do_betting_round()
    round_3.expose_flop()
    assert not round_3.table.flop is None
    round_3.do_betting_round()
    assert round_3.table.turn is None
    round_3.expose_turn()
    assert not round_3.table.turn is None
    round_3.do_betting_round()
    assert round_3.table.river is None
    round_3.expose_river()
    assert not round_3.table.river is None
    round_3.do_betting_round()
    round_3.showdown()
    round_3.settle_round()

# def test_gameflow():
#     round.play()