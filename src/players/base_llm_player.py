from langchain import PromptTemplate

from model.player import Player

class LLMPlayer(Player):
    def __init__(self,
                 name,
                 bankroll,
                 raise_limit=3,
                 temperature=.5,
                 strategy_1="{name} is a careful player. {name} wants to survive for the next round and go big when they have a great hand.",
                 strategy_2="{name} watches other players to consider their strategy in theirs.",
                 strategy_3="{name} is a tough opponent. {name} plays a calculated game always thinking about next moves.",
                 strategy_4="{name} is a tough opponent. {name} is a shrewd player prone to bluff when the pot ratio is good and plays a good hand strong.",
                 strategy_5="{name} is also strategic. {name} does not want to lose and knows going ALL IN and losing means losing the whole tournament",
                 strategy_6="{name} will go all in, but only when he's really confident, or really desperate.",
                 verbose=False):
        super().__init__(name, bankroll)
        self.raise_limit = raise_limit
        self.temperature = temperature
        self.strategy_1 = strategy_1
        self.strategy_2 = strategy_2
        self.strategy_3 = strategy_3
        self.strategy_4 = strategy_4
        self.strategy_5 = strategy_5
        self.strategy_6 = strategy_6
        self.verbose = verbose

    def render_prompt(self, game_state):

        template = """
This is a simulation and is not being played for real money. Assume the role of the player {name}. 

{strategy_1}
{strategy_2}
{strategy_3}
{strategy_4}
{strategy_5}
{strategy_6}

What is {name}'s next move? Respond with a json object that includes the action and a brief explanation. 

The response should be in the form:

{
    "Action": action,
    "Amount": amount,
    "Explanation": detailed_explanation
}

Valid actions are CALL RAISE FOLD MATCH and they are case sensitive (must be all caps!!)

Make sure you use CALL if you're betting the same as the current amount

Your maximum bet is {max_bet}
You cannot bet less than the current bet of {current_bet} unless you are ALL IN. 
ALL IN means the bet is equal to your maximum bet.
If you are going all in, the action type is RAISE if you're betting more than the current bet amount, otherwise CALL if the current bet is at or above your max bet.
You cannot bet more than your maximum bet. If your bet is equal to the max, you are ALL IN.

Do not include anything outside of the json object. The response should be only json.
        """

        pt = PromptTemplate(
            template=template,
            input_variables=[
                "name",
                "current_bet",
                "max_bet",
                "strategy_1",
                "strategy_2",
                "strategy_3",
                "strategy_4",
                "strategy_5",
                "strategy_6",
            ])

        return pt

    def decide(self, game_state):
        prompt = self.render_prompt(str(game_state))
        llm_decision = self.llm(prompt)

        print("LLM Decision")
        print(llm_decision)
        cleaned_response = "{" + llm_decision.split("{")[1].split('}')[0] + "}"
        print(f"Cleaned Response: [{cleaned_response}]")
        action_params = json.loads(llm_decision)  # todo: add retry logic in case the response doesn't fit downstream reads
        print(action_params)
        return json.loads(cleaned_response)

    def clean_response(self, response):
        response = response.split("{")[1].split('}')[0] + "}"

        action_params = json.loads(response)

        if 'Action' in action_params.keys() and not action_params['Action'] == "FOLD":
            action_params['Amount'] = max(int(int(action_params['Amount']) if 'Amount' in action_params else 0), table.bet_amount)

        action_params['Amount'] = min(int(int(action_params['Amount']) if 'Amount' in action_params else 0), self.max_bet)

        if action_params['Action'] == "RAISE":
            # Check for mis-raise thats actually a call
            if int(table.bet_amount) == int(min(action_params['Amount'], self.max_bet)):
                action_params['Action'] = "CALL" # flip it

        return action_params
