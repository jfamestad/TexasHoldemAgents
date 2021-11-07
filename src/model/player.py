from table import Table
from action import Action

class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hole = []

    def deal_card(self, card):
        self.hole.append(card)

    def play(self, table):
        # return action
        pass

    def best_hand(self, table):
        # return Hand()
        pass