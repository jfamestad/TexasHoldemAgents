from model.player import Player
from model.deck import Card
from model.table import Table

def test_init():
    player = Player(
        name="Josh",
        bankroll=100,
    )
    card1 = Card("A", "Hearts")
    card2 = Card("J", "Clubs")
    card3 = Card("A", "Spades")
    card4 = Card("3", "Clubs")
    card5 = Card("Q", "Diamonds")
    card6 = Card("3", "Hearts")
    card7 = Card("A", "Diamonds")

    player.deal_card(card1)
    player.deal_card(card2)

    table = Table(1, 4)

