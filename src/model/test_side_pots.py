"""Tests for side pot handling when players are all-in for different amounts.

When a player is all-in for less than other bets, they can only win an amount
equal to their contribution from each player. The excess goes into side pots.
"""
import pytest
from model.player import Player
from model.action import Action
from model.holdem_round import HoldemRound
from model.deck import Card


class ScriptedPlayer(Player):
    """A player that follows a script of predetermined actions."""
    persona = "Scripted"

    def __init__(self, name: str, bankroll: int, actions: list[Action] = None):
        super().__init__(name, bankroll)
        self.actions = actions or []
        self.action_index = 0

    def play(self, table, player_status, is_called=False, round_number=None):
        if self.action_index < len(self.actions):
            action = self.actions[self.action_index]
            self.action_index += 1
            return action
        # Default to call if no more scripted actions
        return self.call(table)

    def reset_script(self, actions: list[Action]):
        self.actions = actions
        self.action_index = 0


class TestSidePots:
    """Test that side pots are calculated correctly."""

    def test_all_in_player_wins_only_matched_amount(self):
        """
        Scenario from bug report:
        - Player A bets $315
        - Player B (Johnny) is all-in with $100
        - Player C (Paula) is all-in with $100

        If Johnny wins, he should only get $300 (100 from each of 3 players),
        not the full $515 pot.
        """
        # Create players with specific bankrolls
        # Johnny and Paula start with $100, Player A starts with more
        # We'll give Johnny the best hand by controlling the cards

        player_a = ScriptedPlayer("PlayerA", 400)
        johnny = ScriptedPlayer("Johnny", 100)
        paula = ScriptedPlayer("Paula", 100)

        players = [player_a, johnny, paula]

        # Set up the round
        game = HoldemRound(players=players, blind=1)

        # Initialize players for the round
        for p in players:
            p.start_holdem_round()

        # Manually set up the scenario:
        # - Johnny and Paula are all-in at $100
        # - PlayerA bets $315

        # Simulate the betting by directly manipulating state
        # Johnny goes all-in: $100
        johnny.add_chips(100)
        game.table.pot.append(100)
        game.table.bet_amount = 100

        # Paula goes all-in: $100
        paula.add_chips(100)
        game.table.pot.append(100)

        # PlayerA bets $315
        player_a.add_chips(315)
        game.table.pot.append(315)
        game.table.bet_amount = 315

        # Give Johnny the winning hand (Royal Flush)
        johnny._hole = [Card("A", "Spades"), Card("K", "Spades")]
        paula._hole = [Card("2", "Hearts"), Card("3", "Hearts")]
        player_a._hole = [Card("7", "Clubs"), Card("8", "Clubs")]

        # Set community cards for Johnny to have royal flush
        game.table.flop = [Card("Q", "Spades"), Card("J", "Spades"), Card("10", "Spades")]
        game.table.turn = Card("2", "Clubs")
        game.table.river = Card("3", "Clubs")

        # Record bankrolls before showdown
        johnny_before = johnny.bankroll
        paula_before = paula.bankroll
        player_a_before = player_a.bankroll

        # Verify pot total is $515
        assert game.table.pot_total == 515

        # Run showdown and settle
        game.showdown()
        game.settle_round()

        # Johnny should win the main pot: $100 * 3 = $300
        # (He can only win up to his contribution from each player)
        expected_johnny_winnings = 300

        # PlayerA should get back the unmatched portion: $315 - $100 = $215
        # (No one could match above $100)
        expected_player_a_return = 215

        # Johnny's new bankroll: started with 0 (was all-in), wins $300
        assert johnny.bankroll == expected_johnny_winnings, \
            f"Johnny should win $300 (main pot), got ${johnny.bankroll}"

        # PlayerA should get unmatched $215 back
        assert player_a.bankroll == player_a_before + expected_player_a_return, \
            f"PlayerA should get $215 back, has ${player_a.bankroll}"

    def test_side_pot_second_all_in_amount(self):
        """
        Test with two different all-in amounts:
        - Player A bets $300
        - Player B is all-in with $50
        - Player C is all-in with $150

        Main pot: $50 * 3 = $150 (B can win)
        Side pot 1: $100 * 2 = $200 (C can win, from A and C's extra $100 each)
        Side pot 2: $50 from A (returned, no one can match)
        """
        player_a = ScriptedPlayer("PlayerA", 400)
        player_b = ScriptedPlayer("PlayerB", 50)
        player_c = ScriptedPlayer("PlayerC", 150)

        players = [player_a, player_b, player_c]
        game = HoldemRound(players=players, blind=1)

        for p in players:
            p.start_holdem_round()

        # PlayerB all-in: $50
        player_b.add_chips(50)
        game.table.pot.append(50)
        game.table.bet_amount = 50

        # PlayerC all-in: $150
        player_c.add_chips(150)
        game.table.pot.append(150)
        game.table.bet_amount = 150

        # PlayerA bets $300
        player_a.add_chips(300)
        game.table.pot.append(300)
        game.table.bet_amount = 300

        # Give PlayerC the winning hand
        player_c._hole = [Card("A", "Spades"), Card("A", "Hearts")]
        player_b._hole = [Card("2", "Hearts"), Card("3", "Hearts")]
        player_a._hole = [Card("7", "Clubs"), Card("8", "Clubs")]

        game.table.flop = [Card("A", "Clubs"), Card("A", "Diamonds"), Card("10", "Spades")]
        game.table.turn = Card("2", "Clubs")
        game.table.river = Card("3", "Clubs")

        assert game.table.pot_total == 500

        game.showdown()
        game.settle_round()

        # PlayerC wins:
        # - Main pot: $50 * 3 = $150
        # - Side pot: $100 from each of A and C = $200
        # Total: $350
        expected_player_c_winnings = 350

        # PlayerA gets back unmatched: $300 - $150 = $150
        expected_player_a_return = 150

        assert player_c.bankroll == expected_player_c_winnings, \
            f"PlayerC should win $350, got ${player_c.bankroll}"

    def test_all_in_player_loses_only_loses_their_stake(self):
        """
        When all-in player loses, they only lose what they bet.
        - Player A bets $300 and wins
        - Player B was all-in with $100

        Player A should win $200 (the matched portion from B is $100, plus their own $100 back,
        and keep their unmatched $200).
        """
        player_a = ScriptedPlayer("PlayerA", 400)
        player_b = ScriptedPlayer("PlayerB", 100)

        players = [player_a, player_b]
        game = HoldemRound(players=players, blind=1)

        for p in players:
            p.start_holdem_round()

        # PlayerB all-in: $100
        player_b.add_chips(100)
        game.table.pot.append(100)
        game.table.bet_amount = 100

        # PlayerA bets $300
        player_a.add_chips(300)
        game.table.pot.append(300)
        game.table.bet_amount = 300

        # Give PlayerA the winning hand
        player_a._hole = [Card("A", "Spades"), Card("A", "Hearts")]
        player_b._hole = [Card("2", "Hearts"), Card("3", "Hearts")]

        game.table.flop = [Card("A", "Clubs"), Card("K", "Diamonds"), Card("10", "Spades")]
        game.table.turn = Card("2", "Clubs")
        game.table.river = Card("3", "Clubs")

        player_a_before = player_a.bankroll  # $100 left after betting $300

        game.showdown()
        game.settle_round()

        # PlayerA wins the main pot: $100 * 2 = $200
        # PlayerA gets back unmatched: $200
        # Total PlayerA should have: $100 (remaining) + $200 (main pot) + $200 (returned) = $500
        # But that's not right either... let me recalculate

        # PlayerA started with $400, bet $300, has $100 left
        # PlayerB started with $100, bet $100, has $0 left
        # Pot has $400
        # Main pot (that B can contest): $100 + $100 = $200
        # Unmatched from A: $200

        # PlayerA wins:
        # - Main pot: $200
        # - Gets back unmatched: $200
        # PlayerA ends with: $100 + $200 + $200 = $500? No...

        # Actually simpler:
        # PlayerA bet $300, B bet $100
        # A can only win $100 from B (what B put in)
        # A gets their own $300 back minus the $100 matched = $200 returned + $100 matched won
        # So A ends with: $100 (kept) + $200 (pot win) + $200 (returned)
        # That's $500 but A started with $400...

        # Let me think again:
        # A started $400, bet $300 -> $100 left in bankroll
        # B started $100, bet $100 -> $0 left in bankroll
        # Pot = $400
        #
        # A wins. A can win the whole pot they're eligible for.
        # A bet $300, B bet $100.
        # Main pot = $100 (from A) + $100 (from B) = $200
        # Side "pot" = $200 (from A, unmatched) - goes back to A
        #
        # A wins: $200 main pot
        # A returned: $200 unmatched
        # A total: $100 + $200 + $200 = $500

        # Wait, that means A ends with MORE than they started. Let's verify:
        # A: $400 -> bets $300 -> has $100 -> wins $200 main pot -> gets $200 back -> $500
        # B: $100 -> bets $100 -> has $0 -> loses -> $0
        #
        # Total money: started $500, ended $500. OK that's correct.

        # PlayerA should end with $500
        expected_player_a_total = 500

        assert player_a.bankroll == expected_player_a_total, \
            f"PlayerA should end with $500, got ${player_a.bankroll}"

        # PlayerB loses everything
        assert player_b.bankroll == 0, \
            f"PlayerB should have $0, got ${player_b.bankroll}"

    def test_unmatched_bet_returned_to_bettor(self):
        """
        When no one can match a bet, the unmatched portion must be returned.

        - Player A bets $500
        - Player B is all-in with $100
        - Player B wins

        Player B wins $200 (main pot: $100 from each)
        Player A gets back $400 (the unmatched portion)
        """
        player_a = ScriptedPlayer("PlayerA", 500)
        player_b = ScriptedPlayer("PlayerB", 100)

        players = [player_a, player_b]
        game = HoldemRound(players=players, blind=1)

        for p in players:
            p.start_holdem_round()

        # PlayerB all-in: $100
        player_b.add_chips(100)
        game.table.pot.append(100)
        game.table.bet_amount = 100

        # PlayerA bets $500
        player_a.add_chips(500)
        game.table.pot.append(500)
        game.table.bet_amount = 500

        # Give PlayerB the winning hand
        player_b._hole = [Card("A", "Spades"), Card("A", "Hearts")]
        player_a._hole = [Card("2", "Hearts"), Card("3", "Hearts")]

        game.table.flop = [Card("A", "Clubs"), Card("K", "Diamonds"), Card("10", "Spades")]
        game.table.turn = Card("5", "Clubs")
        game.table.river = Card("6", "Clubs")

        # Verify total pot
        assert game.table.pot_total == 600

        # PlayerA has $0 left after betting $500
        assert player_a.bankroll == 0

        game.showdown()
        game.settle_round()

        # PlayerB wins main pot: $100 + $100 = $200
        assert player_b.bankroll == 200, \
            f"PlayerB should win $200, got ${player_b.bankroll}"

        # PlayerA gets back unmatched: $500 - $100 = $400
        assert player_a.bankroll == 400, \
            f"PlayerA should get $400 back, got ${player_a.bankroll}"

        # Verify money conservation: started with $600, should end with $600
        total_after = player_a.bankroll + player_b.bankroll
        assert total_after == 600, f"Money not conserved: {total_after}"

    def test_side_pot_won_by_second_best_hand(self):
        """
        When all-in player wins main pot, side pot goes to next best hand.

        - Player A bets $300 (has worst hand)
        - Player B is all-in with $100 (has best hand - wins main pot)
        - Player C is all-in with $200 (has second best hand - wins side pot)

        Main pot: $100 * 3 = $300 -> Player B wins
        Side pot: ($200-$100) * 2 = $200 -> Player C wins (A and C contested)
        Unmatched: $300 - $200 = $100 -> returned to Player A
        """
        player_a = ScriptedPlayer("PlayerA", 400)
        player_b = ScriptedPlayer("PlayerB", 100)
        player_c = ScriptedPlayer("PlayerC", 200)

        # Track starting total for money conservation check
        starting_total = 400 + 100 + 200  # $700

        players = [player_a, player_b, player_c]
        game = HoldemRound(players=players, blind=1)

        for p in players:
            p.start_holdem_round()

        # PlayerB all-in: $100
        player_b.add_chips(100)
        game.table.pot.append(100)
        game.table.bet_amount = 100

        # PlayerC all-in: $200
        player_c.add_chips(200)
        game.table.pot.append(200)
        game.table.bet_amount = 200

        # PlayerA bets $300
        player_a.add_chips(300)
        game.table.pot.append(300)
        game.table.bet_amount = 300

        # PlayerB has best hand (Royal Flush)
        player_b._hole = [Card("A", "Spades"), Card("K", "Spades")]
        # PlayerC has second best hand (Four Aces)
        player_c._hole = [Card("A", "Hearts"), Card("A", "Diamonds")]
        # PlayerA has worst hand (pair of 2s)
        player_a._hole = [Card("2", "Hearts"), Card("2", "Diamonds")]

        game.table.flop = [Card("Q", "Spades"), Card("J", "Spades"), Card("10", "Spades")]
        game.table.turn = Card("A", "Clubs")
        game.table.river = Card("3", "Clubs")

        assert game.table.pot_total == 600

        # Record bankrolls before
        player_a_before = player_a.bankroll  # $100 left

        game.showdown()
        game.settle_round()

        # PlayerB wins main pot: $100 * 3 = $300
        assert player_b.bankroll == 300, \
            f"PlayerB should win main pot $300, got ${player_b.bankroll}"

        # PlayerC wins side pot: $100 * 2 = $200 (from A's and C's $100-$200 range)
        assert player_c.bankroll == 200, \
            f"PlayerC should win side pot $200, got ${player_c.bankroll}"

        # PlayerA gets back unmatched: $300 - $200 = $100
        expected_a = player_a_before + 100  # $100 + $100 = $200
        assert player_a.bankroll == expected_a, \
            f"PlayerA should have ${expected_a}, got ${player_a.bankroll}"

        # Verify money conservation (total bankrolls should equal starting total)
        total_after = player_a.bankroll + player_b.bankroll + player_c.bankroll
        assert total_after == starting_total, \
            f"Money not conserved: started with ${starting_total}, ended with ${total_after}"

    def test_three_way_all_in_different_amounts(self):
        """
        Complex scenario with three different all-in amounts and a larger bettor.

        - Player A bets $400
        - Player B is all-in with $50 (best hand)
        - Player C is all-in with $150 (second best)
        - Player D is all-in with $250 (third best)

        Main pot ($50 level): $50 * 4 = $200 -> B wins
        Side pot 1 ($150 level): $100 * 3 = $300 -> C wins
        Side pot 2 ($250 level): $100 * 2 = $200 -> D wins
        Unmatched: $400 - $250 = $150 -> returned to A
        """
        player_a = ScriptedPlayer("PlayerA", 500)
        player_b = ScriptedPlayer("PlayerB", 50)
        player_c = ScriptedPlayer("PlayerC", 150)
        player_d = ScriptedPlayer("PlayerD", 250)

        # Track starting total for money conservation check
        starting_total = 500 + 50 + 150 + 250  # $950

        players = [player_a, player_b, player_c, player_d]
        game = HoldemRound(players=players, blind=1)

        for p in players:
            p.start_holdem_round()

        # All players go all-in at their respective amounts
        player_b.add_chips(50)
        game.table.pot.append(50)

        player_c.add_chips(150)
        game.table.pot.append(150)

        player_d.add_chips(250)
        game.table.pot.append(250)

        player_a.add_chips(400)
        game.table.pot.append(400)
        game.table.bet_amount = 400

        # B has best hand (Royal Flush)
        player_b._hole = [Card("A", "Spades"), Card("K", "Spades")]
        # C has second best (Straight Flush, lower)
        player_c._hole = [Card("9", "Spades"), Card("8", "Spades")]
        # D has third best (Four of a kind)
        player_d._hole = [Card("A", "Hearts"), Card("A", "Diamonds")]
        # A has worst (pair)
        player_a._hole = [Card("2", "Hearts"), Card("2", "Diamonds")]

        game.table.flop = [Card("Q", "Spades"), Card("J", "Spades"), Card("10", "Spades")]
        game.table.turn = Card("A", "Clubs")
        game.table.river = Card("3", "Clubs")

        assert game.table.pot_total == 850

        player_a_before = player_a.bankroll  # $100 left

        game.showdown()
        game.settle_round()

        # B wins main pot: $50 * 4 = $200
        assert player_b.bankroll == 200, \
            f"PlayerB should win $200, got ${player_b.bankroll}"

        # C wins side pot 1: ($150-$50) * 3 = $100 * 3 = $300
        assert player_c.bankroll == 300, \
            f"PlayerC should win $300, got ${player_c.bankroll}"

        # D wins side pot 2: ($250-$150) * 2 = $100 * 2 = $200
        assert player_d.bankroll == 200, \
            f"PlayerD should win $200, got ${player_d.bankroll}"

        # A gets back unmatched: $400 - $250 = $150
        expected_a = player_a_before + 150
        assert player_a.bankroll == expected_a, \
            f"PlayerA should have ${expected_a}, got ${player_a.bankroll}"

        # Verify money conservation (total bankrolls should equal starting total)
        total_after = sum(p.bankroll for p in players)
        assert total_after == starting_total, \
            f"Money not conserved: started with ${starting_total}, ended with ${total_after}"
