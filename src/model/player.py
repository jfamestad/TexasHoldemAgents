from itertools import combinations
from model.action import Action

class PlayerStatus:
    def __init__(self):
        self.folded = False
        self.money_on_table = 0

class Player:
    def __init__(self, name, bankroll):
        self.name = name
        self.bankroll = bankroll
        self.hole = []
        self._folded = False

    @property
    def folded(self):
        return self._folded

    def start_round(self):
        self.status = PlayerStatus()
        self.hole = []
        self._folded = False

    def process_action(self, action):
        print(f"Processing Action - {self.name}: {action.action_type}")
        if action.action_type == action.FOLD:
            print(f"{self.name}: {action.action_type}")
            self.status["folded"] = True # deprecate
            self.status._folded = True
            return { "cash": 0 }
        elif action.action_type in [ action.RAISE, action.CALL ]:
            cash_into_pot = action.amount - self.status["money_on_table"]
            self.bankroll -= cash_into_pot
            self.status["money_on_table"] = self.status["money_on_table"] + action.amount
            return { "cash": cash_into_pot }
        elif action.action_type == action.CHECK:
            return {"cash": 0}
        else:
            raise Exception(f"Invalid action type: {action.action_type}")

    def deal_card(self, card):
        print(f"delt {self.name} to {card}")
        self.hole.append(card)

    def play(self, table):
        pass

    def _all_five_card_hands(self, cards):
        all_cards = self.hole
        all_cards.extend(cards)
        return combinations(all_cards, 5)

    def best_hand(self, table):
        # return Hand()
        cards_on_table = table.turn + table.flop + table.river
        return max(self._all_five_card_hands(cards_on_table))