import json

class Table:
    """
    The table object represents the observable game state for players to use in determining their play

    todo: add a property that returns the fields a player needs instead of passing the whole table to them
    - this is needed because a player could call methods on the table like new_holdem_round() otherwise

    """

    def __init__(self, blind, num_players, dealer_button_index=0):
        self.big_blind = 2 * blind
        self.small_blind = blind
        self.dealer_button_index = dealer_button_index

        # setup dealer, blinds, and first action
        self.num_players = num_players
        self.new_holdem_round()

    def __str__(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        return self.__str__()

    def new_holdem_round(self):
        self.pot = []  # list of bet amounts including blinds
        self.flop = None
        self.turn = None
        self.river = None
        self.dealer_button_index = self.dealer_button_index  # randomly assign someone as dealer
        self.big_blind_index = (self.dealer_button_index - 1) % self.num_players
        self.small_blind_index = (self.dealer_button_index - 2) % self.num_players
        self.bet_amount = self.big_blind  # betting starts at the big blind amount
        self.new_betting_round()

    def payout(self):
        self.pot = []
        self.bet_amount = 0

    def new_betting_round(self):
        self.active_player_index = (self.dealer_button_index + 1) % self.num_players  # play starts to the "right" of the dealer

    @property
    def pot_total(self):
        return sum(self.pot)

    def raise_bet(self, amount):
        if amount > self.bet_amount:
            self.bet_amount = amount
        else:
            raise Exception(f"Current Bet is {self.bet_amount}Cannot raise bet to a lessor amount {amount}")

    def next_turn(self):
        self.active_player_index = (self.active_player_index + 1) % self.num_players
        # print(f"Advanced active player index to {self.active_player_index}")

    def raise_blinds(self):
        self.big_blind *= 2
        self.small_blind *= 2

    def next_round(self):
        self.pot = []
        self.dealer_button_index = (self.dealer_button_index + 1) % self.num_players
        self.small_blind_index = (self.dealer_button_index - 2) % self.num_players
        self.big_blind_index = (self.dealer_button_index - 1) % self.num_players
        self.active_player_index = (self.dealer_button_index + 1) % self.num_players  # play starts to the "right" of the dealer
