import logging

from model.action import Action, FOLD, CALL, RAISE, CHECK, MATCH, action_types


class BettingRound:
    def __init__(self, table, players):
        self.is_called = False
        self.betting_round_complete = False
        self.calling_player_name = None
        self.table = table
        self.players = players
        self.reset_active_player_index()
        self.reset_players()
        self.all_in_players = []

    def reset_active_player_index(self):
        self.table.new_betting_round()

    def reset_players(self):
        for player in self.players:
            player.start_betting_round()

    @property
    def still_in(self):
        """
        :return:
        dict with string keys and boolean values
        {
            "Josh": True,
            "Sophia": False,
        }
        """
        still_in = []
        for player in self.players:
            if not player.folded:
                still_in.append(player.name)
        return still_in

    @property
    def all_players_have_bet(self):
        result = True
        for player in self.players:
            if not player.folded:
                if not player.has_bet:
                    result = False
        return result

    def do_round(self):
        print("BettingRound.do_round() start...")

        while not (self.is_called and self.all_players_have_bet):  # ( not self.is_called ) and ( self.active_player_count > 1 ):
            whos_in = [player for player in self.players if not player.folded]
            # print(f"Whos in? {whos_in}")
            if len(whos_in) <= 1:
                logging.debug(f"{whos_in} wins by default")
                break # only one player remains...theyll win this round

            # We have at least two players
            # lets see whos turn it is...
            active_player = self.players[self.table.active_player_index]
            # print(f"Active player: {active_player}")

            # skip them if they're folded
            if not active_player.folded:
                # log the player status before handing it to the player
                player_status = {player.name: player.folded for player in self.players}
                logging.debug(f"The bet is {self.table.bet_amount} to {active_player.name}")

                action = active_player.play(self.table, player_status)
                print(f"{active_player.name}: {action}")
                logging.debug(f"Got action: {action}")

                # handle the players action
                self.handle_action(action, active_player)

            self.table.next_turn()

        return self.players, self.table

    def handle_action(self, action, active_player):
        logging.debug(f"handling action: {action}")
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
        logging.debug(f"{player.name} checks")

    def handle_raise(self, raise_, player): # 'raise' is a Python reserved keyword
        logging.debug(f"{player.name} raises")
        self.table.raise_bet(raise_.amount)
        if raise_.all_in:
            self.handle_all_in(raise_, player)
        # todo: process bet
        # todo: see whos still in and collect bets

    def handle_call(self, call, player):
        # print(f"{player.name} calls...have all players bet?")
        if self.all_players_have_bet:
            if not self.is_called:
                print(f"{player.name} has called the round")
                self.calling_player_name = player.name
            logging.debug(f"{player.name} calls, setting holdem_round.is_called = True")
            self.is_called = True
        if call.all_in:
            self.handle_all_in(call, player)
        # todo: process bet
        # todo: is the round over?

    def handle_match(self, match, player):
        if match.all_in:
            self.handle_all_in(match, player)

    def handle_fold(self, fold, player):
        logging.debug(f"{player.name} folds")
        #self.player_status[player.name] = False
        if len(self.still_in) <= 1:
            self.betting_round_complete = True

    def handle_all_in(self, action, player):
        if not player.name in self.all_in_players: # only add them the first time
            self.all_in_players.append(player.name)
            if self.table.bet_amount > action.amount:
                self.split_pot(action, player)

    def split_pot(self, action, player):
        logging.debug(f"Splitting pot - {player.name} is all in")
        logging.debug(f"Players: {self.still_in}")
        self.table._split_pot = [
            {
                "players": self.still_in,
                "amount": action.amount
            },
            {
                "players": self.still_in.remove(player.name),
                "amount": self.table.bet_amount - action.amount
            }
        ]

    def handle_push(self, players):
        # settle round with multiple winners
        logging.debug(f"Handling Push - {players}")