from model.player import Player
from model.action import Action
import random


class Ricky(Player):
    def play(self, table, is_called=False):
        if is_called:
            action = Action("MATCH", min(table.bet_amount, self.max_bet))
        elif self.bankroll > table.bet_amount:
            action = Action("RAISE", random.randint(table.bet_amount + 1, self.max_bet))
        else:
            action = Action("FOLD")
        print(f"Play - {self.name}: {action.action_type}")
        return action