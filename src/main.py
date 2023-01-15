import copy
import logging

from model.holdem_round import HoldemRound
from players.floyd_folds import Floyd
from players.callie_calls import Callie
from players.robby_random import Robby
from players.ricky_raise import Ricky
from players.herbie_human import Herbie
from model.tournament import Tournament

players = [
    Ricky("Alice", 100),
    Robby("Cody", 100),
    Ricky("Beezie", 100),
    Callie("Madi", 100),
    Herbie("Josh", 100),
    Robby("Michelle", 100),
    Callie("Sophia", 100),
    # Floyd("Bob", 100)
]

if __name__ == '__main__':
    winners = []
    for i in range(1):
        new_players = [copy.deepcopy(player) for player in players]
        tournament = Tournament(
            players=new_players,
            tournament_id=i
        )
        tournament.play()
        logging.info(tournament.winners)
        winners.append(tournament.winners)

    logging.info("Results")
    for result in winners:
        logging.info(f"\t{result}")

