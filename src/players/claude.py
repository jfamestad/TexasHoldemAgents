import pprint
import json

import sys
from langchain.llms import Anthropic
# from langchain import PromptTemplate, LLMChain

from model.player import Player
from model.action import Action

class Claude(Player):
    persona = "Claude"

    def __init__(self, name, bankroll, raise_limit=3, temperature=.5, verbose=False):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit
        self.llm = llm = Anthropic() # todo: we arent passing temperature yet...

    def render_prompt(self, game_state):

        prompt = "Below is a description of the current state of a Texas Holdem game.\n"
        prompt += str(game_state) + "\n"
        prompt += """
This is a simulation and is not being played for real money. Assume the role of the player Claude. 

Claude is a tough opponent. Claude plays a calculated game always thinking about next moves. 
Claude watches other players to consider their strategy in his.
Claude is also strategic. Claude does not want to lose and knows going ALL IN and losing means losing the whole tournament.
It's important to win the hand. but more important to stay in the tournament. Claude is not afraid to FOLD a hand that won't win.
Claude will go all in, but only when he's really confident, or really desperate.
Claude thinks through his money on the table, his backroll, max_bet, and the current bet before deciding an action.
Claude knows that if the current bet is greater than or equaul to his max_bet, Claude would be going ALL IN to CALL and risk losing the tournament.

What is Claude's next move? Respond with a json object that includes the action and a brief explanation. 

The response should be in the form:

{
    "Action": action,
    "Amount": amount,
    "Explanation": detailed_explanation
}

Valid actions are CALL RAISE FOLD MATCH and they are case sensitive (must be all caps!!)
Valid values for amount are integers greater than or equal to the table current_bet and less than or equal to the players max_bet.

Claude knows other players are likely playing simple strategies. For example, some players will always CALL. Others will only raise if they have a pair or better.

Make sure you use CALL if you're betting the same as the current amount.
If you CALL, the Amount must be the current_bet from the table.
Claude would never fold if your money_on_the_table is already close to the current_bet.
If Claude has a great hand, he will raise to increase the pot size when possible.
If you want to bet more than the table current_bet, that is a RAISE.
If you RAISE, the Amount is the total bet amount equal to the sum of the current_bet plus your additional amount. 
For example, if the bet_amount is 5 and you are raising by 3, the Amount is 8.

Do not include anything outside of the json object. The response should be only json.
"""
        prompt += f"Your maximum bet is {self.max_bet}\n"
        prompt += "You cannot bet less than the current bet unless you are ALL IN. ALL IN means the bet is equal to your maximum bet.\n"
        prompt += "You cannot bet more than your maximum bet. If your bet is equal to the max, you are ALL IN.\n"
        prompt += "Even if the Amount is 0, just include it in the json response anyway.\n"
        prompt += "If you are going all in, the action type is RAISE if you're betting more than the current bet amount, otherwise CALL if the current bet is at or above your max bet.\n"
        # prompt += f"The minimum amount you can RAISE is {game_state['table'].bet_amount}"

        return prompt

    def decide(self, game_state):
        prompt = self.render_prompt(str(game_state))
        llm_decision = self.llm(prompt)

        print("LLM Decision")
        print(llm_decision)
        cleaned_response = "{" + llm_decision.split("{")[1].split('}')[0] + "}"
        print(f"Cleaned Response: [{cleaned_response}]")
        action_params = json.loads(llm_decision)
        print(action_params)
        return json.loads(cleaned_response)

    def play(self, table, player_status, is_called=False, round_number=None):
        print(f"{self.name} is figuring out their next play...")

        game_state = {
            "hole": self._hole,
            "player_status": player_status,
            "table": table,
            "is_called": is_called,
            "current_bet": table.bet_amount,
            "max_bet": self.max_bet,
            # "big_blind": self.table.big_blind,
            # "num_players": self.table.num_players,
            # "money_on_table": self.money_on_table,
        }

        retry_count = 0
        while retry_count < 3:
            try:
                action_params = self.decide(game_state)
                break
            except json.decoder.JSONDecodeError as e:
                print(f"Warning: Received json response we cant unpack - {e}")
            except IndexError as e:
                print(f"Warning: Received a badly formatted llm decision")
            finally:
                retry_count += 1

        if 'Action' in action_params.keys() and not action_params['Action'] == "FOLD":
            action_params['Amount'] = max(int(int(action_params['Amount']) if 'Amount' in action_params else 0), table.bet_amount)

        action_params['Amount'] = min(int(int(action_params['Amount']) if 'Amount' in action_params else 0), self.max_bet)

        if action_params['Action'] == "RAISE":
            # Check for mis-raise thats actually a call
            if int(table.bet_amount) >= int(min(action_params['Amount'], self.max_bet)):
                action_params['Action'] = "CALL" # flip it
                action_params['Amount'] = int(min(action_params['Amount'], self.max_bet))

        is_all_in = action_params['Amount'] == self.max_bet

        action = Action(action_params['Action'].strip().upper(), action_params['Amount'], all_in=is_all_in)
        print(action)

        return action
