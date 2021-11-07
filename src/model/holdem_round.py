import random

from table import Table
from deck import Deck

class HoldemRound:
    # HoldemRound orchestrates the game play including player and deck management
    # it passes th Table object around as a shared state the public game knowledge

    def __init__(self, players, blind=1):
        self.players = players  # the list of players was passed in
        dealer_button_index = random.randint(0, len(players))
        self.table = Table(blind, len(players))
        self.deck = None

    def deal(self):
        self.deck = Deck()
        self.deck.shuffle()
        cards_dealt = 0
        while cards_dealt < 2:
            for player in self.players:
                player.deal_card(self.deck.draw())
            cards_dealt += 1

    def expose_flop(self):
        self.deck.draw_card() # burn the top card
        self.table.flop = self.deck.draw(3)

    def expose_turn(self):
        self.table.turn = self.deck.draw()

    def expose_river(self):
        self.table.river = self.deck.draw()

    def do_betting_round(self):
        pass
        # is_called = False
        # until is_called:
        #     self.table = self.players[self.table.active_player_index]

    def showdown(self):
        pass

    def settle_round(self):
        pass

    def play(self):
        self.deal()
        self.do_betting_round()
        self.expose_flop()
        self.do_betting_round()
        self.expose_turn()
        self.do_betting_round()
        self.expose_river()
        self.do_betting_round()
        self.showdown()
        self.settle_round()