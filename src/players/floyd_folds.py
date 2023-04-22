import logging
from model.player import Player
from model.action import Action


class Floyd(Player):
    persona = "Floyd Folds"

    def play(self, table, player_status, is_called=False, round_number=None):
        action = Action("FOLD")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action