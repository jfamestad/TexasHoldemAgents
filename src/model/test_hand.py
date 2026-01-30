from model.hand import Hand
from model.deck import Card

card_1 = Card("A", "Diamonds")
card_2 = Card("K", "Diamonds")
card_3 = Card("Q", "Diamonds")
card_4 = Card("J", "Diamonds")
card_5 = Card("10", "Diamonds")

card_6 = Card("10", "Clubs")
card_7 = Card("J", "Spades")
card_8 = Card("10", "Hearts")
card_9 = Card("J", "Hearts")
card_10 = Card("J", "Spades")

card_11 = Card("A", "Diamonds")
card_12 = Card("2", "Diamonds")
card_13 = Card("3", "Diamonds")
card_14 = Card("4", "Diamonds")
card_15 = Card("5", "Hearts")

card_16 = Card("10", "Clubs")
card_17 = Card("J", "Spades")
card_18 = Card("10", "Hearts")
card_19 = Card("9", "Hearts")
card_20 = Card("J", "Spades")

hand_1 = Hand([
    card_1,
    card_2,
    card_3,
    card_4,
    card_5
])

hand_2 = Hand([
    card_6,
    card_7,
    card_8,
    card_9,
    card_10
])

hand_3 = Hand([
    card_11,
    card_12,
    card_13,
    card_14,
    card_15
])

hand_4 = Hand([
    card_16,
    card_17,
    card_18,
    card_19,
    card_20
])

def test_royal():
    assert not hand_1.is_pair
    assert not hand_1.is_three_of_a_kind
    assert hand_1.is_straight
    assert not hand_1.is_full_house
    assert not hand_1.is_two_pair
    assert hand_1.is_flush
    assert not hand_1.is_four_of_a_kind
    assert hand_1.is_straight_flush
    assert hand_1.is_flush
    assert hand_1.is_royal_flush

def test_full_house():
    assert hand_2.is_pair
    assert hand_2.is_three_of_a_kind
    assert not hand_2.is_straight
    assert hand_2.is_full_house
    assert hand_2.is_two_pair
    assert not hand_2.is_flush
    assert not hand_2.is_four_of_a_kind
    assert not hand_2.is_straight_flush
    assert not hand_2.is_flush
    assert not hand_2.is_royal_flush

def test_straight():
    assert not hand_3.is_pair
    assert not hand_3.is_three_of_a_kind
    assert hand_3.is_straight
    assert not hand_3.is_full_house
    assert not hand_3.is_two_pair
    assert not hand_3.is_flush
    assert not hand_3.is_four_of_a_kind
    assert not hand_3.is_straight_flush
    assert not hand_3.is_flush
    assert not hand_3.is_royal_flush

def test_two_pair():
    assert hand_4.is_pair
    assert not hand_4.is_three_of_a_kind
    assert not hand_4.is_straight
    assert not hand_4.is_full_house
    assert hand_4.is_two_pair
    assert not hand_4.is_flush
    assert not hand_4.is_four_of_a_kind
    assert not hand_4.is_straight_flush
    assert not hand_4.is_flush
    assert not hand_4.is_royal_flush

def test_royal_v_full():
    assert hand_1 > hand_2

def test_straight_v_two_pair():
    assert hand_3 > hand_4

def test_royal_v_two_pair():
    assert hand_1 > hand_4

def test_full_v_two_pair():
    assert hand_2 > hand_4


# Tests for rank comparison bug fix
# The bug was comparing rank strings alphabetically ("A" < "K") instead of
# using numeric rank values (Ace=14 > King=13)

def test_pair_aces_beats_pair_kings():
    """Pair of Aces should beat Pair of Kings (not alphabetical order)."""
    # Pair of Aces: A-A-K-Q-9
    pair_aces = Hand([
        Card("A", "Spades"),
        Card("A", "Hearts"),
        Card("K", "Hearts"),
        Card("Q", "Clubs"),
        Card("9", "Clubs")
    ])
    # Pair of Kings: K-K-A-Q-9
    pair_kings = Hand([
        Card("K", "Clubs"),
        Card("K", "Hearts"),
        Card("A", "Hearts"),
        Card("Q", "Clubs"),
        Card("9", "Clubs")
    ])
    assert pair_aces > pair_kings
    assert not pair_kings > pair_aces


def test_three_of_a_kind_aces_beats_kings():
    """Three Aces should beat Three Kings."""
    three_aces = Hand([
        Card("A", "Spades"),
        Card("A", "Hearts"),
        Card("A", "Clubs"),
        Card("K", "Hearts"),
        Card("Q", "Clubs")
    ])
    three_kings = Hand([
        Card("K", "Spades"),
        Card("K", "Hearts"),
        Card("K", "Clubs"),
        Card("A", "Hearts"),
        Card("Q", "Clubs")
    ])
    assert three_aces > three_kings
    assert not three_kings > three_aces


def test_four_of_a_kind_aces_beats_kings():
    """Four Aces should beat Four Kings."""
    four_aces = Hand([
        Card("A", "Spades"),
        Card("A", "Hearts"),
        Card("A", "Clubs"),
        Card("A", "Diamonds"),
        Card("2", "Clubs")
    ])
    four_kings = Hand([
        Card("K", "Spades"),
        Card("K", "Hearts"),
        Card("K", "Clubs"),
        Card("K", "Diamonds"),
        Card("A", "Clubs")
    ])
    assert four_aces > four_kings
    assert not four_kings > four_aces


def test_two_pair_aces_and_twos_beats_kings_and_queens():
    """Two pair A-A-2-2 should beat K-K-Q-Q."""
    two_pair_aces = Hand([
        Card("A", "Spades"),
        Card("A", "Hearts"),
        Card("2", "Clubs"),
        Card("2", "Diamonds"),
        Card("3", "Hearts")
    ])
    two_pair_kings = Hand([
        Card("K", "Spades"),
        Card("K", "Hearts"),
        Card("Q", "Clubs"),
        Card("Q", "Diamonds"),
        Card("A", "Hearts")
    ])
    assert two_pair_aces > two_pair_kings
    assert not two_pair_kings > two_pair_aces


def test_full_house_aces_over_twos_beats_kings_over_queens():
    """Full house A-A-A-2-2 should beat K-K-K-Q-Q."""
    full_house_aces = Hand([
        Card("A", "Spades"),
        Card("A", "Hearts"),
        Card("A", "Clubs"),
        Card("2", "Diamonds"),
        Card("2", "Hearts")
    ])
    full_house_kings = Hand([
        Card("K", "Spades"),
        Card("K", "Hearts"),
        Card("K", "Clubs"),
        Card("Q", "Diamonds"),
        Card("Q", "Hearts")
    ])
    assert full_house_aces > full_house_kings
    assert not full_house_kings > full_house_aces


def test_pair_same_rank_higher_kicker_wins():
    """When pairs are equal, higher kicker should win."""
    # Pair of Kings with Ace kicker
    pair_kings_ace_kicker = Hand([
        Card("K", "Spades"),
        Card("K", "Hearts"),
        Card("A", "Clubs"),
        Card("5", "Diamonds"),
        Card("3", "Hearts")
    ])
    # Pair of Kings with Queen kicker
    pair_kings_queen_kicker = Hand([
        Card("K", "Clubs"),
        Card("K", "Diamonds"),
        Card("Q", "Spades"),
        Card("5", "Hearts"),
        Card("3", "Clubs")
    ])
    assert pair_kings_ace_kicker > pair_kings_queen_kicker
    assert not pair_kings_queen_kicker > pair_kings_ace_kicker