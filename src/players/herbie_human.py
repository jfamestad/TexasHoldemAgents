import logging
from pprint import pprint

from model.player import Player
from model.action import Action


class Herbie(Player):
    persona = "Herbie Human"

    def play(self, table, player_status, is_called=False):

        pprint(player_status)
        print(self._hole)
        print(f"The bet is: {table.bet_amount}")
        if table.flop:
            print(f"Flop: {table.flop}")
        if table.turn:
            print(f"Turn: {table.turn}")
        if table.river:
            print(f"Rover: {table.river}")

        action_types = {
            "c": "CALL",
            "r": "RAISE",
            "f": "FOLD",
        }

        print(
            f"The bet is {table.bet_amount} and you have {self.bankroll} in your bankroll and {self.status.money_on_table} on the table")
        print("Check/ Call, Fold, or Raise")
        prompt = "Enter: c | r | f: "
        action_type_response = input(prompt)
        print(f"Got Action: {action_type_response}")

        if not action_type_response in action_types.keys():
            raise ValueError(f"Invalid Action Type: {action_type_response}. Valid responses: c | r | f")

        amount_response = None
        if action_type_response in ["r"]:
            prompt = "Please enter an amount: "
            amount_response = int(input(prompt))

        if action_type_response in ["c"]:
            amount_response = min(table.bet_amount, self.max_bet)

        all_in = amount_response == self.max_bet
        if all_in:
            print(f"{self.name} is all in")

        action = Action(action_types[action_type_response], amount_response, all_in=all_in)

        # action = Action("CALL", table.bet_amount)
        logging.debug(f"Play - {self.name}: {action}")
        return action

    def check_results(self, table, results):
        pprint(results)