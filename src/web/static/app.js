// Poker Web UI JavaScript

const API_BASE = '';
let selectedOpponents = [];
let gameStarted = false;
let pollInterval = null;
let lastHistoryLength = 0;
let showingRoundResults = false;

// Card suit symbols and colors
const SUIT_SYMBOLS = {
    'Hearts': { symbol: '\u2665', color: 'red' },
    'Diamonds': { symbol: '\u2666', color: 'red' },
    'Clubs': { symbol: '\u2663', color: 'black' },
    'Spades': { symbol: '\u2660', color: 'black' }
};

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadAvailablePlayers();
    setupEventListeners();
});

async function loadAvailablePlayers() {
    try {
        const response = await fetch(`${API_BASE}/game/players`);
        const players = await response.json();

        const container = document.getElementById('opponent-list');
        container.innerHTML = '';

        for (const [key, info] of Object.entries(players)) {
            const div = document.createElement('div');
            div.className = 'opponent-option';
            div.dataset.key = key;
            div.innerHTML = `
                <strong>${info.name}</strong>
                <span class="description">${info.description}</span>
            `;
            div.addEventListener('click', () => toggleOpponent(key, info.name));
            container.appendChild(div);
        }
    } catch (error) {
        console.error('Failed to load players:', error);
    }
}

function toggleOpponent(key, name) {
    const index = selectedOpponents.findIndex(o => o.key === key);

    if (index >= 0) {
        selectedOpponents.splice(index, 1);
    } else {
        selectedOpponents.push({ key, name });
    }

    updateSelectedDisplay();
}

function updateSelectedDisplay() {
    // Update count
    document.getElementById('selected-count').textContent = selectedOpponents.length;

    // Update list
    const list = document.getElementById('selected-list');
    list.innerHTML = selectedOpponents.map(o =>
        `<span class="selected-chip">${o.name}</span>`
    ).join('');

    // Update button state
    document.getElementById('start-game-btn').disabled = selectedOpponents.length === 0;

    // Update visual selection
    document.querySelectorAll('.opponent-option').forEach(el => {
        const isSelected = selectedOpponents.some(o => o.key === el.dataset.key);
        el.classList.toggle('selected', isSelected);
    });
}

function setupEventListeners() {
    document.getElementById('start-game-btn').addEventListener('click', startGame);
    document.getElementById('fold-btn').addEventListener('click', () => submitAction('FOLD'));
    document.getElementById('call-btn').addEventListener('click', () => submitAction('CALL'));
    document.getElementById('raise-btn').addEventListener('click', () => {
        const amount = parseInt(document.getElementById('raise-amount').value);
        submitAction('RAISE', amount);
    });
    document.getElementById('continue-btn').addEventListener('click', hideResultsModal);
    document.getElementById('new-game-btn').addEventListener('click', returnToLobby);
}

async function startGame() {
    const bankroll = parseInt(document.getElementById('starting-bankroll').value) || 100;
    const opponents = selectedOpponents.map(o => o.key);

    try {
        const response = await fetch(`${API_BASE}/game/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                opponents: opponents,
                starting_bankroll: bankroll
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Failed to start game: ${error.detail}`);
            return;
        }

        gameStarted = true;
        document.getElementById('lobby').classList.add('hidden');
        document.getElementById('game').classList.remove('hidden');

        // Start polling for game state
        startPolling();

    } catch (error) {
        console.error('Failed to start game:', error);
        alert('Failed to start game');
    }
}

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(updateGameState, 500);
    updateGameState(); // Initial update
}

async function updateGameState() {
    try {
        const response = await fetch(`${API_BASE}/game/state`);
        const state = await response.json();

        if (state.phase === 'lobby' || !state.game_started) {
            return;
        }

        renderGameState(state);

    } catch (error) {
        console.error('Failed to get game state:', error);
    }
}

