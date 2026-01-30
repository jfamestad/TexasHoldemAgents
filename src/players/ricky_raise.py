import random
import logging

from model.player import Player
from model.action import Action


RICKY_RAISE_MESSAGES = [
    "Let's make this interesting. Raise!",
    "Too quiet in here. RAISE!",
    "You think that's a bet? Let me show you a bet.",
    "I came here to raise. So I'm raising.",
    "Scared money don't make money. Raise!",
    "Let's pump up the stakes!",
    "Who wants to play for real money? Raise!",
    "That's cute. Here's a real bet.",
    "I'm feeling lucky. Raise!",
    "Fortune favors the bold! Raise!",
]

RICKY_FOLD_MESSAGES = [
    "Even I know when to quit. Fold.",
    "Fine, you win this one.",
    "I'll get you next hand.",
    "Tactical retreat. For now.",
]

RICKY_MATCH_MESSAGES = [
    "Alright, alright. I'll match.",
    "You got me. Matching.",
    "Fair enough. Match.",
]


class Ricky(Player):
    persona = "Ricky Raise"

    def __init__(self, name, bankroll, raise_limit=3):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit

    def start_betting_round(self):
        super().start_betting_round()
        self.raise_count = 0

    def play(self, table, player_status, is_called=False, round_number=None):
        if is_called:
            action = Action("MATCH", min(table.bet_amount, self.max_bet))
            self.last_message = random.choice(RICKY_MATCH_MESSAGES)
        elif self.bankroll > table.bet_amount and self.raise_count < self.raise_limit:
            min_raise = table.bet_amount + 1
            if min_raise >= self.max_bet:
                bet_amount = self.max_bet
            else:
                bet_amount = random.randint(min_raise, self.max_bet)
            action = self._raise(table, bet_amount)
            self.raise_count += 1
            self.last_message = random.choice(RICKY_RAISE_MESSAGES)
        else:
            action = Action("FOLD")
            self.last_message = random.choice(RICKY_FOLD_MESSAGES)
        logging.debug(f"Play - {self.name}: {action.action_type}")
        return action

