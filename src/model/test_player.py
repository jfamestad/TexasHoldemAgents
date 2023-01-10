from model.player import Player
from model.deck import Card
from model.table import Table
from model.action import Action

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

    bankroll = player._bankroll
    player.start_holdem_round()
    player.place_small_blind(table)
    assert player._bankroll == bankroll - table.small_blind

    # bankroll = player._bankroll
    # player.place_big_blind(table)
    # assert player._bankroll == bankroll - table.big_blind

    action = Action("CALL", 10)
    bankroll = player._bankroll
    player.start_holdem_round()
    player.process_action(action)
    assert player._bankroll == bankroll - action.amount

