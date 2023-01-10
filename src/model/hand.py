from model.deck import Deck, Card, ranks, suits

hand_rankings = {
    "ROYAL_FLUSH": 1,
    "STRAIGHT_FLUSH": 2,
    "FOUR_OF_A_KIND": 3,
    "FULL_HOUSE": 4,
    "FLUSH": 5,
    "STRAIGHT": 6,
    "THREE_OF_A_KIND": 7,
    "TWO_PAIR": 8,
    "PAIR": 9,
    "HIGH_CARD": 10
}


class Hand:
    _cards = []
    _ace_low = False

    def __init__(self, cards):
        if len(cards) == 5:
            self._cards = cards
        else:
            raise ("Expected 5 cards in hand")

    def __str__(self):
        return "{}, {}, {}, {}, {}".format(*["{}{}".format(card.rank, card.suit[0]) for card in self._cards])

    def __repr__(self):
        cards_string = "[{}, {}, {}, {}, {}]".format(*self._cards)
        return "Hand({})".format(cards_string)

    @property
    def suits(self):
        return {card.suit for card in self._cards}

    @property
    def ranks(self):
        return {card.rank for card in self._cards}

    @property
    def high_card(self):
        if self._ace_low:
            not_ace = [card for card in self._cards if not card.rank == "A"]
            return max(not_ace)
        return max(self._cards)

    def sort(self):
        return sorted(self._cards)

    def next_high_card(self, ranks):
        # rank = []
        # return high card after removing passed ranks
        # eg: [3, 6, 7, 8 ,9].next_high([8, 9]) = 7
        considered_cards = [card for card in self._cards if not card.rank in ranks]
        return max(considered_cards) if len(considered_cards) > 0 else None

    @property
    def rank_frequencies(self):
        ranks_in_hand = {card.rank for card in self._cards}
        rank_frequencies = {}
        for rank in ranks_in_hand:
            count = len([card for card in self._cards if card.rank == rank])
            rank_frequencies[rank] = count
        return rank_frequencies

    @property
    def is_flush(self):
        return len(self.suits) == 1

    @property
    def is_straight(self):
        # a straight has 5 unique values (ie: no pairs)
        hand_ranks = {ranks[card.rank] for card in self._cards}
        if len(ranks) < 5:
            return False

        if 2 in hand_ranks and 14 in hand_ranks:
            # Have an Ace and a King (14, 13) so we should check for Ace low straight
            # instead of Ace high
            hand_ranks.discard(14)
            hand_ranks.add(1)
            self._ace_low = True

        low_card = min(hand_ranks)
        for i in range(4):
            if not ((low_card + i) in hand_ranks):
                return False
        return True

    @property
    def is_straight_flush(self):
        return self.is_straight and self.is_flush

    @property
    def is_royal_flush(self):
        return self.is_straight_flush and ("A" in self.ranks) and ("K" in self.ranks)

    @property
    def is_pair(self):
        return 2 in {self.rank_frequencies[rank] for rank in self.ranks}

    @property
    def is_two_pair(self):
        return len([rank for rank in self.ranks if self.rank_frequencies[rank] >= 2]) == 2

    @property
    def is_three_of_a_kind(self):
        return 3 in {self.rank_frequencies[rank] for rank in self.ranks}

    @property
    def is_full_house(self):
        return self.is_pair and self.is_three_of_a_kind

    @property
    def is_four_of_a_kind(self):
        return 4 in {self.rank_frequencies[rank] for rank in self.ranks}

    def __eq__(self, other):
        sorted_other = other.sort()
        for i, card in enumerate(self.sort(), start=0):
            if not sorted_other[i].rank == card.rank:
                return False
        return self.is_flush == other.is_flush

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        self_description = self.describe()
        self_hand_rank = self_description[0]

        other_description = other.describe()
        other_hand_rank = other_description[0]

        if not other_hand_rank == self_hand_rank:
            return hand_rankings[self_hand_rank] > hand_rankings[other_hand_rank]

        if self_hand_rank == "ROYAL_FLUSH":
            return False

        if self_hand_rank in ["STRAIGHT_FLUSH", "STRAIGHT"]:
            return self.high_card < other.high_card

        if self_hand_rank == "FOUR_OF_A_KIND":
            if not self_description[1] == other_description[1]:
                return self_description[1] < other_description[1]
            self_fifth_card = [card for card in self._cards if not card.rank == self_description[1]][0]
            other_fifth_card = [card for card in other._cards if not card.rank == self_description[1]][0]
            return self_fifth_card < other_fifth_card

        if self_hand_rank == "FULL_HOUSE":
            if self_description[1] == other_description[1]:
                # print("same triple, comparing double: {} < {} ? {}".format( self_description[2], other_description[2], self_description[2] < other_description[2]))
                return ranks[self_description[2]] < ranks[other_description[2]]
            return self_description[1] < self_description[1]

        if self_hand_rank == "THREE_OF_A_KIND":
            if self_description[1] == other_description[1]:
                # print("same triple")
                self_next_high = self.next_high_card([self_description[1]])
                other_next_high = other.next_high_card([other_description[1]])
                if self_next_high == other_next_high:
                    # print("same next high")
                    self_last = self.next_high_card([self_description[1]])
                    other_last = other.next_high_card([other_description[1]])
                    return self_last < other_last
                # print("Comparing {} < {}? {}".format(self_next_high, other_next_high, self_next_high < other_next_high))
                return self_next_high < other_next_high
            return self_description[1] < other_description[1]

        if self_hand_rank == "TWO_PAIR":
            self_high_pair = self_description[1][1]
            other_high_pair = other_description[1][1]
            self_low_pair = self_description[1][0]
            other_low_pair = other_description[1][0]
            self_last_card = self.next_high_card([self_high_pair, self_low_pair])
            other_last_card = other.next_high_card([other_high_pair, other_low_pair])
            if self_high_pair == other_high_pair:
                if self_low_pair == other_low_pair:
                    return self_last_card < other_last_card
                return self_low_pair < other_low_pair
            return self_high_pair < other_high_pair

        if self_hand_rank == "PAIR":
            if self_description[1] == other_description[1]:
                self_next_high = self.next_high_card([self_description[1]])
                other_next_high = other.next_high_card([other_description[1]])
                if self_next_high == other_next_high:
                    self_next_next_high = self.next_high_card([self_description[1], self_next_high.rank])
                    other_next_next_high = other.next_high_card([self_description[1], other_next_high.rank])
                    if self_next_next_high == other_next_next_high:
                        self_last = self.next_high_card(
                            [self_description[1], self_next_high.rank, self_next_next_high.rank])
                        other_last = other.next_high_card(
                            [self_description[1], other_next_high.rank, other_next_next_high.rank])
                        return self_last < other_last
                    return self_next_next_high < other_next_next_high
                return self_next_high < other_next_high
            return self_description[1] < other_description[1]

        if self_hand_rank in ["HIGH_CARD", "FLUSH"]:
            sorted_other = other.sort()
            for i, card in enumerate(self.sort(), start=0):
                if not sorted_other[i].rank == card.rank:
                    return card < sorted_other[i]
            return False

    def __le__(self, other):
        return not self > other

    def __gt__(self, other):
        if self == other:
            return False
        return not self < other

    def __ge__(self, other):
        return not self < other

    def describe(self):
        if self.is_royal_flush:
            return ("ROYAL_FLUSH", self.suits)
        elif self.is_straight_flush:
            return ("STRAIGHT_FLUSH", self.high_card, self.suits)
        elif self.is_four_of_a_kind:
            return ("FOUR_OF_A_KIND", [rank for rank in self.ranks if self.rank_frequencies[rank] == 4][0])
        elif self.is_full_house:
            return (
                "FULL_HOUSE",
                [rank for rank in self.ranks if self.rank_frequencies[rank] == 3][0],
                [rank for rank in self.ranks if self.rank_frequencies[rank] == 2][0]
            )
        elif self.is_flush:
            return ("FLUSH", self.high_card)
        elif self.is_straight:
            if not self._ace_low:
                return ("STRAIGHT", self.high_card)
            else:
                return ("STRAIGHT",)
        elif self.is_three_of_a_kind:
            return ("THREE_OF_A_KIND", [rank for rank in self.ranks if self.rank_frequencies[rank] == 3][0])
        elif self.is_two_pair:
            return ("TWO_PAIR", sorted([rank for rank in self.ranks if self.rank_frequencies[rank] == 2]))
        elif self.is_pair:
            return (
                "PAIR",
                [rank for rank in self.ranks if self.rank_frequencies[rank] == 2][0],
                self.high_card
            )
        else:
            return ("HIGH_CARD", self.high_card)
