import logging
import os
import pandas as pd
import shortuuid

from model.holdem_round import HoldemRound


class Tournament:
    def __init__(self, players, tournament_id, results_dir="results"):
        if len(players) <= 1:
            raise ValueError("")
        self.players = players
        self.tournament_id = tournament_id
        self.round_results = []
        self.results_dir = results_dir
        self._uuid = shortuuid.uuid()

    @property
    def num_players(self, big_blind=2):
        return len(self.players)

    def players_still_in(self, big_blind):
        return [player for player in self.players if (player.bankroll >= big_blind)]

    def player_status(self):
        for player in self.players:
            logging.debug(player)

    def do_first_round(self):
        players = self.players_still_in(2)
        holdem_round = HoldemRound(
            players=players,
            blind=1,
        )
        self.players, self.table = holdem_round.play()
        results = holdem_round.results
        results["round_number"] = 0
        results["tournament_id"] = self.tournament_id
        results["tournament_uuid"] = self._uuid
        self.round_results.append(results)

    def do_round(self, round_number):
        players = self.players_still_in(self.table.big_blind)
        print("starting round")
        initial_players = players.copy()
        holdem_round = HoldemRound(
            players=players,
            table=self.table,
            round_number=round_number,
        )
        self.players, self.table = holdem_round.play()
        results = holdem_round.results
        results["round_number"] = round_number
        results["tournament_id"] = self.tournament_id
        results["tournament_uuid"] = self._uuid
        results["player_count"] = self.count_still_in
        results["players_in_round"] = [ player.name for player in initial_players ]
        results["players_eliminated"] = [ player.name for player in initial_players if not player in self.players_still_in(self.table.big_blind) ]
        self.round_results.append(results)

    def write_tournament_results(self):
        df = pd.DataFrame(self.round_results)
        filename = f"tournement-{self._uuid}-{self.tournament_id}.csv"
        filepath = os.path.join(self.results_dir, filename)
        logging.debug(f"Writing tournament results to csv: {filepath}")
        os.makedirs(self.results_dir,
                    exist_ok=True)
        df.to_csv(filepath)

    def play(self):
        # Play rounds until only one player remains
        self.do_first_round()
        # players = [player for player in self.players if player.bankroll > self.tables[0].big_blind] # blinds will all move together
        self.count_still_in = len(self.players_still_in(self.table.big_blind))
        round_counter = 1
        while self.count_still_in >= 2:
            logging.debug(f"Starting round with players: {self.players_still_in(self.table.big_blind)} last: {self.count_still_in}")
            self.do_round(round_counter)
            if round_counter % 10 == 0:
                self.table.raise_blinds()
            self.count_still_in = len(self.players_still_in(self.table.big_blind))
            logging.debug(self.players)
            round_counter += 1
        high_score = max([player.bankroll for player in self.players_still_in(self.table.big_blind)])
        self.winners = [player for player in self.players if player.bankroll == high_score]
        self.write_tournament_results()
        return self.players, self.table
