import json
import os


class RulesLoader:
    """Loads chess movement rules from JSON configuration."""

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "rules.json")

        try:
            with open(config_path, "r") as file:
                self.rules = json.load(file)
        except FileNotFoundError:
            self.rules = {}

    def get_rule(self, piece_type):
        return self.rules.get(piece_type)