function renderGameState(state) {
    // Check if round is complete and we need to show results
    if (state.round_complete && state.round_results && !showingRoundResults) {
        showRoundResultsModal(state.round_results);
        return;
    }

    // Update pot
    document.getElementById('pot-amount').textContent = state.pot || 0;

    // Update status
    const statusText = document.getElementById('status-text');
    if (state.game_over) {
        statusText.textContent = 'Game Over!';
        showGameOverModal(state);
    } else if (state.your_turn) {
        statusText.textContent = 'Your turn!';
    } else {
        statusText.textContent = `Phase: ${state.phase || 'Waiting'} - Round ${state.round_number || 1}`;
    }

    // Render community cards
    renderCommunityCards(state.community_cards || []);

    // Render your cards
    renderYourCards(state.your_cards || []);

    // Update your info
    document.getElementById('your-bankroll').textContent = state.your_bankroll || 0;
    document.getElementById('your-table-money').textContent = state.your_money_on_table || 0;

    // Render players
    renderPlayers(state.players || []);

    // Show/hide action buttons
    const actionArea = document.getElementById('action-area');
    if (state.your_turn && !state.game_over) {
        actionArea.classList.remove('hidden');
        document.getElementById('current-bet').textContent = state.current_bet || 0;

        const toCall = Math.max(0, (state.current_bet || 0) - (state.your_money_on_table || 0));
        document.getElementById('to-call').textContent = toCall;

        // Set raise input defaults
        const raiseInput = document.getElementById('raise-amount');
        raiseInput.min = (state.current_bet || 0) + 1;
        raiseInput.max = state.your_max_bet || 100;
        if (!raiseInput.value || parseInt(raiseInput.value) < raiseInput.min) {
            raiseInput.value = Math.min((state.current_bet || 0) * 2, state.your_max_bet || 100);
        }

        // Update call button text
        const callBtn = document.getElementById('call-btn');
        if (toCall === 0) {
            callBtn.textContent = 'Check';
        } else if (toCall >= (state.your_bankroll || 0)) {
            callBtn.textContent = `All In ($${state.your_bankroll})`;
        } else {
            callBtn.textContent = `Call $${toCall}`;
        }
    } else {
        actionArea.classList.add('hidden');
    }

    // Render history and chat
    renderHistory(state.history || []);
    renderChat(state.history || []);

    lastHistoryLength = (state.history || []).length;
}

function renderCommunityCards(cards) {
    const container = document.getElementById('community-cards');
    container.innerHTML = '';

    // Show 5 card slots
    for (let i = 0; i < 5; i++) {
        const card = cards[i];
        if (card) {
            container.appendChild(createCardElement(card));
        } else {
            const placeholder = document.createElement('div');
            placeholder.className = 'card card-placeholder';
            container.appendChild(placeholder);
        }
    }
}

function renderYourCards(cards) {
    const container = document.getElementById('your-cards');
    container.innerHTML = '';

    if (cards.length === 0) {
        // Show placeholders
        for (let i = 0; i < 2; i++) {
            const placeholder = document.createElement('div');
            placeholder.className = 'card card-placeholder';
            container.appendChild(placeholder);
        }
    } else {
        cards.forEach(card => {
            container.appendChild(createCardElement(card));
        });
    }
}

function createCardElement(card) {
    const div = document.createElement('div');
    const suitInfo = SUIT_SYMBOLS[card.suit] || { symbol: '?', color: 'black' };

    div.className = `card card-${suitInfo.color}`;
    div.innerHTML = `
        <span class="card-rank">${card.rank}</span>
        <span class="card-suit">${suitInfo.symbol}</span>
    `;
    return div;
}

function renderPlayers(players) {
    const container = document.getElementById('players-area');
    container.innerHTML = '';

    // Filter out "You" - shown separately
    const opponents = players.filter(p => !p.is_you);

    opponents.forEach((player, index) => {
        const div = document.createElement('div');
        div.className = `player-seat ${player.folded ? 'folded' : ''}`;
        div.innerHTML = `
            <div class="player-name">
                ${player.name}
                ${player.is_dealer ? '<span class="dealer-chip">D</span>' : ''}
            </div>
            <div class="player-bankroll">$${player.bankroll}</div>
            ${player.money_on_table > 0 ? `<div class="player-bet">Bet: $${player.money_on_table}</div>` : ''}
            ${player.folded ? '<div class="player-status">Folded</div>' : ''}
        `;
        container.appendChild(div);
    });
}

