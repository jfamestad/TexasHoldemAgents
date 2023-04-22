from model.player import Player
from model.action import Action

class Paula(Player):
    persona = "Paula Pairs"

    def play(self, table, player_status, is_called=False, round_number=None):
        # Check if player has a pair
        hand = self._hole
        if hand[0] == hand[1]:
            # If player has a pair, raise bet by double the current bet
            if table.bet_amount * 2 <= self.max_bet:
                action = Action("RAISE", table.bet_amount * 2)
            else:
                if self.max_bet <= table.bet_amount:
                    action = Action("CALL", self.max_bet, all_in=True)
                else:
                    action = Action("RAISE", self.max_bet, all_in=True)
        else:
            # Player does not have a pair, fold
            action = Action("FOLD", 0)
        return action
