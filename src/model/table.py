import random

from deck import Deck

class Table:
    def __init__(self, players, blind):
        self.deck = None
        self.players = players # the list of players was passed in
        self.big_blind = 2 * blind
        self.small_blind = blind
        self.pot = [] # list of bets including blinds

        # setup dealer, blinds, and first action
        self.dealer_button_index = random.randint(0, len(players)) # randomly assign someone as dealer
        self.active_player_index = self.dealer_button_index + 1 % len(players) # play starts to the "right" of the dealer
        self.small_blind_index = self.dealer_button_index - 2 % len(players)
        self.big_blind_index = self.dealer_button_index - 1 % len(players)

        # community cards
        self.flop = None
        self.turn = None
        self.river = None

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
        self.flop = self.deck.draw(3)

    def expose_turn(self):
        self.turn = self.deck.draw()

    def expose_river(self):
        self.river = self.deck.draw()

    def do_betting_round(self):
        pass

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