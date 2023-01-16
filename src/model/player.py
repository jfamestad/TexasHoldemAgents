from itertools import combinations
import logging

from model.hand import Hand
from model.action import Action, FOLD, CALL, RAISE, CHECK, MATCH


class PlayerStatus:
    def __init__(self):
        self.folded = False
        self._money_on_table = 0
        self.has_bet = False

    def add_chips(self, amount):
        self._money_on_table += amount

    @property
    def money_on_table(self):
        return self._money_on_table


class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self._bankroll = bankroll
        self._hole = []
        self._best_hand = None
        self._games_played = 0
        # self._folded = False

    def __str__(self):
        return f"Player({self.name}, {self._bankroll})"

    def __repr__(self):
        return f"Player({self.name}, {self._bankroll})"

    @property
    def folded(self):
        return self.status.folded

    @property
    def has_bet(self):
        return self.status.has_bet

    @property
    def max_bet(self):
        max_bet = self.status.money_on_table + self.bankroll
        logging.debug(f"{self.name} has a max bet of {max_bet}")
        return max_bet

    @property
    def games_played(self):
        return self._games_played

    def add_chips(self, amount):
        if amount > self.bankroll:
            raise ValueError(f"Cannot add more ({amount}) chips than {self.name} has in bankroll ({self.bankroll}).")
        self.status.add_chips(amount)
        self._bankroll -= amount

    def start_holdem_round(self):
        self.status = PlayerStatus()
        self._hole = []
        self._folded = False
        self._best_hand = None
        self._games_played += 1

    def place_small_blind(self, table):
        logging.debug(f"{self.name} is placing small blind: {table.small_blind}")
        if self.status.money_on_table > 0:
            raise Exception("Cannot place small blind when I already placed big blind")
        # self._bankroll -= table.small_blind
        self.add_chips(table.small_blind)
        logging.debug(f"{self.name} placed small blind: {self._bankroll} left in bankroll")
        return table.small_blind

    def place_big_blind(self, table):
        logging.debug(f"{self.name} is placing big blind: {table.big_blind}")
        if self.status.money_on_table > 0:
            raise Exception("Cannot place big blind when I already placed small blind")
        # self._bankroll -= table.big_blind
        self.add_chips(table.big_blind)
        logging.debug(f"{self.name} placed big blind: {self._bankroll} left in bankroll")
        return table.big_blind

    def start_betting_round(self):
        self.status.has_bet = False

    def process_action(self, action):
        logging.debug(f"Processing Action - {self.name}: {action.action_type}")
        logging.debug(f"{self.name}: {self._bankroll}")
        self.status.has_bet = True
        if action.action_type == FOLD:
            logging.debug(f"{self.name}: {action.action_type}")
            # self.status["folded"] = True # deprecate
            self.status.folded = True
            logging.debug(f"{self.name} is folding: {self._bankroll}")
            return 0
        elif action.action_type in [RAISE, CALL, MATCH]:
            if self._bankroll + self.status.money_on_table < action.amount:
                logging.debug(f"{self.name} has {self._bankroll} in the bank and {self.status.money_on_table} on the table")
                logging.debug(f"Action amount is: {action.amount}")
                raise ValueError("Player does not have enough money for this bet")
            logging.debug(f"Action amount: {action.amount}")
            logging.debug(f"Money on table: {self.status.money_on_table}")
            cash_into_pot = action.amount - self.status.money_on_table  # leaky abstraction need to refactor
            logging.debug(f"Cash into the pot: {cash_into_pot}")
            if cash_into_pot < 0:
                logging.debug(f"WARN: Illegal Request")
                logging.debug(f"WARN: {self.name} handling bet amount {action.amount}")
                logging.debug(f"WARN: {self.name} has bankroll {self.bankroll} and {self.status.money_on_table} on the table")

                raise ValueError("Cannot remove money from the pot")
            logging.debug(f"Cash into pot: {cash_into_pot}")
            # self._bankroll -= cash_into_pot
            logging.debug(f"{self.name} calling, raising, or matching by {action.amount}")
            # self.status.money_on_table += action.amount  # leaky abstraction refactor
            self.add_chips(cash_into_pot)
            logging.debug(f"{self.name} still has: {self._bankroll} in their bankroll")
            return cash_into_pot
        elif action.action_type == CHECK:
            return 0
        else:
            raise Exception(f"Invalid action type: {action.action_type}")

    def deal_card(self, card):
        logging.debug(f"delt {self.name} to {card}")
        self._hole.append(card)
        assert len(self._hole) <= 2

    def play(self, table, player_status, is_called=False):
        pass # Players implement this function to define the Actions they play

    def check_results(self, table, results):
        pass # Players can implement this function to inspect the end state of each round.

    def _all_five_card_hands(self, cards):
        all_cards = self._hole
        all_cards.extend(cards)
        logging.debug(f"{self.name} makes a hand from: {all_cards}")
        card_combinations = combinations(all_cards, 5)
        # print(f"Combinations: {card_combinations}")
        hands = [Hand(cards) for cards in card_combinations]
        # print(f"Hands: {hands}")
        return hands

    def best_hand(self, table, refresh=False):
        logging.debug(f"{self.name} is holding {self._hole}")
        if self.folded:
            return None
        # if not (self._best_hand or refresh):
        cards_on_table = table.flop + [table.turn] + [table.river]
        self._best_hand = max(self._all_five_card_hands(cards_on_table))
        logging.debug(f"{self.name} presents hand: {self._best_hand}")
        return self._best_hand

    def collect_winnings(self, amount):
        logging.debug(f"{self.name} collects a ${amount} pot")
        self._bankroll += amount

    @property
    def bankroll(self):
        return self._bankroll
