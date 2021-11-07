
action_types = [
    "CHECK",
    "CALL",
    "RAISE",
    "FOLD",
]

class Action:
    def __init__(self, action_type):
        if not action_type in action_types:
            raise Exception(f"Invalid action: {action_type}")
        self.action_type = action_type