import random
import logging

from model.player import Player
from model.action import Action


ROBBY_CALL_MESSAGES = [
    "Eeny, meeny, miny... call!",
    "My gut says call. Or was it lunch?",
    "I flipped a mental coin. Call!",
    "Why not? Call.",
    "Randomly feeling lucky. Call.",
]

ROBBY_FOLD_MESSAGES = [
    "The dice in my head said fold.",
    "Random says no. Fold!",
    "Not feeling it. Or am I? Nope, fold.",
    "My chaos brain says out.",
    "Folding... for completely arbitrary reasons.",
]

ROBBY_RAISE_MESSAGES = [
    "Chaos reigns! Raise!",
    "Let's make things interesting. Random raise!",
    "I have no idea what I'm doing. RAISE!",
    "The universe told me to raise. Or was that the pizza?",
    "Spinning the wheel of fortune... RAISE!",
    "Pure random energy! Raise!",
]


class Robby(Player):
    persona = "Robbie Random"

    def play(self, table, player_status, is_called=False, round_number=None):
        random_value = random.random()
        if is_called:
            if self.max_bet > table.bet_amount:
                if random_value > .5:
                    action = Action("MATCH", table.bet_amount)
                    self.last_message = random.choice(ROBBY_CALL_MESSAGES)
                else:
                    action = Action("FOLD")
                    self.last_message = random.choice(ROBBY_FOLD_MESSAGES)
            else:
                if random_value > .5:
                    action = Action("MATCH", self.max_bet, all_in=True)
                    self.last_message = random.choice(ROBBY_RAISE_MESSAGES)
                else:
                    action = Action("FOLD")
                    self.last_message = random.choice(ROBBY_FOLD_MESSAGES)
        elif random_value < .33:
            action = Action("CALL", min(table.bet_amount, self.max_bet))
            self.last_message = random.choice(ROBBY_CALL_MESSAGES)
        elif random_value < .67:
            action = Action("FOLD")
            self.last_message = random.choice(ROBBY_FOLD_MESSAGES)
        else:
            logging.debug(f"{self.name} wants to raise. Current Bet is {table.bet_amount}, {self.name} has {self.bankroll}")
            if self.max_bet > table.bet_amount:
                action = Action("RAISE", random.randint(table.bet_amount + 1, self.max_bet))
                self.last_message = random.choice(ROBBY_RAISE_MESSAGES)
            else:
                logging.debug(f"<> {self.name} is all in <>")
                action = Action("CALL", self.max_bet, all_in=True)
                self.last_message = random.choice(ROBBY_RAISE_MESSAGES)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action