import random
import logging

from model.player import Player
from model.action import Action


class Ricky(Player):
    persona = "Ricky Raise"

    def play(self, table, player_status, is_called=False):
        if is_called:
            action = Action("MATCH", min(table.bet_amount, self.max_bet))
        elif self.bankroll > table.bet_amount:
            action = Action("RAISE", random.randint(table.bet_amount + 1, self.max_bet))
        else:
            action = Action("FOLD")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action