import itertools
import random


suits = ["Hearts", "Clubs", "Spades", "Diamonds"]

ranks = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14
}


class Card(dict):
    _suits = suits
    _ranks = ranks

    def __init__(self, rank, suit):
        if not rank in self._ranks:
            raise Exception("Cannot create card. Invalid rank.")
        if not suit in self._suits:
            raise Exception("Cannot create card. Invalid suit")
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "Card(\"{}\", \"{}\")".format(self.rank, self.suit)

    def __eq__(self, other):
        return self.rank == other.rank

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self._ranks[self.rank] < self._ranks[other.rank]

    def __le__(self, other):
        return self._ranks[self.rank] <= self._ranks[other.rank]

    def __gt__(self, other):
        return self._ranks[other.rank] < self._ranks[self.rank]

    def __ge__(self, other):
        return self._ranks[other.rank] <= self._ranks[self.rank]


class Deck:
    _suits = suits
    _ranks = ranks
    _cards = [Card(rank, suit) for rank, suit in itertools.product(_ranks, _suits)]

    # def __init__(self, random_seed=None):
    #     self.random_seed = random_seed

    def shuffle(self):
        self._cards = random.sample(self._cards, len(self._cards))

    def draw_card(self):
        cards_left = len(self._cards)
        card = self._cards[0]
        self._cards.remove(card)
        assert len(self._cards) == cards_left - 1
        return card

    def draw_cards(self, count=1):
        cards = []
        for i in range(count):
            if len(self._cards) == 0:
                raise Exception("Cannot draw card. No cards left in deck")
            # card = self._cards[0]
            card = self._cards.pop(0)
            cards.append(card)
        return cards

    def draw(self, count=None):
        if count == None:
            return self.draw_card()
        return self.draw_cards(count)
