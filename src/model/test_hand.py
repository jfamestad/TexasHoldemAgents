from hand import Hand
from deck import Card

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