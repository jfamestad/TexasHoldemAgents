import logging

from model.player import Player
from model.action import Action


class Stuart(Player):
    persona = "Stuart Stats"

    def play(self, table, player_status, is_called=False):
        action = Action("CALL")
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action