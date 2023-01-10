from model.player import Player
from model.action import Action

class Stuart(Player):
    def play(self, table, is_called=False):
        action = Action("CALL")
        print(f"Play - {self.name}: {action.action_type}")
        return action