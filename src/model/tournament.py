import math
from numpy.random import choice

from model.holdem_round import HoldemRound


class Tournament:
    def __init__(self, players):
        self.players = players

    @property
    def num_players(self, big_blind=2):
        return len(self.players)

    def players_still_in(self, big_blind):
        return [player for player in self.players if player.bankroll >= big_blind]

    def player_status(self):
        for player in self.players:
            print(player)

    def do_first_round(self):
        players = self.players_still_in(2)
        self.players, self.table = HoldemRound(
            players=players,
            blind=1
        ).play()

    def do_round(self):
        players = self.players_still_in(2)
        self.players, self.table = HoldemRound(
            players=players,
            table=self.table
        ).play()

    def play(self):
        # Play rounds until only one player remains
        self.do_first_round()
        # players = [player for player in self.players if player.bankroll > self.tables[0].big_blind] # blinds will all move together
        while len(self.players_still_in(2)) > 1:
            self.do_round()