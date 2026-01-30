"""FastAPI server for the poker web UI.

Run with: python -m web.server
"""
import logging
import threading
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from model.holdem_round import HoldemRound
from players.web_player import WebPlayer

# Import available player types
from players.callie_calls import Callie
from players.floyd_folds import Floyd
from players.paula_pairs import Paula
from players.ricky_raise import Ricky
from players.robby_random import Robby
from players.johnny_jacks import Johnny
from players.stuart_stats import Stuart

# Try to import LLM players (may not be available)
try:
    from players.claude import Claude
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from players.chad_gpt import Chad
    CHAD_AVAILABLE = True
except ImportError:
    CHAD_AVAILABLE = False


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Poker Web UI")

# Game state
game_lock = threading.Lock()
game_thread: Optional[threading.Thread] = None
current_game: Optional[HoldemRound] = None
web_player: Optional[WebPlayer] = None
all_players: list = []
game_over = False
game_results: Optional[dict] = None
action_history: list[dict[str, Any]] = []
round_count = 0

# Round pause state
round_complete = False
round_results: Optional[dict] = None
continue_event = threading.Event()


# Available player types
PLAYER_TYPES = {
    "callie": {"class": Callie, "name": "Callie Calls", "description": "Always calls"},
    "floyd": {"class": Floyd, "name": "Floyd Folds", "description": "Always folds"},
    "paula": {"class": Paula, "name": "Paula Pairs", "description": "Raises on pairs"},
    "ricky": {"class": Ricky, "name": "Ricky Raise", "description": "Raises randomly"},
    "robby": {"class": Robby, "name": "Robby Random", "description": "Plays randomly"},
    "johnny": {"class": Johnny, "name": "Johnny Jacks", "description": "Plays on jacks+"},
    "stuart": {"class": Stuart, "name": "Stuart Stats", "description": "Statistical player"},
}

if CLAUDE_AVAILABLE:
    PLAYER_TYPES["claude"] = {"class": Claude, "name": "Claude", "description": "Claude AI player"}

if CHAD_AVAILABLE:
    PLAYER_TYPES["chad"] = {"class": Chad, "name": "Chad GPT", "description": "GPT-based player"}


class StartGameRequest(BaseModel):
    opponents: list[str]  # List of player type keys
    starting_bankroll: int = 100


class ActionRequest(BaseModel):
    action: str  # FOLD, CALL, RAISE
    amount: Optional[int] = None


def card_to_dict(card) -> dict:
    """Convert a Card object to a dictionary."""
    if card is None:
        return None
    return {"rank": card.rank, "suit": card.suit}


def format_hand_description(desc) -> str:
    """Format a hand description tuple into a readable string."""
    if desc is None:
        return None
    if isinstance(desc, str):
        return desc

    # desc is a tuple like ("TWO_PAIR", ["5", "Q"]) or ("PAIR", "3", Card(...))
    hand_type = desc[0].replace("_", " ").title()

    if len(desc) == 1:
        return hand_type

    # Format the rest of the tuple
    details = desc[1:]
    detail_strs = []
    for d in details:
        if isinstance(d, list):
            detail_strs.append(" and ".join(str(x) for x in d))
        elif hasattr(d, 'rank'):  # Card object
            detail_strs.append(d.rank)
        elif isinstance(d, set):  # suits
            detail_strs.append(", ".join(d))
        else:
            detail_strs.append(str(d))

    if detail_strs:
        return f"{hand_type}: {', '.join(detail_strs)}"
    return hand_type


