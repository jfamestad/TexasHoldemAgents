from collections import namedtuple

Character = namedtuple("Character", ("filename", "classname"))

characters = [
    Character("callie_calls", "Callie"),
    Character("floyd_folds", "Floyd"),
    Character("herbie_human", "Herbie"),
    Character("johnny_jacks", "Johnny"),
    Character("ricky_raise", "Ricky"),
    Character("robbie_random", "Robby"),
    Character("stuart_stats", "Stuart"),
]

def do_test_character(character):
    # print(f"Testing {character.classname} from {character.filename}")
    # module = __import__(character.filename)
    # PlayerCharacter = getattr(module, character.classname)
    # import players
    print(f"Importing {character.classname} from {character.filename}")
    PlayerCharacter = getattr(__import__(character.filename), f"{character.classname}")


# def test_characters():
#     for character in characters:
#         do_test_character(character)