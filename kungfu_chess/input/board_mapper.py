from kungfu_chess.model.position import Position


class BoardMapper:
    """Translates pixel coordinates into board positions."""

    def __init__(self, board):
        self._board = board

    def to_position(self, x, y):
        col = x // self._board.cell_size
        row = y // self._board.cell_size

        if self._board.is_within_bounds(row, col):
            return Position(row, col)

        return None
