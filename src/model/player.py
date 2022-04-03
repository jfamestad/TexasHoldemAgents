from itertools import combinations
from model.hand import Hand
from model.action import Action, FOLD, CALL, RAISE, CHECK

class PlayerStatus:
    def __init__(self):
        self.folded = False
        self.money_on_table = 0

class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hole = []
        self._best_hand = None
        #self._folded = False

    @property
    def folded(self):
        return self.status.folded

    def start_holdem_round(self):
        self.status = PlayerStatus()
        self.hole = []
        self._folded = False
        self._best_hand = None

    def start_betting_round(self):
        self.has_bet = False

    def process_action(self, action):
        print(f"Processing Action - {self.name}: {action.action_type}")
        if action.action_type == FOLD:
            print(f"{self.name}: {action.action_type}")
            #self.status["folded"] = True # deprecate
            self.status.folded = True
            return { "cash": 0 }
        elif action.action_type in [ RAISE, CALL ]:
            cash_into_pot = action.amount - self.status.money_on_table # leaky abstraction need to refactor
            self.bankroll -= cash_into_pot
            self.status.money_on_table = self.status.money_on_table + action.amount # leaky abstraction refactor
            return { "cash": cash_into_pot }
        elif action.action_type == CHECK:
            return {"cash": 0}
        else:
            raise Exception(f"Invalid action type: {action.action_type}")

    def deal_card(self, card):
        print(f"delt {self.name} to {card}")
        self.hole.append(card)
        assert len(self.hole) <= 2

    def play(self, table):
        pass

    def _all_five_card_hands(self, cards):
        all_cards = self.hole
        all_cards.extend(cards)
        print(f"{self.name} makes a hand from: {all_cards}")
        card_combinations = combinations(all_cards, 5)
        #print(f"Combinations: {card_combinations}")
        hands = [ Hand(cards) for cards in card_combinations ]
        #print(f"Hands: {hands}")
        return hands

    def best_hand(self, table, refresh=False):
        if self.folded:
            return None
        if not ( self._best_hand or refresh ):
            cards_on_table = self.hole + table.flop + [table.turn] + [table.river]
            self._best_hand = max(self._all_five_card_hands(cards_on_table))
        print(f"{self.name} presents hand: {self._best_hand}")
        return self._best_hand

    def collect_winnings(self, amount):
        print(f"{self.name} collects a ${amount} pot")
        self.bankroll += amount