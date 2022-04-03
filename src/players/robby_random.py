from model.player import Player
from model.action import Action
import random

class Robby(Player):
    def play(self, table):
        random_value = random.random()
        if random_value < .33:
            action = Action("CALL", table.bet_amount)
        elif random_value < .67:
            action = Action("FOLD")
        else:
            action = Action("RAISE", random.randint(table.bet_amount, self.bankroll))
        print(f"Play - {self.name}: {action.action_type}")
        return action