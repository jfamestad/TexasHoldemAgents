import copy

from model.holdem_round import HoldemRound
from players.floyd_folds import Floyd
from players.callie_calls import Callie
from players.robby_random import Robby
from players.ricky_raise import Ricky
from model.tournament import Tournament

players = [
    Ricky("Josh", 100),
    Robby("Cody", 100),
    Ricky("Beezie", 100),
    Callie("Madi", 100),
    # Floyd("Alice", 100),
    Robby("Michelle", 100),
    Callie("Sophia", 100),
    # Floyd("Bob", 100)
]

if __name__ == '__main__':
    winners = []
    for i in range(1000):
        new_players = [copy.deepcopy(player) for player in players]
        tournament = Tournament(
            players=new_players,
            tournament_id=i
        )
        tournament.play()
        print(tournament.winners)
        winners.append(tournament.winners)

    print("Results")
    for result in winners:
        print(f"\t{result}")

