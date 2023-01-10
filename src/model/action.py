CHECK = "CHECK"
FOLD = "FOLD"
RAISE = "RAISE"
CALL = "CALL"
MATCH = "MATCH"

action_types = [
    CHECK,
    CALL,
    RAISE,
    FOLD,
    MATCH
]


class Action:
    def __init__(self, action_type, amount=None, all_in=False):
        if not action_type in action_types:
            raise Exception(f"Invalid action: {action_type}")
        if not amount:
            if action_type in [RAISE, CALL, MATCH]:
                raise Exception(f"Invalid MATCH, RAISE or CALL amount (None)")
        else:
            if action_type in [CHECK, FOLD]:
                raise Exception(f"Invalid CHECK or FOLD")
            if amount < 0:
                raise ValueError(f"Cannot {action_type} by a negative number: {amount}")
        self.action_type = action_type
        self.amount = amount
        self.all_in = all_in

    def __str__(self):
        return f"Action({self.action_type}, {self.amount})"
