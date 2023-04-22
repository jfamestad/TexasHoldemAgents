import logging

from model.player import Player
from model.action import Action

class Callie(Player):
    persona = "Callie Calls"

    def __init__(self, name, bankroll, raise_limit=3):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit

    def play(self, table, player_status, is_called=False, round_number=None):
        logging.debug(f"{self.name} sees the bet is at: {table.bet_amount}")
        if self.max_bet > table.bet_amount:
            action = Action("CALL", table.bet_amount)
        else:
            logging.debug(f"{self.name} is all in")
            logging.debug(f"{self.name} has {self.bankroll} in the bank and {self.status.money_on_table} on the table")
            action = Action("CALL", self.max_bet, all_in=True)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action