## Texas Holdem Agents

Texas Holdem Agents is a poker simulation designed to be played
by some combination of human and ai players. The player interface
is a Python class that inherits from model.player.

The simulation currently includes baseline rules based players,
a human player cli interface, and two LLM agents using models
from Anthropic and OpenAI. If you use an LLM model, you need to
configure your API access keys as an environment error. If you
miss the API keys, you should see a helpful message.

### Running it

There's not much for an interface yet. You can define a tournament
or series of them as I have in src/main.py. The easiest way to get
started is to install python requirements and then run main.py.
You can modify it to change to the player mix to your liking.
If you run it with a Human player, it will prompt you for input.

The source code is rooted in the src directory.  
```bash
cd src
```  

` 
Install dependencies
```bash
pip install -r requirements.txt
```
Run the simulation
```angular2html
python3 main.py
```