import random

from model.table import Table
from model.deck import Deck
from model.action import Action, FOLD, CALL, RAISE, CHECK, action_types

class HoldemRound:
    # HoldemRound orchestrates the game play including player and deck management
    # it passes th Table object around as a shared state the public game knowledge

    def __init__(self, players, blind=1):
        self.players = players  # the list of players was passed in
        dealer_button_index = random.randint(0, len(players))
        self.table = Table(blind, len(players))
        self.deck = None
        self.betting_round_complete = False
        self.is_called = False
        self.player_status = {f"{player.name}": False for player in self.players} # True if a player is still in the game, False when they fold

    @property
    def active_player_count(self):
        #print(f"active player count: {len([player for player in self.player_status if self.player_status[player]])}")
        return len([player for player in self.player_status if self.player_status[player]])

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
        print(f"handing action: {action}")
        if action.action_type == CALL:
            self.handle_call(action, active_player)
        elif action.action_type == FOLD:
            self.handle_fold(action, active_player)
        elif action.action_type == CHECK:
            self.handle_check(action, active_player)
        elif action.action_type == RAISE:
            self.handle_raise(action, active_player)
        else:
            raise Exception(f"Cannot handle action of type: {action.action_type}")

    def handle_check(self, check, player):
        # check is noop
        print(f"{player.name} checks")

    def handle_raise(self, raise_, player): # 'raise' is a Python reserved keyword
        print(f"{player.name} raises")
        # todo: process bet
        # todo: see whos still in and collect bets

    def handle_call(self, call, player):
        self.is_called = True
        print(f"{player.name} has called")
        # todo: process bet
        # todo: is the round over?

    def handle_fold(self, fold, player):
        print(f"{player.name} folds")
        self.player_status[player.name] = False
        if self.active_player_count <= 1:
            self.betting_round_complete = True

    def do_betting_round(self):
        self.is_called = False
        self.betting_round_complete = False

        for player in self.players:
            player.start_round()

        # handle whose turn it is and apply their action to the table and player
        calling_player_name = None
        while not ( self.is_called or self.betting_round_complete ): # ( not self.is_called ) and ( self.active_player_count > 1 ):
            #print(self.table)
            print(f"Active Player Index: {self.table.active_player_index}")
            active_player = self.players[self.table.active_player_index]
            print(f"Betting - Active Player: {active_player.name}")
            #print(self.player_status)
            #print(active_player.folded)
            #print(self.betting_round_complete)
            if not active_player.folded:
                action = active_player.play(self.table)
                print(f"Got action: {action}")
                self.handle_action(action, active_player)
                # todo: apply action to players pot
                if action == CALL:
                    calling_player_name = active_player.name
                    print(f"Calling Player Name: {calling_player_name}")
            #self.players[self.table.active_player_index] = active_player
            self.table.next_turn()

        if self.active_player_count <= 1:
            self.betting_round_complete = True

        # go around the table and top up bets from players who are still in
        while not self.betting_round_complete:
            print(f"betting complete: {self.betting_round_complete}")
            #print(f"Active Player Index: {self.table.active_player_index}")
            active_player = self.players[self.table.active_player_index]
            print(active_player.name)
            if not active_player.folded:
                print(f"Called - Active Player: {active_player.name}")
                action = active_player.play(self.table)
                self.handle_action(action, active_player.name)
            else:
                print(self.player_status[active_player.name])
                print(f"Skipped Folded Player - Player: {active_player.name}")
            self.table.next_turn()

        # go around the table and top up bets from players who are still in



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