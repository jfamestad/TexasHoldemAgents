
CHECK = "CHECK"
FOLD = "FOLD"
RAISE = "RAISE"
CALL = "CALL"

action_types = [
    CHECK,
    CALL,
    RAISE,
    FOLD,
]

class Action:
    def __init__(self, action_type, amount=None):
        if not action_type in action_types:
            raise Exception(f"Invalid action: {action_type}")
        if not amount:
            if action_type in [ RAISE, CALL ]:
                raise Exception(f"Invalid RAISE or CALL amount (None)")
        else:
            if action_type in [ CHECK, FOLD ]:
                raise Exception(f"Invalid CHECK or FOLD")
        self.action_type = action_type
        self.amount = amount

    def __str__(self):
        return f"Action({self.action_type}, {self.amount})"

# class Call(Action):
#     pass
#
# class Check(Action):
#     pass
#
# class Raise(Action):
#     pass
#
# class Fold(Action):
#     pass