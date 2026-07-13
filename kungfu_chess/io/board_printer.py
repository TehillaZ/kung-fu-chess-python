class BoardPrinter:
    """Prints a board as text."""

    def print_board(self, board):
        for row in board.cells:
            print(" ".join(row))
