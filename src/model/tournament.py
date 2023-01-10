import math
from numpy.random import choice


class Tournament:
    def __init__(self, players, players_per_table=10):
        self.players = players
        self.players_per_table = players_per_table
        self.assign_players_to_tables()

    @property
    def num_players(self):
        return len(self.players)

    def assign_players_to_tables(self):
        # assigns random table assignments
        """
        [
            [players at table 1],
            ...,
            [players at table n]
        ]
        :return:
        """
        self.table_count = math.ceil(self.num_players / self.players_per_table)
        self.tables = []
        for i in range(self.table_count):
            self.table_assignments.append(choice(self.players, max(self.players_per_table, len(self.players))))

        return self.tables


    def setup(self):
        self.num_tables = math.ceil(self.num_players / self.players_per_table)
        self.assign_players_to_tables()

    def do_round(self):
        players = [player for player in self.players if player.bankroll > self.table.big_blind]
        for table_assignment in self.table_assignments:
            if self.table:
                self.players, self.table = HoldemRound(
                    players=players,
                    table=table
                ).play()
            else:
                self.players, self.table = HoldemRound(
                    players=players,
                    blind=1
                ).play()

    def play(self):
        # Play rounds until only one player remains
        pass
