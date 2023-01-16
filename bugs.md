## Misdelt A of Spades twice
This example shows human player had a pair of Aces, but presented a Queen high and
subsequently lost the hand. However, closer inspection shows the Ace of Spedes in 
both the players hole and in the flop.

```terminfo
[Card("10", "Spades"), Card("A", "Diamonds")]
The bet is: 40
Flop: [Card("A", "Spades"), Card("7", "Clubs"), Card("4", "Spades")]
Turn: Card("3", "Hearts")
Rover: Card("2", "Spades")
The bet is 40 and you have 60 in your bankroll and 40 on the table
Check/ Call, Fold, or Raise
Enter: c | r | f: c
Got Action: c
Advanced active player index to 0
Whos in? [Player(Madi, 547), Player(Josh, 60)]
Active player: Player(Beezie, 2)
Advanced active player index to 1
Whos in? [Player(Madi, 547), Player(Josh, 60)]
Active player: Player(Madi, 547)
Advanced active player index to 2
{'all_hands': {'Josh': Hand([Card("10", "Spades"), Card("A", "Diamonds"), Card("4", "Spades"), Card("3", "Hearts"), Card("2", "Spades")]),
               'Madi': Hand([Card("Q", "Clubs"), Card("A", "Spades"), Card("4", "Spades"), Card("3", "Hearts"), Card("2", "Spades")])},
 'pot_size': 91,
 'winner_personas': ['Callie Calls'],
 'winners': ['Madi'],
 'winning_hand': Hand([Card("Q", "Clubs"), Card("A", "Spades"), Card("4", "Spades"), Card("3", "Hearts"), Card("2", "Spades")])}
```

## Split Pot
No serious attempt has been made to get this right yet. 