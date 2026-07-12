from board import Board
from movement import MoveValidator
from realtime_movement import (
    apply_completed_moves,
    compute_departure_time,
    travel_time,
)
from rules import RulesLoader

EMPTY_CELL = "."
MS_PER_CELL = 1000


class ChessGameSimulator:

    def __init__(self, board_setup):
        self._board = Board(board_setup)
        self.board = self._board.cells
        self.move_validator = MoveValidator(RulesLoader())
        self.selected_pos = None
        self.clock = 0
        self.pending_moves = []
        self._move_order = 0

    def _get_cell_coords(self, x: int, y: int):
        col = x // self._board.cell_size
        row = y // self._board.cell_size

        if 0 <= row < self._board.rows() and 0 <= col < self._board.cols():
            return row, col

        return None

    def _apply_completed_moves(self):
        self.pending_moves = apply_completed_moves(
            self._board,
            self.pending_moves,
            self.clock,
            self.move_validator,
        )

    def _has_pending_move_from(self, position):
        return any(move["start"] == position for move in self.pending_moves)

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
            if not self._has_pending_move_from(previous_position):
                departure_time = compute_departure_time(
                    self.clock,
                    piece,
                    previous_position,
                    (row, col),
                    self.pending_moves,
                )
                move_time = travel_time(
                    previous_position,
                    (row, col),
                    MS_PER_CELL,
                )
                self.pending_moves.append({
                    "piece": piece,
                    "start": previous_position,
                    "end": (row, col),
                    "departure_time": departure_time,
                    "arrival_time": departure_time + move_time,
                    "order": self._move_order,
                })
                self._move_order += 1

        self.selected_pos = None

    def execute_wait(self, ms: int):
        self.clock += ms
        self._apply_completed_moves()

    def print_board(self):
        self._board.print_board()
