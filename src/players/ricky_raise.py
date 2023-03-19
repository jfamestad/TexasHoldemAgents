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
            min_raise = table.bet_amount + 1
            if min_raise >= self.max_bet:
                bet_amount = self.max_bet
            else:
                bet_amount = random.randint(min_raise, self.max_bet)
            action = self._raise(table, bet_amount)
            self.raise_count += 1
        else:
            action = Action("FOLD")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action