def run_game_loop():
    """Run the poker game in a background thread."""
    global current_game, game_over, game_results, action_history, round_count
    global round_complete, round_results

    logger.info("Starting game loop")

    try:
        # Create the game
        table = None
        round_number = 1

        while not game_over:
            # Check if any player is out of money
            active_players = [p for p in all_players if p.bankroll > 0]
            if len(active_players) < 2:
                logger.info("Game over - not enough players with money")
                game_over = True
                break

            # If web player is out of money, game over
            if web_player.bankroll <= 0:
                logger.info("Game over - you're out of money!")
                game_over = True
                game_results = {
                    "winner": None,
                    "message": "You're out of money!",
                    "final_bankrolls": {p.name: p.bankroll for p in all_players}
                }
                break

            logger.info(f"Starting round {round_number}")
            round_count = round_number

            # Clear action history for new round
            action_history = []

            # Create a new round
            current_game = HoldemRound(
                players=active_players,
                blind=1,
                table=table,
                round_number=round_number
            )

            # Monkey-patch the betting round to capture actions
            # Must patch in holdem_round's namespace since it imports BettingRound directly
            import model.holdem_round
            from model.betting_round import BettingRound as OriginalBettingRound

            class TrackedBettingRound(OriginalBettingRound):
                def handle_action(self, action, active_player):
                    # Record action in history with chat message if available
                    message = getattr(active_player, 'last_message', None)
                    action_history.append({
                        "player": active_player.name,
                        "action": action.action_type,
                        "amount": action.amount,
                        "all_in": action.all_in,
                        "message": message
                    })
                    # Clear the message after capturing it
                    if hasattr(active_player, 'last_message'):
                        active_player.last_message = None
                    return super().handle_action(action, active_player)

            # Apply the patch to holdem_round's namespace
            model.holdem_round.BettingRound = TrackedBettingRound

            # Run the round
            try:
                players_result, table = current_game.play()
                table = current_game.table

                # Build round results with all player hands
                player_hands = []
                for p in active_players:
                    hand_info = {
                        "name": p.name,
                        "cards": [card_to_dict(c) for c in p._hole] if p._hole else [],
                        "folded": p.folded,
                        "is_you": p == web_player,
                    }
                    # Add best hand description if they didn't fold
                    if not p.folded and hasattr(current_game, 'results') and current_game.results:
                        all_hands = current_game.results.get("all_hands", {})
                        if p.name in all_hands:
                            hand_info["best_hand"] = format_hand_description(all_hands[p.name].describe())
                    player_hands.append(hand_info)

                # Store round results
                winning_hand = None
                if current_game.results and current_game.results.get("winning_hand"):
                    winning_hand = format_hand_description(current_game.results["winning_hand"].describe())

                round_results = {
                    "round_number": round_number,
                    "winners": current_game.results.get("winners", []) if current_game.results else [],
                    "winning_hand": winning_hand,
                    "pot_size": current_game.results.get("pot_size", 0) if current_game.results else 0,
                    "player_hands": player_hands,
                    "community_cards": [],
                }

                # Add community cards
                if current_game.table.flop is not None:
                    round_results["community_cards"].extend([card_to_dict(c) for c in current_game.table.flop])
                if current_game.table.turn is not None:
                    round_results["community_cards"].append(card_to_dict(current_game.table.turn))
                if current_game.table.river is not None:
                    round_results["community_cards"].append(card_to_dict(current_game.table.river))

                # Signal that round is complete and wait for user to continue
                round_complete = True
                continue_event.clear()

                logger.info("Round complete, waiting for user to continue...")

                # Wait for user to click continue (check periodically for game_over)
                while not continue_event.is_set() and not game_over:
                    continue_event.wait(timeout=0.5)

                round_complete = False
                round_results = None

                if game_over:
                    break

            except Exception as e:
                logger.error(f"Error in game round: {e}")
                import traceback
                traceback.print_exc()
                game_over = True
                game_results = {"error": str(e)}
                break

            round_number += 1

    except Exception as e:
        logger.error(f"Game loop error: {e}")
        import traceback
        traceback.print_exc()
        game_over = True
        game_results = {"error": str(e)}


@app.get("/game/players")
def get_available_players():
    """List available player types."""
    return {
        key: {"name": info["name"], "description": info["description"]}
        for key, info in PLAYER_TYPES.items()
    }


