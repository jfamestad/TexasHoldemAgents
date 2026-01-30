import random

from model.player import Player
from model.action import Action


PAULA_PAIR_MESSAGES = [
    "Two of a kind? That's my kind of hand!",
    "Pairs are beautiful. Raising.",
    "When you've got a pair, you've got to share!",
    "Matched cards, matched energy. Let's go!",
    "Double trouble coming your way!",
    "I see a pair, I raise. It's simple.",
]

PAULA_NO_PAIR_MESSAGES = [
    "No pair? No point. Fold.",
    "I only play pairs. This isn't one.",
    "Wake me up when I get matching cards.",
    "Singles aren't my style. Folding.",
    "Call me when the deck is more generous.",
]


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
            self.last_message = random.choice(PAULA_PAIR_MESSAGES)
        else:
            # Player does not have a pair, fold
            action = Action("FOLD", 0)
            self.last_message = random.choice(PAULA_NO_PAIR_MESSAGES)
        return action
