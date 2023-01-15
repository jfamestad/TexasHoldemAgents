import random
import logging

from model.player import Player
from model.action import Action


class Robby(Player):
    persona = "Robbie Random"

    def play(self, table, player_status, is_called=False):
        random_value = random.random()
        if is_called:
            if self.max_bet > table.bet_amount:
                if random_value > .5:
                    action = Action("MATCH", table.bet_amount)
                else:
                    action = Action("FOLD")
            else:
                if random_value > .5:
                    action = Action("MATCH", self.max_bet, all_in=True)
                else:
                    action = Action("FOLD")
        elif random_value < .33:
            action = Action("CALL", min(table.bet_amount, self.max_bet))
        elif random_value < .67:
            action = Action("FOLD")
        else:
            logging.debug(f"{self.name} wants to raise. Current Bet is {table.bet_amount}, {self.name} has {self.bankroll}")
            if self.max_bet > table.bet_amount:
                action = Action("RAISE", random.randint(table.bet_amount + 1, self.max_bet))
            else:
                logging.debug(f"<> {self.name} is all in <>")
                action = Action("CALL", self.max_bet, all_in=True)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action