import logging

from model.player import Player
from model.action import Action
from model.deck import Card, Deck

JACKS_OR_BETTER = ["J", "Q", "K", "A"]

class Johnny(Player):
    persona = "Johnny Jacks"
    # Johnny wants to play a jacks or better pair
    # he will stay in with a high card Jack or better
    # he will fold after the flop if he doesnt get his pair
    # if he gets it, he wants to raise the bet

    def jacks_or_better(self):
        return [card for card in self._hole if card.rank in JACKS_OR_BETTER]

    def play(self, table, player_status, is_called=False):
        logging.debug(f"{self.name} sees the bet is at: {table.bet_amount}")
        print(f"{self.name} has {self._hole} in the hole")
        has_jack_or_better = max(self._hole).rank in JACKS_OR_BETTER
        print(f"{self.name}'s high card is Jack or better? {has_jack_or_better}")
        betting_round = self.get_game_phase(table)
        print(betting_round)

        if betting_round == 1:

            if not has_jack_or_better:
                # Johnny doesnt play if he doesnt have at least one face card
                return self.fold()

            # we have at least one jack or better...what stage of the round is it?
            if self._hole[0].rank == self._hole[1].rank:
                return self._raise(table)

            return self.call(table)

        if betting_round == 2:
            # todo: flop is exposed, betting before the turn
            # if Johnny got his card, hs doubles down

            if self._hole[0].rank == self._hole[1].rank:
                ranks_in_flop = [card for card in table.flop if card.rank == self._hole[0].rank]
                if len(ranks_in_flop) >= 1:
                    return self._raise(table)
                else:
                    print(f"{self.name} stays in the game")
                    return self.call(table)

            for card in self.jacks_or_better():
                ranks_in_flop = [card.rank for card in table.flop]
                if card.rank in ranks_in_flop:
                    print(f"Jacks or better pair: {card.rank}")
                    print(f"{self.name} wants to go all in")
                    return self._raise(table)

            return self.call(table)

        if betting_round == 3:
            # todo: turn is exposed, betting before the turn
            # if Johnny got his card, hs doubles down

            if self._hole[0].rank == self._hole[1].rank:
                ranks_in_turn = [card for card in [table.turn] if card.rank == self._hole[0].rank]
                if len(ranks_in_turn) >= 1:
                    return self._raise(table)
                else:
                    return self.call(table)

            for card in self.jacks_or_better():
                ranks_in_turn = [card.rank for card in [table.turn]]
                if card.rank in ranks_in_turn:
                    print(f"Jacks or better pair: {card.rank}")
                    return self._raise(table, min(2 * table.bet_amount, self.max_bet))

            return self.call(table)

        if betting_round == 4:
            # todo: flop is exposed, betting before the turn
            # if Johnny got his card, hs doubles down

            if self._hole[0].rank == self._hole[1].rank:
                ranks_in_river = [card for card in [table.river] if card.rank == self._hole[0].rank]
                if len(ranks_in_river) >= 1:
                    return self._raise(table)
                else:
                    return self.call(table)

            for card in self.jacks_or_better():
                ranks_in_river = [card.rank for card in [table.river]]
                if card.rank in ranks_in_river:
                    print(f"Jacks or better pair: {card.rank}")
                    return self._raise(table, 2 * table.bet_amount)
                    return action

            return self.call(table)

        # we shouldnt ever get here
        return self.fold()