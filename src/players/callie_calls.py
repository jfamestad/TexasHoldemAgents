from model.player import Player
from model.action import Action

class Callie(Player):
    def play(self, table, is_called=False):
        print(f"{self.name} sees the bet is at: {table.bet_amount}")
        if self.max_bet > table.bet_amount:
            action = Action("CALL", table.bet_amount)
        else:
            print(f"{self.name} is all in")
            print(f"{self.name} has {self.bankroll} in the bank and {self.status.money_on_table} on the table")
            action = Action("CALL", self.max_bet, all_in=True)
        print(f"Play - {self.name}: {action.action_type}")
        return action