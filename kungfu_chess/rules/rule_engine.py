from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.rules.piece_rules import (
    build_piece_validators,
    piece_color,
    piece_kind,
)
from kungfu_chess.rules.rules_loader import RulesLoader


class MoveValidation:
    """Stable read-only validation result for a move request."""

    def __init__(self, is_valid, reason):
        self.is_valid = is_valid
        self.reason = reason

    def __repr__(self):
        return (
            f"MoveValidation(is_valid={self.is_valid!r}, "
            f"reason={self.reason!r})"
        )


class RuleEngine:
    """Validates moves without mutating the board."""

    def __init__(self, rules_loader=None):
        self._rules_loader = rules_loader or RulesLoader()
        self._validators = build_piece_validators(self._rules_loader)

    def validate_move(self, *args):
        if len(args) == 3:
            board, start, end = args
            piece = (
                board.get_piece(*start)
                if board.is_within_bounds(*start)
                else EMPTY_CELL
            )
        elif len(args) == 4:
            piece, start, end, board = args
        else:
            raise TypeError("validate_move expects 3 or 4 arguments")

        if not board.is_within_bounds(*start) or not board.is_within_bounds(*end):
            return MoveValidation(False, "outside_board")

        if piece == EMPTY_CELL:
            return MoveValidation(False, "empty_source")

        target_piece = board.get_piece(*end)
        if (
            target_piece != EMPTY_CELL
            and piece_color(piece) == piece_color(target_piece)
        ):
            return MoveValidation(False, "friendly_destination")

        piece_type = piece_kind(piece)
        validator = self._validators.get(piece_type)

        if validator is None:
            return MoveValidation(False, "illegal_piece_move")

        if validator(piece, start, end, board):
            return MoveValidation(True, "ok")

        return MoveValidation(False, "illegal_piece_move")

    def is_legal_move(self, piece, start, end, board):
        return self.validate_move(piece, start, end, board).is_valid
