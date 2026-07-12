from board import Board
from movement import MoveValidator
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

    def _get_cell_coords(self, x: int, y: int):
        col = x // self._board.cell_size
        row = y // self._board.cell_size

        if 0 <= row < self._board.rows() and 0 <= col < self._board.cols():
            return row, col

        return None

    def _travel_time(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        distance = max(abs(end_row - start_row), abs(end_col - start_col))
        return distance * MS_PER_CELL

    def _column_range(self, start, end):
        start_row, start_col = start
        end_row, end_col = end

        if start_row == end_row:
            return min(start_col, end_col), max(start_col, end_col)

        return None

    def _row_range(self, start, end):
        start_row, start_col = start
        end_row, end_col = end

        if start_col == end_col:
            return min(start_row, end_row), max(start_row, end_row)

        return None

    def _path_cells(self, start, end):
        start_row, start_col = start
        end_row, end_col = end
        cells = []

        row_step = 0 if end_row == start_row else (1 if end_row > start_row else -1)
        col_step = 0 if end_col == start_col else (1 if end_col > start_col else -1)

        row, col = start_row, start_col
        while True:
            cells.append((row, col))
            if (row, col) == (end_row, end_col):
                break
            row += row_step
            col += col_step

        return cells

    def _ranges_overlap(self, first_range, second_range):
        return (
            first_range[0] <= second_range[1]
            and second_range[0] <= first_range[1]
        )

    def _has_common_route(self, start1, end1, start2, end2):
        column_range1 = self._column_range(start1, end1)
        column_range2 = self._column_range(start2, end2)
        if column_range1 and column_range2:
            return self._ranges_overlap(column_range1, column_range2)

        row_range1 = self._row_range(start1, end1)
        row_range2 = self._row_range(start2, end2)
        if row_range1 and row_range2:
            return self._ranges_overlap(row_range1, row_range2)

        return bool(set(self._path_cells(start1, end1)) & set(self._path_cells(start2, end2)))

    def _departure_time(self, piece, start, end):
        departure_time = self.clock

        for pending in self.pending_moves:
            if pending["piece"][0] == piece[0]:
                continue

            if self._has_common_route(
                start,
                end,
                pending["start"],
                pending["end"],
            ):
                departure_time = max(departure_time, pending["arrival_time"])

        return departure_time

    def _apply_completed_moves(self):
        still_pending = []

        for move in sorted(self.pending_moves, key=lambda m: m["arrival_time"]):
            if move["arrival_time"] <= self.clock:
                self._board.move_piece(move["start"], move["end"])
            else:
                still_pending.append(move)

        self.pending_moves = still_pending

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
                departure_time = self._departure_time(
                    piece,
                    previous_position,
                    (row, col),
                )
                travel_time = self._travel_time(previous_position, (row, col))
                self.pending_moves.append({
                    "piece": piece,
                    "start": previous_position,
                    "end": (row, col),
                    "departure_time": departure_time,
                    "arrival_time": departure_time + travel_time,
                })

        self.selected_pos = None

    def execute_wait(self, ms: int):
        self.clock += ms
        self._apply_completed_moves()

    def print_board(self):
        self._board.print_board()
