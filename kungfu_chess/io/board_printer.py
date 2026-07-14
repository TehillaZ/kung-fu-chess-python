class BoardPrinter:
    """Prints a board as text."""

    def print_board(self, board):
        print(self.format_board(board))

    def format_board(self, board):
        return "\n".join(" ".join(row) for row in board.cells)
