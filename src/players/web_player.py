"""Web-controllable human player for the poker web UI.

This player uses a queue to receive actions from the web API and exposes
game state for the API to read.
"""
import logging
import queue
import threading
from typing import Any, Optional

from model.player import Player
from model.action import Action, FOLD, CALL, RAISE


class WebPlayer(Player):
    """A player controlled via web API using a thread-safe queue."""

    persona = "Human (Web)"

    def __init__(self, name: str, bankroll: int):
        super().__init__(name, bankroll)
        self.action_queue: queue.Queue = queue.Queue()
        self.waiting_for_action = threading.Event()
        self._current_table = None
        self._current_player_status = None
        self._current_is_called = False
        self._round_number = None
        self._action_history: list[dict[str, Any]] = []

    def start_holdem_round(self):
        """Reset state for a new round."""
        super().start_holdem_round()
        self._action_history = []
        # Clear any pending actions from previous round
        while not self.action_queue.empty():
            try:
                self.action_queue.get_nowait()
            except queue.Empty:
                break

    def play(self, table, player_status, is_called: bool = False, round_number: Optional[int] = None) -> Action:
        """Wait for an action from the web UI.

        This method blocks until an action is submitted via submit_action().
        """
        # Store current state for API access
        self._current_table = table
        self._current_player_status = player_status
        self._current_is_called = is_called
        self._round_number = round_number

        logging.debug(f"{self.name} waiting for action from web UI")

        # Signal that we're waiting for input
        self.waiting_for_action.set()

        try:
            # Block until we receive an action (with timeout to allow checking for game end)
            while True:
                try:
                    action_data = self.action_queue.get(timeout=0.5)
                    break
                except queue.Empty:
                    # Keep waiting - allows periodic checking
                    continue

            # Parse the action
            action = self._parse_action(action_data, table)

            # Record in history
            self._record_action(action)

            logging.debug(f"{self.name} received action: {action}")
            return action

        finally:
            self.waiting_for_action.clear()

    def _parse_action(self, action_data: dict, table) -> Action:
        """Convert API action data to an Action object."""
        action_type = action_data.get("action", "FOLD").upper()
        amount = action_data.get("amount")

        if action_type == "FOLD":
            return self.fold()
        elif action_type == "CALL":
            return self.call(table)
        elif action_type == "RAISE":
            if amount is None:
                # Default to min raise (double current bet)
                amount = min(table.bet_amount * 2, self.max_bet)
            return self._raise(table, amount)
        else:
            # Default to fold on unrecognized action
            logging.warning(f"Unrecognized action type: {action_type}, defaulting to FOLD")
            return self.fold()

    def _record_action(self, action: Action):
        """Record an action in the history."""
        self._action_history.append({
            "player": self.name,
            "action": action.action_type,
            "amount": action.amount,
            "all_in": action.all_in
        })

    def submit_action(self, action_data: dict):
        """Submit an action from the web API.

        Args:
            action_data: Dict with 'action' (FOLD/CALL/RAISE) and optional 'amount'
        """
        self.action_queue.put(action_data)

    def is_waiting(self) -> bool:
        """Check if this player is waiting for an action."""
        return self.waiting_for_action.is_set()

    def get_state(self) -> dict[str, Any]:
        """Get the current game state visible to this player."""
        table = self._current_table

        if table is None:
            return {"phase": "waiting", "your_turn": False}

        # Determine game phase
        if table.river is not None:
            phase = "river"
        elif table.turn is not None:
            phase = "turn"
        elif table.flop is not None:
            phase = "flop"
        else:
            phase = "preflop"

        # Convert cards to serializable format
        def card_to_dict(card):
            if card is None:
                return None
            return {"rank": card.rank, "suit": card.suit}

        your_cards = [card_to_dict(c) for c in self._hole] if self._hole else []

        # Note: Card inherits from dict but stores data as attributes, so empty
        # Card is falsy. Must use "is not None" checks instead of truthiness.
        community_cards = []
        if table.flop is not None:
            community_cards.extend([card_to_dict(c) for c in table.flop])
        if table.turn is not None:
            community_cards.append(card_to_dict(table.turn))
        if table.river is not None:
            community_cards.append(card_to_dict(table.river))

        return {
            "phase": phase,
            "your_turn": self.is_waiting(),
            "your_cards": your_cards,
            "community_cards": community_cards,
            "pot": table.pot_total,
            "current_bet": table.bet_amount,
            "your_bankroll": self.bankroll,
            "your_money_on_table": self.status.money_on_table if hasattr(self, 'status') else 0,
            "your_max_bet": self.max_bet,
            "big_blind": table.big_blind,
            "small_blind": table.small_blind,
        }

    @property
    def action_history(self) -> list[dict[str, Any]]:
        """Get the action history for the current round."""
        return self._action_history.copy()
