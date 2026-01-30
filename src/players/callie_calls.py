import logging
import random

from model.player import Player
from model.action import Action


CALLIE_MESSAGES = [
    "I'm in. I'm always in.",
    "Call! That's what I do.",
    "You know I'm calling this.",
    "Folding is for quitters.",
    "I didn't come here to fold.",
    "Sure, I'll see that bet.",
    "Call. Obviously.",
    "I believe in staying positive. And staying in.",
    "Why would I fold? The fun is in playing!",
    "I trust my cards. Call.",
]

CALLIE_ALL_IN_MESSAGES = [
    "All in! Let's see what happens!",
    "Everything I've got. No regrets!",
    "This is it! All in!",
    "Go big or go home, right?",
]


class Callie(Player):
    persona = "Callie Calls"

    def __init__(self, name, bankroll, raise_limit=3):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit

    def play(self, table, player_status, is_called=False, round_number=None):
        logging.debug(f"{self.name} sees the bet is at: {table.bet_amount}")
        if self.max_bet > table.bet_amount:
            action = Action("CALL", table.bet_amount)
            self.last_message = random.choice(CALLIE_MESSAGES)
        else:
            logging.debug(f"{self.name} is all in")
            logging.debug(f"{self.name} has {self.bankroll} in the bank and {self.status.money_on_table} on the table")
            action = Action("CALL", self.max_bet, all_in=True)
            self.last_message = random.choice(CALLIE_ALL_IN_MESSAGES)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action