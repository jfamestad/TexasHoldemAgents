import logging
from model.player import Player
from model.action import Action


class Floyd(Player):
    persona = "Floyd Folds"

    def play(self, table, player_status, is_called=False):
        action = Action("FOLD")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action