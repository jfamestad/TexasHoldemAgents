import logging
import random

from model.player import Player
from model.action import Action


FLOYD_MESSAGES = [
    "Nope. I'm out.",
    "These cards are trash. Fold.",
    "I've got a bad feeling about this one.",
    "Not worth it. I fold.",
    "I'll wait for a better hand.",
    "Life's too short for bad cards.",
    "I know when I'm beat. Fold.",
    "Maybe next time.",
    "This hand isn't going anywhere.",
    "Discretion is the better part of valor. Fold.",
    "*sighs* Fold.",
    "I'm saving my chips for a real hand.",
]


class Floyd(Player):
    persona = "Floyd Folds"

    def play(self, table, player_status, is_called=False, round_number=None):
        action = Action("FOLD")
        self.last_message = random.choice(FLOYD_MESSAGES)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action