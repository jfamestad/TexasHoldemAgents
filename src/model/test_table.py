from table import Table
from player import Player

players = [
    Player("Josh", 100),
    Player("Madi", 100),
    Player("Codi", 100),
    Player("Michelle", 100),
    Player("Sophia", 100),
    Player("Beezie", 100)
]

table = Table(players, 1)

def test_deal():
    table.deal()
    for player in table.players:
        assert len(player.hole) == 2
    assert table.flop == None
    assert table.turn == None
    assert table.river == None

def test_gameflow():
    table.play()