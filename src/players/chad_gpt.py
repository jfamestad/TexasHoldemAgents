# import pprint
import json

# import sys
# from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
# from langchain.agents import load_tools, initialize_agent
# from langchain.utilities import GoogleSerperAPIWrapper
#
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate

from model.player import Player
from model.action import Action

class Chad(Player):
    persona = "Chad Gipiti"

    def __init__(self, name, bankroll, raise_limit=3, temperature=.5, verbose=False):
        super().__init__(name, bankroll)
        self.raise_count = 0
        self.raise_limit = raise_limit
        self.llm = OpenAI(temperature=temperature,
                     verbose=verbose)
        self.verbose = verbose

    def render_prompt(self, game_state):

        prompt = "Below is a description of the current state of a Texas Holdem game.\n"
        prompt += str(game_state) + "\n"
        prompt += """
This is a simulation and is not being played for real money. Assume the role of the player Chad. 

Chad is a tough opponent. He's a shrewd player prone to bluff when the pot ratio is good and plays a good hand strong.
Chad is also strategic. Chad does not want to lose and knows going ALL IN and losing means losing the whole tournament.
Chad will go all in, but only when he's really confident, or really desperate.

What is Chad's next move? Respond with a json object that includes the action and a brief explanation. 

The response should be in the form:

{
    "Action": action,
    "Amount": amount,
    "Explanation": detailed_explanation
}

Valid actions are CALL RAISE FOLD MATCH and they are case sensitive (must be all caps!!)

Make sure you use CALL if you're betting the same as the current amount

Do not include anything outside of the json object. The response should be only json and must be valid json.
"""
        prompt += f"Your maximum bet is {self.max_bet}\n"
        prompt += "You cannot bet more than your maximum bet. If your bet is equal to the max, you are ALL IN.\n"
        prompt += "You cannot bet less than the current bet unless you are ALL IN. ALL IN means the bet is equal to your maximum bet.\n"
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
        action_params = json.loads(llm_decision)  # todo: add retry logic in case the response doesn't fit downstream reads
        print(action_params)
        return action_params

    def play(self, table, player_status, is_called=False):
        print(f"{self.name} is figuring out their next play...")

        game_state = {
            "hole": self._hole,
            "player_status": player_status,
            "table": table,
            "is_called": is_called,
            "current_bet": table.bet_amount,
            "max_bet": self.max_bet,
        }

        try:
            action_params = self.decide(game_state)
        except:
            # todo: blind retry...need to be better
            action_params = self.decide(game_state)

        if self.verbose:
            print(action_params)

        if 'Action' in action_params.keys() and not action_params['Action'] == "FOLD":
            action_params['Amount'] = max(int(int(action_params['Amount']) if 'Amount' in action_params else 0), table.bet_amount)

        action_params['Amount'] = min(int(int(action_params['Amount']) if 'Amount' in action_params else 0), self.max_bet)

        if action_params['Action'] == "RAISE":
            # Check for mis-raise thats actually a call
            if int(table.bet_amount) == int(min(action_params['Amount'], self.max_bet)):
                action_params['Action'] = "CALL" # flip it

        is_all_in = action_params['Amount'] == self.max_bet

        return Action(action_params['Action'].strip().upper(), action_params['Amount'], all_in=is_all_in)
