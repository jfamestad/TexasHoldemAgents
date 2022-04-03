from model.player import Player
from model.action import Action
import random

class Ricky(Player):
    def play(self, table):
        action = Action("RAISE", random.randint(table.bet_amount + 1, self.bankroll))
        print(f"Play - {self.name}: {action.action_type}")
        return action