import random

from model.deck import Deck

class Table:
    # Table object will be passed around to player
    # it contains the publicly viewable aspects of the round
    # stuff like the bets, community cards

    def __init__(self, blind, num_players):
        self.big_blind = 2 * blind
        self.small_blind = blind
        self.pot = [] # list of bets including blinds

        # setup dealer, blinds, and first action
        self.num_players = num_players
        self.dealer_button_index = 0 # randomly assign someone as dealer
        self.big_blind_index = ( self.dealer_button_index - 1 ) % self.num_players
        self.small_blind_index = ( self.dealer_button_index - 2 ) % self.num_players
        self.active_player_index = ( self.dealer_button_index + 1 ) % self.num_players # play starts to the "right" of the dealer

        # community cards
        self.flop = None
        self.turn = None
        self.river = None

    def next_turn(self):
        self.active_player_index = ( self.active_player_index + 1 ) % self.num_players

    def next_round(self):
        self.dealer_button_index = ( self.dealer_button_index + 1 ) % self.num_players
        self.small_blind_index = ( self.dealer_button_index - 2 ) % self.num_players
        self.big_blind_index = ( self.dealer_button_index - 1 ) % self.num_players