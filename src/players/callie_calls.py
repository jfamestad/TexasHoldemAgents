from model.player import Player
from model.action import Action

class Callie(Player):
    def play(self, table):
        action = Action("CALL", table.bet_amount)
        print(f"Play - {self.name}: {action.action_type}")
        return action