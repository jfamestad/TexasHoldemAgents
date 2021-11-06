from deck import Card

class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hole = []

    def deal_card(self, card):
        self.hole.append(card)

    def play(self, table):
        # check, bet, raise, call, fold
        return (table)