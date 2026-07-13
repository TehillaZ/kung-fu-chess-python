from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.rules.path_utils import is_path_clear
from kungfu_chess.rules.rules_loader import RulesLoader

RULE_BASED_PIECES = ("K", "R", "B", "Q", "N")
SLIDING_PIECES = frozenset({"R", "B", "Q"})


def is_friendly_piece(moving_piece, target_piece):
    return (
        target_piece != EMPTY_CELL
        and moving_piece[0] == target_piece[0]
    )


def can_capture(moving_piece, target_piece):
    if target_piece == EMPTY_CELL:
        return True

    return moving_piece[0] != target_piece[0]


def is_pawn_move_legal(piece, start, end, board):
    color = piece[0]
    start_row, start_col = start
    end_row, end_col = end

    delta_row = end_row - start_row
    delta_col = end_col - start_col
    forward = -1 if color == "w" else 1
    start_rank = board.rows() - 1 if color == "w" else 0

    target_piece = board.get_piece(end_row, end_col)

    if delta_col == 0 and delta_row == forward:
        return target_piece == EMPTY_CELL

    if delta_col == 0 and delta_row == 2 * forward:
        if start_row != start_rank:
            return False
        if target_piece != EMPTY_CELL:
            return False
        return is_path_clear(start, end, board)

    if abs(delta_col) == 1 and delta_row == forward:
        if target_piece == EMPTY_CELL:
            return False
        return target_piece[0] != color

    return False


def _validate_rule_based_move(piece, start, end, board, rules_loader, piece_type):
    start_row, start_col = start
    end_row, end_col = end

    delta_row = abs(end_row - start_row)
    delta_col = abs(end_col - start_col)

    rule = rules_loader.get_rule(piece_type)

    if not rule:
        return True

    if "max_steps" in rule:
        if delta_row > rule["max_steps"] or delta_col > rule["max_steps"]:
            return False

    if rule.get("is_knight"):
        return (
            (delta_row == 2 and delta_col == 1)
            or (delta_row == 1 and delta_col == 2)
        )

    if delta_row == delta_col:
        if not rule.get("diagonal"):
            return False
    elif delta_row == 0 or delta_col == 0:
        if not rule.get("straight"):
            return False
    else:
        return False

    if piece_type in SLIDING_PIECES:
        if not is_path_clear(start, end, board):
            return False

    target_piece = board.get_piece(end_row, end_col)

    if not can_capture(piece, target_piece):
        return False

    return True


def _create_rule_validator(rules_loader, piece_type):
    def is_legal_move(piece, start, end, board):
        return _validate_rule_based_move(
            piece, start, end, board, rules_loader, piece_type
        )

    return is_legal_move


def build_piece_validators(rules_loader):
    validators = {"P": is_pawn_move_legal}

    for piece_type in RULE_BASED_PIECES:
        validators[piece_type] = _create_rule_validator(rules_loader, piece_type)

    return validators
