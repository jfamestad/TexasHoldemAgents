import random
import math
import logging

from model.table import Table
from model.deck import Deck
# from model.action import Action, FOLD, CALL, RAISE, CHECK, MATCH, action_types
from model.betting_round import BettingRound

class HoldemRound:
    # HoldemRound orchestrates the game play including player and deck management
    # it passes th Table object around as a shared state the public game knowledge

    def __init__(self, players, blind=1, table=None, raise_blinds=False):
        self.players = players  # the list of players was passed in
        if table:
            self.table = table
            self.table.new_holdem_round()
            self.table.num_players = len(players)
            self.table.next_round()
            if raise_blinds:
                self.table.raise_blinds()
        else:
            self.dealer_button_index = random.randint(0, len(players))
            self.table = Table(blind, len(players))
            if raise_blinds:
                raise Exception("Cannot raise blinds on new table. raise_blinds requires a table parameter.")
        self.deck = None
        self.results = None
        self.betting_round_complete = False
        self.is_called = False
        self.all_in_players = []
        self._split_pot = None
        self._last_total_money = None
        self.player_status = {f"{player.name}": False for player in self.players} # True if a player is still in the game, False when they fold
        for player in self.players:
            player.start_holdem_round()

    @property
    def active_player_count(self):
        count = len(self.players_still_in)
        logging.debug(f"Player still in count: {count}")
        return count

    @property
    def players_still_in(self):
        still_in = [player.name for player in self.players if not player.folded]
        logging.debug(f"Still in: {still_in}")
        return [player.name for player in self.players if not player.folded]

    @property
    def all_players_have_bet(self):
        players = [ player for player in self.players if player.name in self.players_still_in ]
        return len([ player for player in players if not player.has_bet ]) == 0

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
        # print("dealing the river")
        self.table.river = self.deck.draw()

    def do_betting_round(self):
        logging.debug("Starting betting round")
        print(f"Do the preround money check")
        betting_round = BettingRound(self.table, self.players)
        betting_round.check_money_supply()
        self.players, self.table = betting_round.do_round()
        print("Checking post round money supply")
        betting_round.check_money_supply()

    def showdown(self):
        #best_hands = [ player.best_hand(self.table) for player in self.players if not player.folded ]
        player_hands = {player.name: player.best_hand(self.table) for player in self.players if not player.folded}
        print(player_hands)
        self.winning_hand = max([player_hands[player.name] for player in self.players if not player.folded])
        logging.info(f"Winning Hand: {self.winning_hand}")
        print(f"{self.winning_hand.describe()}: {self.winning_hand}")
        winners = [ player for player in player_hands if player_hands[player] == self.winning_hand ]
        assert len(winners) >= 1 # should be at least one winner
        logging.debug(winners)

        logging.debug(f"Flop: {self.table.flop}")
        logging.debug(f"Turn: {self.table.turn}")
        logging.debug(f"River: {self.table.river}")

        if len(winners) > 1:
            for winner in winners:
                logging.debug(f"Multiple Winners...")
                logging.debug(f"    Winner: {winner}")
                player = [player for player in self.players if player.name == winner][0]
                # print(f"{player.name} hole: {player.hole}")

            for player_name in player_hands:
                logging.debug(f"{player_name}: {player_hands[player_name]}")

        self.winners = winners
        self.results = {
            "pot_size": self.table.pot_total,
            "winners": self.winners,
            "winner_personas": [player.persona for player in self.players if player.name in self.winners],
            "winning_hand": self.winning_hand,
            "all_hands": player_hands,
        }

    def settle_round(self):
        # print("Checking before betting players settle up")
        # self.check_total_money()
        for i in range(len(self.players)):
            name = self.players[i].name
            if name in self.winners:
                # print(f"Checking before {name} settles up")
                # self.check_total_money()
                # todo: sum up amounts from the pot
                players_share_of_pot = math.floor(self.table.pot_total / len(self.winners)) # tip the dealer!
                print(f"{name} collects {players_share_of_pot} from the pot. total pot size {self.table.pot_total}")
                self.players[i].collect_winnings(players_share_of_pot)
                # print(f"Checking after {name} settles up")
                # self.check_total_money()
            # print(f"Checking after players all settle up")
            # self.check_total_money()
            self.table.payout()
            self.players[i].check_results(self.table, self.results)
            # print("Checking after letting players check results")
            # self.check_total_money()

    def collect_blinds(self):
        logging.debug(f"Collecting blinds")
        self.table.pot.append(self.players[self.table.big_blind_index].place_big_blind(self.table))
        self.table.pot.append(self.players[self.table.small_blind_index].place_small_blind(self.table))

    def check_total_money(self):
        print(f"Checking money supply for change. Last value: {self._last_total_money}")
        total = sum([player.bankroll for player in self.players]) + self.table.pot_total
        print(f"Current Total: {total}")
        # if (not total is None) and (total > 1100):
        #     raise Exception("New Money detected in game")
        if self._last_total_money is None:
            print(f"First check of money supply. Nonevalue ok {self._last_total_money}")
            self._last_total_money = total
        else:
            if not self._last_total_money == total:
                print(f"New money detected. Change in total money in game: {self._last_total_money}")
                raise Exception("New Money detected in game")
        self._last_total_money = total
        return self._last_total_money

    def play(self):
        logging.debug(f"Playing round with {len(self.players)} players")
        print("Play round")
        self.table.new_holdem_round()
        # self.check_total_money()
        assert len(self.players) > 1
        for player in self.players:
            player.start_holdem_round()
        self.collect_blinds()
        self.deal()
        self.do_betting_round()
        self.expose_flop()
        self.do_betting_round()
        self.expose_turn()
        self.do_betting_round()
        self.expose_river()
        # print("Checking before betting round after river")
        # self.check_total_money()
        self.do_betting_round()
        # print("Checking before showdown")
        # self.check_total_money()
        self.showdown()
        # print("Checking before settle")
        # self.check_total_money()
        self.settle_round()
        # print("Checking after settle")
        # self.check_total_money()
        return self.players, self.table