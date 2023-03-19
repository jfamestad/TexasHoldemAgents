import random
from model.player import Player
from model.action import Action

# this player was written by ChatGPT using gpt3.5

class Paula(Player):
    persona = "Paula Pairs"

    def __init__(self, name, bankroll):
        super().__init__(name, bankroll)

    def has_pair(self, community_cards):
        for card in self.jacks_or_better():
            if card.rank in [c.rank for c in community_cards]:
                return True
        return False

    def play(self, table, player_status, is_called=False):
        # If the player has a pair, raise by 2 times the current bet
        if player_status["hand_type"] == "PAIR":
            action = Action("RAISE", min(2 * table.bet_amount, self.max_bet))
        # Otherwise, if the current bet is less than 10% of the player's bankroll, call
        elif table.bet_amount <= 0.1 * self.bankroll:
            action = Action("CALL", min(table.bet_amount, self.max_bet))
        # Otherwise, fold
        else:
            action = Action("FOLD")
        return action