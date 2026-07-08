EMPTY_CELL = "."

class Board:
    """Represents the chess board."""

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

    def move_piece(self, start, end):
        start_row, start_col = start
        end_row, end_col = end

        piece = self.get_piece(start_row, start_col)

        self.set_piece(end_row, end_col, piece)
        self.set_piece(start_row, start_col, EMPTY_CELL)

    def rows(self):
        return len(self.cells)

    def cols(self):
        return len(self.cells[0])

    def print_board(self):
        for row in self.cells:
            print(" ".join(row))
