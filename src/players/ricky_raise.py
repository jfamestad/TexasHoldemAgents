from model.player import Player
from model.action import Action

class Ricky(Player):
    def play(self, table):
        action = Action("CALL")
        print(f"Play - {self.name}: {action.action_type}")
        return action