@app.post("/game/start")
def start_game(request: StartGameRequest):
    """Start a new game with the specified opponents."""
    global game_thread, web_player, all_players, game_over, game_results, action_history, round_count
    global round_complete, round_results

    with game_lock:
        # Check if game is already running
        if game_thread is not None and game_thread.is_alive():
            raise HTTPException(status_code=400, detail="Game already in progress")

        # Reset state
        game_over = False
        game_results = None
        action_history = []
        round_count = 0
        round_complete = False
        round_results = None
        continue_event.clear()

        # Create web player (the human)
        web_player = WebPlayer("You", request.starting_bankroll)

        # Create opponent players
        opponents = []
        for i, opponent_type in enumerate(request.opponents):
            if opponent_type not in PLAYER_TYPES:
                raise HTTPException(status_code=400, detail=f"Unknown player type: {opponent_type}")

            player_info = PLAYER_TYPES[opponent_type]
            player_class = player_info["class"]
            player_name = f"{player_info['name']}"
            if i > 0:
                player_name = f"{player_info['name']} {i+1}"

            opponents.append(player_class(player_name, request.starting_bankroll))

        # Combine all players (web player first for easier tracking)
        all_players = [web_player] + opponents

        # Start game thread
        game_thread = threading.Thread(target=run_game_loop, daemon=True)
        game_thread.start()

        return {
            "status": "started",
            "players": [p.name for p in all_players],
            "starting_bankroll": request.starting_bankroll
        }


@app.get("/game/state")
def get_game_state():
    """Get the current game state."""
    global web_player, all_players, current_game, game_over, game_results, round_count
    global round_complete, round_results

    if web_player is None:
        return {"phase": "lobby", "game_started": False}

    # Get base state from web player
    state = web_player.get_state()

    # Override community cards with live data from game table
    # (WebPlayer's cached table may be stale between betting rounds)
    # Note: Card inherits from dict but stores data as attributes, so empty Card
    # is falsy. Must use "is not None" checks instead of truthiness.
    if current_game and current_game.table:
        table = current_game.table
        community_cards = []
        if table.flop is not None:
            community_cards.extend([card_to_dict(c) for c in table.flop])
        if table.turn is not None:
            community_cards.append(card_to_dict(table.turn))
        if table.river is not None:
            community_cards.append(card_to_dict(table.river))
        state["community_cards"] = community_cards

        # Also update phase based on live table
        if table.river is not None:
            state["phase"] = "river"
        elif table.turn is not None:
            state["phase"] = "turn"
        elif table.flop is not None:
            state["phase"] = "flop"
        else:
            state["phase"] = "preflop"

        # Update pot and bet from live table
        state["pot"] = table.pot_total
        state["current_bet"] = table.bet_amount

    # Add additional info
    state["game_started"] = True
    state["game_over"] = game_over
    state["round_number"] = round_count

    # Add round complete state
    state["round_complete"] = round_complete
    if round_complete and round_results:
        state["round_results"] = round_results

    if game_results:
        state["results"] = game_results

    # Add player info
    if all_players:
        players_info = []
        for i, p in enumerate(all_players):
            player_info = {
                "name": p.name,
                "bankroll": p.bankroll,
                "folded": p.folded if hasattr(p, 'folded') else False,
                "is_dealer": current_game.table.dealer_button_index == i if current_game else False,
                "is_you": p == web_player,
                "money_on_table": p.status.money_on_table if hasattr(p, 'status') and p.status else 0,
            }
            players_info.append(player_info)
        state["players"] = players_info

    # Add action history
    state["history"] = action_history[-20:]  # Last 20 actions

    return state


@app.post("/game/action")
def submit_action(request: ActionRequest):
    """Submit a player action."""
    global web_player

    if web_player is None:
        raise HTTPException(status_code=400, detail="No game in progress")

    if not web_player.is_waiting():
        raise HTTPException(status_code=400, detail="Not your turn")

    # Submit the action
    web_player.submit_action({
        "action": request.action,
        "amount": request.amount
    })

    return {"status": "action_submitted", "action": request.action}


@app.get("/game/history")
def get_history():
    """Get the action history for the current round."""
    return {"history": action_history}


@app.post("/game/continue")
def continue_game():
    """Continue to the next round after viewing results."""
    global round_complete

    if not round_complete:
        raise HTTPException(status_code=400, detail="No round waiting for continuation")

    continue_event.set()
    return {"status": "continuing"}


@app.post("/game/stop")
def stop_game():
    """Stop the current game."""
    global game_over, game_thread, web_player, round_complete

    with game_lock:
        game_over = True
        round_complete = False

        # Signal continue event to unblock game loop if waiting
        continue_event.set()

        # If web player is waiting, send a fold to unblock
        if web_player and web_player.is_waiting():
            web_player.submit_action({"action": "FOLD"})

        return {"status": "stopped"}


# Serve static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
def root():
    """Serve the main page."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Poker Web UI - static files not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
