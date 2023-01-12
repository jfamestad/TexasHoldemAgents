import math
from numpy.random import choice

from model.holdem_round import HoldemRound


class Tournament:
    def __init__(self, players, tournament_id):
        if len(players) <= 1:
            raise ValueError("")
        self.players = players
        self.tournament_id = tournament_id

    @property
    def num_players(self, big_blind=2):
        return len(self.players)

    def players_still_in(self, big_blind):
        return [player for player in self.players if (player.bankroll >= big_blind)]

    def player_status(self):
        for player in self.players:
            print(player)

    def do_first_round(self):
        players = self.players_still_in(2)
        self.players, self.table = HoldemRound(
            players=players,
            blind=1,
        ).play()

    def do_round(self):
        players = self.players_still_in(self.table.big_blind)
        # todo: dropping players?
        self.players, self.table = HoldemRound(
            players=players,
            table=self.table,
        ).play()

    def play(self):
        # Play rounds until only one player remains
        self.do_first_round()
        # players = [player for player in self.players if player.bankroll > self.tables[0].big_blind] # blinds will all move together
        count_still_in = len(self.players_still_in(self.table.big_blind))
        round_counter = 1
        while count_still_in >= 2:
            print(f"Starting round with players: {self.players_still_in(self.table.big_blind)} last: {count_still_in}")
            self.do_round()
            if round_counter % 10 == 0:
                self.table.raise_blinds()
            count_still_in = len(self.players_still_in(self.table.big_blind))
            print(self.players)
            round_counter += 1
        high_score = max([player.bankroll for player in self.players_still_in(self.table.big_blind)])
        self.winners = [player for player in self.players if player.bankroll == high_score]
        return self.players, self.table
