from model.table import Table

num_players = 8


def test_init():
    table = Table(1, num_players)
    assert table.flop is None
    assert table.turn is None
    assert table.river is None


def test_next_turn():
    table = Table(1, num_players)
    active_player_index = table.active_player_index
    table.next_turn()
    assert table.active_player_index == ( active_player_index + 1 ) % num_players
    for i in range(10 * num_players):
        assert table.active_player_index < num_players
        assert table.active_player_index >= 0
        table.next_turn()


def test_next_round():
    table = Table(1, num_players)
    dealer_button_index = table.dealer_button_index
    big_blind_index = table.big_blind_index
    small_blind_index = table.small_blind_index
    table.next_round()
    assert table.dealer_button_index == ( dealer_button_index + 1 ) % num_players
    assert table.big_blind_index == ( big_blind_index + 1 ) % num_players
    assert table.small_blind_index == ( small_blind_index + 1 ) % num_players
    for i in range(10 * num_players):
        assert table.dealer_button_index < num_players
        assert table.dealer_button_index >= 0
        table.next_round()