function renderHistory(history) {
    const container = document.getElementById('history-list');

    // Show last 10 actions
    const recent = history.slice(-10);
    container.innerHTML = recent.map(action => {
        let text = `<strong>${action.player}</strong>: ${action.action}`;
        if (action.amount && action.action !== 'FOLD') {
            text += ` $${action.amount}`;
        }
        if (action.all_in) {
            text += ' (All In!)';
        }
        return `<div class="history-item">${text}</div>`;
    }).join('');

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function renderChat(history) {
    const container = document.getElementById('chat-list');

    // Filter to only actions with messages
    const messagesOnly = history.filter(action => action.message);
    const recent = messagesOnly.slice(-15);

    container.innerHTML = recent.map(action => {
        return `<div class="chat-message">
            <span class="chat-player">${action.player}:</span>
            <span class="chat-text">${action.message}</span>
        </div>`;
    }).join('');

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function submitAction(action, amount = null) {
    try {
        const body = { action };
        if (amount !== null) {
            body.amount = amount;
        }

        const response = await fetch(`${API_BASE}/game/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        if (!response.ok) {
            const error = await response.json();
            alert(`Action failed: ${error.detail}`);
        }

    } catch (error) {
        console.error('Failed to submit action:', error);
    }
}

function showGameOverModal(state) {
    const modal = document.getElementById('game-over-modal');
    const content = document.getElementById('game-over-content');

    let html = '';
    if (state.results) {
        if (state.results.message) {
            html += `<p>${state.results.message}</p>`;
        }
        if (state.results.final_bankrolls) {
            html += '<h3>Final Bankrolls</h3><ul>';
            for (const [name, amount] of Object.entries(state.results.final_bankrolls)) {
                html += `<li>${name}: $${amount}</li>`;
            }
            html += '</ul>';
        }
    }

    content.innerHTML = html || '<p>Thanks for playing!</p>';
    modal.classList.remove('hidden');

    // Stop polling
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

function showRoundResultsModal(results) {
    showingRoundResults = true;

    const modal = document.getElementById('results-modal');
    const content = document.getElementById('results-content');
    const handsContainer = document.getElementById('results-hands');

    // Set round number
    document.getElementById('results-round-number').textContent = results.round_number || '?';

    // Build winner info
    let html = '';
    if (results.winners && results.winners.length > 0) {
        const winnerNames = results.winners.join(', ');
        html += `<p class="winner-announcement"><strong>${winnerNames}</strong> wins $${results.pot_size}!</p>`;
        if (results.winning_hand) {
            html += `<p class="winning-hand">Winning hand: <strong>${results.winning_hand}</strong></p>`;
        }
    }

    // Build community cards display
    if (results.community_cards && results.community_cards.length > 0) {
        html += '<div class="results-community"><h4>Community Cards</h4><div class="cards-row">';
        results.community_cards.forEach(card => {
            const suitInfo = SUIT_SYMBOLS[card.suit] || { symbol: '?', color: 'black' };
            html += `<div class="card card-small card-${suitInfo.color}">
                <span class="card-rank">${card.rank}</span>
                <span class="card-suit">${suitInfo.symbol}</span>
            </div>`;
        });
        html += '</div></div>';
    }

    content.innerHTML = html;

    // Build player hands display
    let handsHtml = '<h4>All Hands</h4><div class="player-hands-grid">';

    results.player_hands.forEach(player => {
        const isWinner = results.winners && results.winners.includes(player.name);

        handsHtml += `<div class="player-hand-result ${isWinner ? 'winner' : ''} ${player.folded ? 'folded' : ''}">`;
        handsHtml += `<div class="player-hand-name">${player.name}${player.is_you ? ' (You)' : ''}${isWinner ? ' - WINNER' : ''}</div>`;

        if (player.folded) {
            handsHtml += '<div class="player-hand-status">Folded</div>';
        } else if (player.cards && player.cards.length > 0) {
            handsHtml += '<div class="cards-row">';
            player.cards.forEach(card => {
                const suitInfo = SUIT_SYMBOLS[card.suit] || { symbol: '?', color: 'black' };
                handsHtml += `<div class="card card-small card-${suitInfo.color}">
                    <span class="card-rank">${card.rank}</span>
                    <span class="card-suit">${suitInfo.symbol}</span>
                </div>`;
            });
            handsHtml += '</div>';
            if (player.best_hand) {
                handsHtml += `<div class="player-best-hand">${player.best_hand}</div>`;
            }
        }

        handsHtml += '</div>';
    });

    handsHtml += '</div>';
    handsContainer.innerHTML = handsHtml;

    modal.classList.remove('hidden');
}

async function hideResultsModal() {
    document.getElementById('results-modal').classList.add('hidden');
    showingRoundResults = false;

    // Tell server to continue to next round
    try {
        await fetch(`${API_BASE}/game/continue`, { method: 'POST' });
    } catch (error) {
        console.error('Failed to continue game:', error);
    }
}

function returnToLobby() {
    // Stop game
    fetch(`${API_BASE}/game/stop`, { method: 'POST' });

    // Reset state
    gameStarted = false;
    selectedOpponents = [];
    lastHistoryLength = 0;

    // Show lobby
    document.getElementById('game').classList.add('hidden');
    document.getElementById('lobby').classList.remove('hidden');
    document.getElementById('game-over-modal').classList.add('hidden');

    // Reset selections
    updateSelectedDisplay();
}
