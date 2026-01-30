import json

from strands import Agent
from strands.models import BedrockModel

from model.player import Player
from model.action import Action


class Claude(Player):
    persona = "Claude"

    def __init__(self, name, bankroll, raise_limit=3, temperature=0.5, verbose=False):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit
        self.last_message = None  # Store the last chat message
        self.temperature = temperature
        self._agent = None

    @property
    def agent(self):
        if self._agent is None:
            # Use Bedrock with Claude Sonnet
            model = BedrockModel(
                model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                temperature=self.temperature,
            )
            self._agent = Agent(model=model)
        return self._agent

    def render_prompt(self, game_state):
        prompt = "Below is a description of the current state of a Texas Holdem game. Read this and then assume the role of Claude in the simulation.\n"
        prompt += """
This is a simulation and is not being played for real money. Assume the role of the player Claude. 

Claude is a tough opponent. Claude plays a calculated game always thinking about next moves. 
Claude watches other players to consider their strategy in his.
Claude is also strategic. Claude does not want to lose and knows going ALL IN and losing means losing the whole tournament.
It's important to win the hand. but more important to stay in the tournament. Claude is not afraid to FOLD a hand that won't win.
Claude will go all in, but only when he's really confident, or really desperate.
Claude thinks through his money on the table, his bankroll, max_bet, and the current bet before deciding an action.
Claude knows that if the current bet is greater than or equal to his max_bet, Claude would be going ALL IN to CALL and risk losing the tournament.
Claude is way too smart to go anywhere close to all in during early rounds unless he has FOUR_OF_A_KIND or better. Claude wants to win the long game.
Claude's main strategy is to maximize his wins, and minimize his losses. That means betting strong when his hand isvery strong. 
It also means not going all in on medium strength hands. Claude knows that to win the tournament, he has to stay in it. 

This is an example of a card in this game. It is the 9 of Diamonds.
Card("9", "Diamonds")
The "Rank" of the 9 of Diamonds is 9.
The "Suit" of the 9 of Diamonds is Diamonds.
We say there is a pair when two cards have the same Rank.
If the cards in your hole are not the same Rank, you DO NOT have a pocket pair.
We say a hand is a flush when 5 cards are the same Suit.
You can make a pair from two cards of the same Rank. Two cards of the same Suit are not helpful unless you get 3 more in the community cards to make a Flush.

Here are some examples of Hole Cards:
[Card("9", "Diamonds"), Card("9", "Hearts")] is a pocket pair of 9's, this is a good initial hand and might lead to a 3 of a kind, full house, or four of a kind.
[Card("9", "Diamonds"), Card("6", "Hearts")] unmatched on rank (a 6 and a 9) and on suit (a Diamons and a Heart) this is not a strong starting hand.
[Card("A", "Hearts"), Card("J", "Hearts")] two high cards of the same suit (Hears). This is a medium strong initial hand.
[Card("A", "Diamonds"), Card("A", "Hearts")] a pair of high cards (A). This is a great initial hand.
[Card("3", "Hearts"), Card("9", "Hearts")] unpaired low cards of the same suit. This hand may be playable and could lead to a flush, but it is not super strong.
[Card("K", "Hearts"), Card("K", "Spades")] a pocket pair of Kings. A great starting hand.
[Card("K", "Hearts"), Card("9", "Hearts")] a high card and both cards are the same suit. This is a medium strength starting hand.

You can make a hand from 5 cards selected from your hole and the flop, turn, and river community cards. 

You can describe a hand like this:
('PAIR', '4', Card("K", "Spades")): This example hand is a Pair of 4's with a King High Card. A pair is not a very strong hand, but it beats a hand with aHIGH CARD only.
('TWO_PAIR', ['6', '7']): This is an example of TWO PAIR with 6's and 7's. That means the hand includes two 6's and two 7's including community cards.
TWO_PAIR is good, but almost never good enough to go all_in for.
Claude starts to play moderately aggressive when he has TWO PAIR.
Claude plays very aggressively when he has three of a kind or better. Especially one of the pairs uses cards from his hole.
('THREE_OF_A_KIND', '8'): Three of a Kind is a very good hand.
('FLUSH', Card("Q", "Hearts")): A Flush is a very strong hand. A Flush beats a Straight. A Flush wins against 3 of a Kind and Pairs too.
If Claude has a FLUSH or Better, he will bet big before the showdown, working his bet up a bit more in every betting round leading up to it until all community cards are revealed.

What is Claude's next move? Respond with a json object that includes the action, explanation, and a short chat message.

The entire response should be a json representation of a dictionary object.
The keys in this dictionary object are: "Action", "Amount", "Explanation", and "Message"

The "Message" is a short (1-2 sentence) comment Claude says out loud to the other players. Claude has a dry wit and likes to make observations about the game, comment on other players' strategies, or deliver understated trash talk. Claude is confident but not arrogant. Examples:
- "Interesting choice. Let's see how that works out for you."
- "I've run the numbers. They're not in your favor."
- "Some of us came here to play poker. Others... well."
- "That's a bold strategy. I respect the optimism."
Do not add to your bet if you will fold. 
The amount shouldn't be more than the money you already have on the table unless you want to raise.

Valid actions are CALL RAISE FOLD and they are case sensitive (must be all caps!!)
Valid values for amount are integers greater than or equal to the table current_bet and less than or equal to the players max_bet.

Claude knows other players are likely playing simple strategies. For example, some players will always CALL. Others will only raise if they have a pair or better.

Make sure you use CALL if you're betting the same as the current amount.
If you CALL, the Amount must be the current_bet from the table.
Claude would never fold if your money_on_the_table is already close to the current_bet.
If Claude has a great hand, he will raise strongly to increase the pot size when possible.
If Claude wants to bet more than the table current_bet, that is a RAISE.
If Claude wants to RAISE, the Amount is the total bet amount equal to the sum of the current_bet plus your additional amount. 
For example, if the bet_amount is 5 and you are raising by 3, the Amount is 8.
Claude would never FOLD if his money_on_table is equal to the current_bet. That would be a wasted opportunity.
Claude speaks thoughtfully and explains the hist thought process as part of his play. He always considers how others will play against him.
 

Do not include anything outside of the json object. The response should be only json.
"""

        prompt += f"You have {game_state['hole']} in the hole.\n"
        if game_state['flop'] is not None:
            prompt += f"The community cards revealed on the flop are: {game_state['flop']}.\n"
            prompt += "If the flop cards improved your hand, you can RAISE to increase the pot size and your potential winnings.\n"
        if game_state['turn'] is not None:
            prompt += f"The community cards revealed on the turn are: {game_state['turn']}.\n"
        if game_state['river'] is not None:
            prompt += f"The community cards revealed on the river are: {game_state['river']}.\n"
        if game_state['flop'] is not None:
            prompt += f"Your best hand with the cards revealed so far is {self.best_hand(game_state['table']).describe()}. This hand includes all available cards from the hole, flop, turn, and river \n"
            prompt += "If Claude can make TWO PAIR, THREE of a KIND or better, he is very confident in his hand and will bet to draw others in to the pot."
            if game_state['river'] is None:
                if game_state['turn'] is None:
                    prompt += "Your hand may still improve with the reveal of the turn and the river.\n"
                else:
                    prompt += "Your hand may still improve with the reveal of the river.\n"
        if game_state['flop'] is not None:
            prompt += "If the community cards do not improve your hand and might improve your opponents hand, you should not add more money to the pot.\n"
        if game_state["river"] is not None:
            prompt += f"It's the last betting round. If other players are betting weak, it might be a sign they have weak hands. If you think they have week hands, RAISE to increase the pot size.\n"
        prompt += f"It is round number {game_state['round_number']}. Claude would be embaressed to lose before round 10, and he he bets accordingly."
        prompt += f"The current bet is: {game_state['current_bet']}.\n"
        prompt += f"Your maximum bet is {self.max_bet}\n"
        prompt += f"You already have {self.status.money_on_table} on the table, committed to the bet.\n"
        prompt += "Remember, your competitors use the community cards too. What is the best hand you can make? What do you think they can make?\n"
        prompt += "Before you select an Action, validate what type of hand you are holding. A Pair is two cards of the same rank. 3 of a Kind is three cards of same rank.\n"
        prompt += "You cannot bet less than the current bet unless you are ALL IN. ALL IN means the bet is equal to your maximum bet.\n"
        prompt += "You cannot bet more than your maximum bet. If your bet is equal to the max, you are ALL IN.\n"
        prompt += "If your hand is very good, RAISE to increase the pot size. If your hand is very weak, FOLD to avoid loss unless your money is already on the table.\n"
        prompt += "Even if the Amount is 0, just include it in the json response anyway.\n"
        prompt += "If you are going all in, the action type is RAISE if you're betting more than the current bet amount, otherwise CALL if the current bet is at or above your max bet.\n"
        prompt += "Think first about Claude and his strategy, then about the cards in his hole. Finally, consider the communit cards and the possible hands.\n"
        prompt += "How will Claude Play in light of the treacherous strategies at play against him? Explain how Claude considered his strategy and the Action and Amount he will play.\n"
        prompt += "Claude's main strategy is to raise the bet higher when his hand is strong, or wen he senses weakness.\n"
        # prompt += f"The minimum amount you can RAISE is {game_state['table'].bet_amount}"

        if game_state['flop'] is None:
            prompt += "A pair after the flop is nothing to get excited about. It might take TWO PAIR or better to take the hand.\n"
            prompt += f"After this betting round, you will see the flop.\n"
            prompt += "If your cards are really weak, and your money_on_table is still 0 or really low, you should just FOLD and conserve your bankroll.\n"
            if self._hole[0].rank == self._hole[1].rank:
                prompt += "Claude is holding a pocket pair.\n"
            else:
                prompt += "Claude is not holding a pocket pair but might still make a good hand with the flop. Think about what hands he might be able to make with his hole cards.\n"
                prompt += "It might make sense to stay in if you have a high card, or if the current_bet is equal to your money_on_table. But, don't raise unless you have something better.\n"
            if self._hole[0].suit == self._hole[1].suit:
                prompt += "Claude's cards have matched suites. A flush draw may be possible.\n"
        elif game_state['turn'] is None:
            prompt += f"After this betting round, you will see the turn.\n"
        elif game_state['river'] is None:
            prompt += "After this betting round, you will see the river.\n"
        else:
            prompt += "After this betting round, everyone will show cards and we will settle the round.\n"


        return prompt

    def decide(self, game_state):
        prompt = self.render_prompt(game_state)

        print(f"Hole: {self._hole}")
        print(f"Flop: {game_state['table'].flop}")
        print(f"Turn: {game_state['table'].turn}")
        print(f"River: {game_state['table'].river}")
        if game_state['flop'] is not None:
            print(f"Best Made Hand: {self.best_hand(game_state['table']).describe()}")
        print(f"Current Bet: {game_state['current_bet']}")
        print(f"Your maximum bet is {self.max_bet} and you already have {self.status.money_on_table} of that on the table.\n")

        # Call the Strands agent
        result = self.agent(prompt)
        llm_decision = str(result)

        print("LLM Decision")
        print(llm_decision)

        # Extract JSON from response
        cleaned_response = "{" + llm_decision.split("{")[1].split('}')[0] + "}"
        print(f"Cleaned Response: {cleaned_response}")
        return json.loads(cleaned_response)

    def play(self, table, player_status, is_called=False, round_number=None):
        print(f"{self.name} is figuring out their next play...")
        print(f"Round Number: {round_number}")

        game_state = {
            "hole": self._hole,
            "player_status": player_status,
            "table": table,
            "is_called": is_called,
            "current_bet": table.bet_amount,
            "max_bet": self.max_bet,
            "flop": table.flop,
            "turn": table.turn,
            "river": table.river,
            "round_number": round_number,
            # "big_blind": self.table.big_blind,
            # "num_players": self.table.num_players,
            # "money_on_table": self.money_on_table,
        }

        retry_count = 0
        action_params = None
        while retry_count < 5:
            try:
                action_params = self.decide(game_state)
                if not 'Action' in action_params.keys() and not 'action' in action_params.keys():
                    raise Exception("MissingActionType")
                if not 'Amount' in action_params.keys() and not 'amount' in action_params.keys():
                    raise Exception("InvalidActionAmount")
                if 'action' in action_params:
                    action_params['Action'] = action_params['action']
                if 'amount' in action_params:
                    action_params['Amount'] = action_params['amount']
                if action_params['Amount'] == '':
                    action_params['Amount'] = 0
                if not 'Action' in action_params.keys():
                    raise Exception("NoValidActionType")
                if not 'Amount' in action_params.keys():
                    raise Exception("NoActionAmount")
                if not action_params['Action'].upper() in ['CALL', 'FOLD', 'RAISE']:
                    raise Exception("InvalidActionType")
                action_params['Action'] = action_params['Action'].strip()
                break
            except json.decoder.JSONDecodeError as e:
                print(f"Warning: Received json response we cant unpack - {e}")
            except IndexError as e:
                print(f"Warning: Received a badly formatted llm decision")
            except Exception as e:
                print(f"Warning: {e}")
            finally:
                retry_count += 1

        if action_params is None:
            print("WARNING: Failed to get valid play after 5 tries to the LLM, FOLDING.")
            action_params = {}
            action_params['Action'] = 'FOLD'
            action_params['Amount'] = 0
            action_params['Message'] = "I'm having trouble thinking straight. Fold."

        if 'Action' in action_params.keys() and not action_params['Action'] == "FOLD":
            action_params['Amount'] = max(int(int(action_params['Amount']) if 'Amount' in action_params else 0), table.bet_amount)

        action_params['Amount'] = min(int(int(action_params['Amount']) if 'Amount' in action_params else 0), self.max_bet)

        if 'action' in action_params:
            action_params['Action'] = action_params['action']
        if 'amount' in action_params:
            action_params['Amount'] = action_params['amount']
        if action_params['Amount'] == '':
            action_params['Amount'] = 0

        if action_params['Action'] == "RAISE":
            # Check for mis-raise thats actually a call
            if int(table.bet_amount) >= int(min(action_params['Amount'], self.max_bet)):
                action_params['Action'] = "CALL" # flip it
                action_params['Amount'] = int(min(action_params['Amount'], self.max_bet))

        is_all_in = action_params['Amount'] == self.max_bet

        # Store the chat message if provided
        self.last_message = action_params.get('Message') or action_params.get('message')

        action = Action(action_params['Action'].strip().upper(), action_params['Amount'], all_in=is_all_in)
        print(action)
        if self.last_message:
            print(f"{self.name} says: {self.last_message}")

        return action
