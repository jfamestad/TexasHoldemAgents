import copy
import logging

from model.holdem_round import HoldemRound
from players.floyd_folds import Floyd
from players.callie_calls import Callie
from players.robby_random import Robby
from players.ricky_raise import Ricky
from players.herbie_human import Herbie
from players.stuart_stats import Stuart
from players.paula_pairs import Paula
from players.johnny_jacks import Johnny
from players.chad_gpt import Chad
from players.claude import Claude
from model.tournament import Tournament

players = [
    Ricky("Alice", 100),
    Robby("Cody", 100),
    Chad("Chad", 100, temperature=.75),
    Claude("Claude", 100),
    Callie("Baxter", 100),
    # Ricky("Julio", 100),
    # Robby("Michelle", 100),
    # Johnny("Johnny", 100),
    # Callie("Sophia", 100),
    # Stuart("Alice", 100),
    Paula("Paula", 100),
    Johnny("Beezie", 100),
    # Johnny("Madi", 100),
    # Herbie("Josh", 100),
    Robby("Michelle", 100),
    # Johnny("Johnny", 100),
    Callie("Sophia", 100),
    # Floyd("Bob", 100)
]

if __name__ == '__main__':
    winners = []
    for i in range(20):
        # try:
            print(f"Starting round {i}")
            new_players = [copy.deepcopy(player) for player in players]
            tournament = Tournament(
                players=new_players,
                tournament_id=i
            )
            tournament.play()
            logging.info(tournament.winners)
            winners.append(tournament.winners)
        # except Exception as e:
        #     print(f"Error: {e}")
        #     print(e)
        #     print("Too many bad responses...")

    logging.info("Results")
    for result in winners:
        logging.info(f"\t{result}")

