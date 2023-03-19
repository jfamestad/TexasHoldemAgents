import random
import logging

from model.player import Player
from model.action import Action


class Ricky(Player):
    persona = "Ricky Raise"

    def __init__(self, name, bankroll, raise_limit=3):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit

    def start_betting_round(self):
        super().start_betting_round()
        self.raise_count = 0

    def play(self, table, player_status, is_called=False):
        if is_called:
            action = Action("MATCH", min(table.bet_amount, self.max_bet))
        elif self.bankroll > table.bet_amount and self.raise_count < self.raise_limit:
            max_raise = min(self.bankroll, self.max_bet)
            min_raise = table.bet_amount + 1
            action = Action("RAISE", random.randint(min_raise, max_raise))
            self.raise_count += 1
        else:
            action = Action("FOLD")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action

