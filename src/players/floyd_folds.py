from model.player import Player
from model.action import Action

class Floyd(Player):
    def play(self, table, is_called=False):
        action = Action("FOLD")
        print(f"Play - {self.name}: {action.action_type}")
        return action