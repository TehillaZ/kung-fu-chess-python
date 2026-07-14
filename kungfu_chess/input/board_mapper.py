from kungfu_chess.model.position import Position, as_tuple


CELL_SIZE = 100


class BoardMapper:
    """Translates pixel coordinates into board positions."""

    def __init__(self, board, cell_size=CELL_SIZE):
        self._board = board
        self._cell_size = cell_size

    def pixel_to_cell(self, x, y):
        col = x // self._cell_size
        row = y // self._cell_size

        if self._board.is_within_bounds(row, col):
            return Position(row, col)

        return None

    def to_position(self, x, y):
        return self.pixel_to_cell(x, y)
