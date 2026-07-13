from kungfu_chess.model.position import as_tuple

EMPTY_CELL = "."


class Board:
    """Logical chess board."""

    def __init__(self, board_string, cell_size=100):
        self.cell_size = cell_size
        self.cells = [
            row.split()
            for row in board_string.strip().split("\n")
        ]

    def get_piece(self, row, col):
        return self.cells[row][col]

    def set_piece(self, row, col, piece):
        self.cells[row][col] = piece

    def is_empty(self, row, col):
        return self.get_piece(row, col) == EMPTY_CELL

    def is_within_bounds(self, row, col):
        return 0 <= row < self.rows() and 0 <= col < self.cols()

    def move_piece(self, start, end):
        start_row, start_col = as_tuple(start)
        end_row, end_col = as_tuple(end)

        piece = self.get_piece(start_row, start_col)

        self.set_piece(end_row, end_col, piece)
        self.set_piece(start_row, start_col, EMPTY_CELL)
        self._promote_pawn_if_needed(end_row, end_col)

    def _promote_pawn_if_needed(self, row, col):
        piece = self.get_piece(row, col)

        if len(piece) != 2 or piece[1] != "P":
            return

        color = piece[0]
        promotion_row = 0 if color == "w" else self.rows() - 1

        if row == promotion_row:
            self.set_piece(row, col, f"{color}Q")

    def rows(self):
        return len(self.cells)

    def cols(self):
        return len(self.cells[0])
