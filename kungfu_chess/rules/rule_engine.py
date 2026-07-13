from kungfu_chess.rules.piece_rules import build_piece_validators
from kungfu_chess.rules.rules_loader import RulesLoader


class RuleEngine:
    """Validates moves without mutating the board."""

    def __init__(self, rules_loader=None):
        self._rules_loader = rules_loader or RulesLoader()
        self._validators = build_piece_validators(self._rules_loader)

    def validate_move(self, piece, start, end, board):
        if start == end:
            return "same_position"

        piece_type = piece[1] if len(piece) == 2 else piece
        validator = self._validators.get(piece_type)

        if validator is None:
            return None

        if validator(piece, start, end, board):
            return None

        return "illegal_move"

    def is_legal_move(self, piece, start, end, board):
        return self.validate_move(piece, start, end, board) is None
