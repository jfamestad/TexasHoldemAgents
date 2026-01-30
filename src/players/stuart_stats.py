import logging
import random

from model.player import Player
from model.action import Action


STUART_CALL_MESSAGES = [
    "The expected value suggests a call.",
    "Statistically speaking, I should stay in.",
    "Running the numbers... call.",
    "My model says this is +EV. Call.",
    "The variance is acceptable. Calling.",
    "Pot odds look favorable.",
    "According to my calculations... call.",
]

STUART_ALL_IN_MESSAGES = [
    "The math leaves me no choice. All in.",
    "Statistically, this is my only option.",
    "When the numbers say go, you go all in.",
    "My bankroll analysis is complete. All in.",
]


class Stuart(Player):
    persona = "Stuart Stats"

    def play(self, table, player_status, is_called=False, round_number=None):

        print(f"Table: {table}")
        print(f"Player status: {player_status}")
        print(f"Called?: {is_called}")

        logging.debug(f"{self.name} sees the bet is at: {table.bet_amount}")
        if self.max_bet > table.bet_amount:
            action = Action("CALL", table.bet_amount)
            self.last_message = random.choice(STUART_CALL_MESSAGES)
        else:
            logging.debug(f"{self.name} is all in")
            logging.debug(
                f"{self.name} has {self.bankroll} in the bank and {self.status.money_on_table} on the table")
            action = Action("CALL", self.max_bet, all_in=True)
            self.last_message = random.choice(STUART_ALL_IN_MESSAGES)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action
