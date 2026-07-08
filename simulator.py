from board import Board
from movement import MoveValidator
from rules import RulesLoader
EMPTY_CELL = "."
class ChessGameSimulator:

    def __init__(self, board_setup):
        self._board = Board(board_setup)
        self.board = self._board.cells
        self.move_validator = MoveValidator(RulesLoader())
        self.selected_pos = None
        self.clock = 0

    def _get_cell_coords(self, x: int, y: int):
        col = x // self._board.cell_size
        row = y // self._board.cell_size

        if 0 <= row < self._board.rows() and 0 <= col < self._board.cols():
            return row, col

        return None

    def execute_click(self, x: int, y: int):
        coords = self._get_cell_coords(x, y)

        if coords is None:
            return

        row, col = coords

        if self.selected_pos is None:
            if not self._board.is_empty(row, col):
                self.selected_pos = (row, col)
            return

        previous_position = self.selected_pos
        piece = self._board.get_piece(*previous_position)

        target_piece = self._board.get_piece(row, col)

        if target_piece != EMPTY_CELL:
           if target_piece[0] == piece[0]:
               self.selected_pos = (row, col)
               return

        if self.move_validator.is_legal_move(
            piece,
            previous_position,
            (row, col),
            self._board,
        ):
            self._board.move_piece(previous_position, (row, col))

        self.selected_pos = None

    def execute_wait(self, ms: int):
        self.clock += ms

    def print_board(self):
        self._board.print_board()

