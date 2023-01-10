import random

from model.table import Table
from model.deck import Deck
from model.action import Action, FOLD, CALL, RAISE, CHECK, MATCH, action_types

class HoldemRound:
    # HoldemRound orchestrates the game play including player and deck management
    # it passes th Table object around as a shared state the public game knowledge

    def __init__(self, players, blind=1, table=None, raise_blinds=False):
        self.players = players  # the list of players was passed in
        if table:
            self.table = table
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
        self.betting_round_complete = False
        self.is_called = False
        self.all_in_players = []
        self._split_pot = None
        self.player_status = {f"{player.name}": False for player in self.players} # True if a player is still in the game, False when they fold
        for player in self.players:
            player.start_holdem_round()

    @property
    def active_player_count(self):
        return len(self.players_still_in)

    @property
    def players_still_in(self):
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
        self.table.river = self.deck.draw()

    def handle_action(self, action, active_player):
        print(f"handling action: {action}")
        self.table.pot.append(active_player.process_action(action))
        if action.action_type == CALL:
            self.handle_call(action, active_player)
        elif action.action_type == FOLD:
            self.handle_fold(action, active_player)
        elif action.action_type == CHECK:
            self.handle_check(action, active_player)
        elif action.action_type == RAISE:
            self.handle_raise(action, active_player)
        elif action.action_type == MATCH:
            self.handle_match(action, active_player)
        else:
            raise Exception(f"Cannot handle action of type: {action.action_type}")

    def handle_check(self, check, player):
        # check is noop
        print(f"{player.name} checks")

    def handle_raise(self, raise_, player): # 'raise' is a Python reserved keyword
        print(f"{player.name} raises")
        self.table.raise_bet(raise_.amount)
        if raise_.all_in:
            self.handle_all_in(raise_, player)
        # todo: process bet
        # todo: see whos still in and collect bets

    def handle_call(self, call, player):
        # print(f"{player.name} calls...have all players bet?")
        if self.all_players_have_bet:
            if not self.is_called:
                self.calling_player_name = player.name
            print(f"{player.name} calls, setting holdem_round.is_called = True")
            self.is_called = True
        if call.all_in:
            self.handle_all_in(call, player)
        # todo: process bet
        # todo: is the round over?

    def handle_match(self, match, player):
        if match.all_in:
            self.handle_all_in(match, player)

    def handle_fold(self, fold, player):
        print(f"{player.name} folds")
        #self.player_status[player.name] = False
        if self.active_player_count <= 1:
            self.betting_round_complete = True

    def handle_all_in(self, action, player):
        self.all_in_players.append(player.name)
        if self.table.bet_amount > action.amount:
            self.split_pot(action, player)

    def split_pot(self, action, player):
        print(f"Splitting pot - {player.name} is all in")
        print(f"Players: {self.players_still_in}")
        self._split_pot = [
            {
                "players": self.players_still_in,
                "amount": action.amount
            },
            {
                "players": self.players_still_in.remove(player.name),
                "amount": self.table.bet_amount - action.amount
            }
        ]

    def handle_push(self, players):
        # settle round with multiple winners
        print(f"Handling Push - {players}")

    def do_betting_round(self):
        print("Starting betting round")
        # print("initializing holdem_round.is_called = False")
        self.is_called = False
        self.betting_round_complete = False
        self.calling_player_name = None

        # handle whose turn it is and apply their action to the table and player
        calling_player_name = None
        while not ( self.is_called ): # ( not self.is_called ) and ( self.active_player_count > 1 ):
            #print(self.table)
            # print(f"Active Player Index: {self.table.active_player_index}")
            active_player = self.players[self.table.active_player_index]
            # print(f"Betting - Active Player: {active_player.name}")
            #print(self.player_status)
            #print(active_player.folded)
            #print(self.betting_round_complete)
            if not active_player.folded:
                print(f"The bet is {self.table.bet_amount} to {active_player.name}")
                action = active_player.play(self.table)
                print(f"Got action: {action}")
                self.handle_action(action, active_player)
                # todo: apply action to players pot
                # if action == CALL:
                    # self.calling_player_name = active_player.name
                    # print(f"Calling Player Name: {self.calling_player_name}")
            #self.players[self.table.active_player_index] = active_player
            self.table.next_turn()

        print("Betting is called...settling up with  remaining players")
        players_still_in = [player.name for player in self.players if not player.folded]
        print(f"Players still in: {players_still_in}")

        if self.active_player_count <= 1:
            self.betting_round_complete = True

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
        active_player = self.players[self.table.active_player_index]
        while not active_player.name == self.calling_player_name:
            # print(f"Active Player: {active_player.name} - Calling Player: {self.calling_player_name}")
            active_player = self.players[self.table.active_player_index]
            print(f"Round is called. Match or Fold to {active_player.name}")
            if not active_player.folded:
                print(f"Called - Active Player: {active_player.name}")
                action = active_player.play(self.table, is_called=True)
                self.handle_action(action, active_player)
            self.table.next_turn()
            active_player = self.players[self.table.active_player_index]

        print("Betting round is complete")
        players_still_in = [player.name for player in self.players if not player.folded]
        print(f"Players still in: {players_still_in}")

        # go around the table and top up bets from players who are still in

    def showdown(self):
        #best_hands = [ player.best_hand(self.table) for player in self.players if not player.folded ]
        player_hands = { player.name: player.best_hand(self.table) for player in self.players if not player.folded }
        best_hand = max([ player.best_hand(self.table) for player in self.players if not player.folded ])
        print(f"Winning Hand: {best_hand}")
        print(f"{best_hand.describe()}: {best_hand}")
        winners = [ player for player in player_hands if player_hands[player] == best_hand ]
        print(winners)

        print(f"Flop: {self.table.flop}")
        print(f"Turn: {self.table.turn}")
        print(f"River: {self.table.river}")

        if len(winners) > 1:
            for winner in winners:
                print(f"Multiple Winners...")
                print(f"    Winner: {winner}")
                player = [player for player in self.players if player.name == winner][0]
                print(f"{player.name} hole: {player.hole}")

            for player_name in player_hands:
                print(f"{player_name}: {player_hands[player_name]}")

        # if len(winners) == 1:
        #     winner_name = winners[0]
        #     winner = [ player for player in self.players if player.name == winner_name ][0]
        #
        #     return winner, best_hand
        # else:
        #     self.handle_push(winners)

        return winners

    def settle_round(self, players):


        self.winners = players
        for i in range(len(self.players)):
            if self.players[i].name in self.winners:
                # todo: sum up amounts from the pot
                self.players[i].collect_winnings(self.table.pot_total / len(self.winners)) # bug - only paying out bet amount
        # if self._split_pot:
        #     for winner in [i for i in self.players if i.name == ]:
        #     # for winner in self.winners:
        #         winner.bankroll += (self.table.pot / len(self.winners))
        # else:
        #     winner = self.winners[0]
        #     winner.bankroll += self.table.pot

    def collect_blinds(self):
        print("Collecting blinds")
        self.table.pot.append(self.players[self.table.big_blind_index].place_big_blind(self.table))
        self.table.pot.append(self.players[self.table.small_blind_index].place_small_blind(self.table))

    def play(self):
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
        self.winners = self.showdown()
        self.settle_round(self.winners)
        return self.players, self.table