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

    # def handle_action(self, action, active_player):
    #     logging.debug(f"handling action: {action}")
    #     self.table.pot.append(active_player.process_action(action))
    #     if action.action_type == CALL:
    #         self.handle_call(action, active_player)
    #     elif action.action_type == FOLD:
    #         self.handle_fold(action, active_player)
    #     elif action.action_type == CHECK:
    #         self.handle_check(action, active_player)
    #     elif action.action_type == RAISE:
    #         self.handle_raise(action, active_player)
    #     elif action.action_type == MATCH:
    #         self.handle_match(action, active_player)
    #     else:
    #         raise Exception(f"Cannot handle action of type: {action.action_type}")
    #
    # def handle_check(self, check, player):
    #     # check is noop
    #     logging.debug(f"{player.name} checks")
    #
    # def handle_raise(self, raise_, player): # 'raise' is a Python reserved keyword
    #     logging.debug(f"{player.name} raises")
    #     self.table.raise_bet(raise_.amount)
    #     if raise_.all_in:
    #         self.handle_all_in(raise_, player)
    #     # todo: process bet
    #     # todo: see whos still in and collect bets
    #
    # def handle_call(self, call, player):
    #     # print(f"{player.name} calls...have all players bet?")
    #     if self.all_players_have_bet:
    #         if not self.is_called:
    #             self.calling_player_name = player.name
    #         logging.debug(f"{player.name} calls, setting holdem_round.is_called = True")
    #         self.is_called = True
    #     if call.all_in:
    #         self.handle_all_in(call, player)
    #     # todo: process bet
    #     # todo: is the round over?
    #
    # def handle_match(self, match, player):
    #     if match.all_in:
    #         self.handle_all_in(match, player)
    #
    # def handle_fold(self, fold, player):
    #     logging.debug(f"{player.name} folds")
    #     #self.player_status[player.name] = False
    #     if self.active_player_count <= 1:
    #         self.betting_round_complete = True
    #
    # def handle_all_in(self, action, player):
    #     if not player.name in self.all_in_players: # only add them the first time
    #         self.all_in_players.append(player.name)
    #         if self.table.bet_amount > action.amount:
    #             self.split_pot(action, player)

    # def split_pot(self, action, player):
    #     logging.debug(f"Splitting pot - {player.name} is all in")
    #     logging.debug(f"Players: {self.players_still_in}")
    #     self._split_pot = [
    #         {
    #             "players": self.players_still_in,
    #             "amount": action.amount
    #         },
    #         {
    #             "players": self.players_still_in.remove(player.name),
    #             "amount": self.table.bet_amount - action.amount
    #         }
    #     ]
    #
    # def handle_push(self, players):
    #     # settle round with multiple winners
    #     logging.debug(f"Handling Push - {players}")

    def do_betting_round(self):
        logging.debug("Starting betting round")
        # for player in self.players:
        #     player.start_betting_round()
        betting_round = BettingRound(self.table, self.players)
        self.players, self.table = betting_round.do_round()
        # self.players, table = betting_round.do_round()
        # print("initializing holdem_round.is_called = False")
        # self.is_called = False
        # self.betting_round_complete = False
        # self.calling_player_name = None

        # handle whose turn it is and apply their action to the table and player

        """
        self.calling_player_name = None
        someone_hasnt_bet = len([player for player in self.players if not player.has_bet]) > 0
        while ( not self.is_called ) or someone_hasnt_bet: # ( not self.is_called ) and ( self.active_player_count > 1 ):
            whos_in = [player for player in self.players if not player.folded]
            if len(whos_in) <= 1:
                logging.debug(f"{whos_in} wins by default")
                break
               
               
        # checking if betting has been called and if everyone has bet yet. We cant ackowledge a call before everyone has bet
        # once everyone has bet, we end betting after the next call 
        """
            #print(self.table)
            # print(f"Active Player Index: {self.table.active_player_index}")

        """
            active_player = self.players[self.table.active_player_index]
        """


            # print(f"Betting - Active Player: {active_player.name}")
            #print(self.player_status)
            #print(active_player.folded)
            #print(self.betting_round_complete)


        """
            if not active_player.folded:
                player_status = {player.name: player.folded for player in self.players}
                logging.debug(f"The bet is {self.table.bet_amount} to {active_player.name}")
                action = active_player.play(self.table, player_status)
                logging.debug(f"Got action: {action}")
                self.handle_action(action, active_player)
        
                # todo: apply action to players pot
                # if action == CALL:
                    # self.calling_player_name = active_player.name
                    # print(f"Calling Player Name: {self.calling_player_name}")
            #self.players[self.table.active_player_index] = active_player
            self.table.next_turn()
            active_player = self.players[self.table.active_player_index]
            someone_hasnt_bet = len([player for player in self.players if not player.has_bet]) > 0
            
            
            # already looping over the wrapped list of players 
            # if they havent folded, show them the table and handle their play (Action)
            # iterate the active player index
        """

        """
        logging.debug("Betting is called...settling up with  remaining players")
        players_still_in = [player.name for player in self.players if not player.folded]
        logging.debug(f"Players still in: {players_still_in}")

        if self.active_player_count <= 1:
            self.betting_round_complete = True
           
        # end the betting round if theres only one player left 
        """

        # go around the table and top up bets from players who are still in
        # while not self.betting_round_complete:
        #     print(f"betting complete: {self.betting_round_complete}")
        #     #print(f"Active Player Index: {self.table.active_player_index}")
        #     active_player = self.players[self.table.active_player_index]
        #     print(active_player.name)
        #     if not active_player.folded:
        #         print(f"Called - Active Player: {active_player.name}")
        #         action = active_player.play(self.table)
        #         self.handle_action(action, active_player)
        #     else:
        #         print(f"Skipped Folded Player - Player: {active_player.name}")


        """
        while not active_player.name == self.calling_player_name:
            if self.active_player_count < 2:
                logging.debug(f"Only one player is remains...winner by default")
                break
            # print(f"Active Player: {active_player.name} - Calling Player: {self.calling_player_name}")
            active_player = self.players[self.table.active_player_index]
            logging.debug(f"Round is called. Match or Fold to {active_player.name}")
            if not active_player.folded:
                player_status = {player.name: player.folded for player in self.players}
                logging.debug(f"Called - Active Player: {active_player.name}")
                action = active_player.play(self.table, player_status, is_called=True)
                self.handle_action(action, active_player)

            logging.debug("Betting round is complete")
            players_still_in = [player.name for player in self.players if not player.folded]
            logging.debug(f"Players still in: {players_still_in}")

            self.table.next_turn()
            active_player = self.players[self.table.active_player_index]

            # go around the table and top up bets from players who are still in
            
        # getting here means someone called the round and everybody has bet
        # we need to go around the table and let everyone match or fold
        # then process their actions
        """

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


        # if len(winners) == 1:
        #     winner_name = winners[0]
        #     winner = [ player for player in self.players if player.name == winner_name ][0]
        #
        #     return winner, best_hand
        # else:
        #     self.handle_push(winners)

        self.winners = winners
        self.results = {
            "pot_size": self.table.pot_total,
            "winners": self.winners,
            "winner_personas": [player.persona for player in self.players if player.name in self.winners],
            "winning_hand": self.winning_hand,
            "all_hands": player_hands,
        }

    def settle_round(self):
        for i in range(len(self.players)):
            if self.players[i].name in self.winners:
                # todo: sum up amounts from the pot
                self.players[i].collect_winnings(math.floor(self.table.pot_total / len(self.winners))) # tip the dealer!
            self.players[i].check_results(self.table, self.results)
        # if self._split_pot:
        #     for winner in [i for i in self.players if i.name == ]:
        #     # for winner in self.winners:
        #         winner.bankroll += (self.table.pot / len(self.winners))
        # else:
        #     winner = self.winners[0]
        #     winner.bankroll += self.table.pot

    def collect_blinds(self):
        logging.debug(f"Collecting blinds")
        self.table.pot.append(self.players[self.table.big_blind_index].place_big_blind(self.table))
        self.table.pot.append(self.players[self.table.small_blind_index].place_small_blind(self.table))

    def play(self):
        logging.debug(f"Playing round with {len(self.players)} players")
        print("Play round")
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
        self.do_betting_round()
        self.showdown()
        self.settle_round()
        return self.players, self.table