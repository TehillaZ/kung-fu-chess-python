from board import EMPTY_CELL

class MoveValidator:
    """Checks whether a chess move is legal."""

    def __init__(self, rules_loader):
        self.rules_loader = rules_loader

    def is_legal_move(self, piece, start, end, board):
        if start == end:
            return False

        start_row, start_col = start
        end_row, end_col = end

        delta_row = abs(end_row - start_row)
        delta_col = abs(end_col - start_col)

        piece_type = piece[1] if len(piece) == 2 else piece
        rule = self.rules_loader.get_rule(piece_type)

        if not rule:
            return True

        if "max_steps" in rule:
            if (
                delta_row > rule["max_steps"]
                or delta_col > rule["max_steps"]
            ):
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

        if piece_type in ("R", "B", "Q"):
            if not self._is_path_clear(start, end, board):
                return False

        target_piece = board.get_piece(*end)

        if not self._can_capture(piece, target_piece):
            return False

        return True

    def _is_path_clear(self, start, end, board):
        start_row, start_col = start
        end_row, end_col = end

        row_step = 1 if end_row > start_row else -1 if end_row < start_row else 0
        col_step = 1 if end_col > start_col else -1 if end_col < start_col else 0

        current_row, current_col = start_row + row_step, start_col + col_step

        while (current_row, current_col) != (end_row, end_col):
            if not board.is_empty(current_row, current_col):
                return False
            current_row += row_step
            current_col += col_step

        return True

    def _can_capture(self, moving_piece, target_piece):
        if target_piece == EMPTY_CELL:
            return True

        moving_color = moving_piece[0]
        target_color = target_piece[0]

        return moving_color != target_color