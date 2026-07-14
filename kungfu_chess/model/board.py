from kungfu_chess.model.piece import PIECE_STATE_CAPTURED, PIECE_STATE_IDLE
from kungfu_chess.model.position import Position, as_tuple

EMPTY_CELL = "."


class DuplicateOccupancyError(ValueError):
    """Raised when two pieces would occupy the same cell."""


class DuplicatePieceIdError(ValueError):
    """Raised when a piece ID is already registered on the board."""


class Board:
    """Logical chess board storing Piece objects by cell."""

    def __init__(self, board_string=None, cell_size=100, rows=None, cols=None):
        if board_string is not None:
            from kungfu_chess.io.board_parser import BoardParser

            parsed = BoardParser.parse(board_string, cell_size=cell_size)
            self.cell_size = parsed.cell_size
            self._grid = parsed._grid
            self._pieces_by_id = parsed._pieces_by_id
            self.cells = [
                [EMPTY_CELL for _ in range(parsed.cols())]
                for _ in range(parsed.rows())
            ]
            self._sync_cells()
            return

        self.cell_size = cell_size
        self._pieces_by_id = {}

        if rows is None or cols is None:
            raise ValueError("Board requires board_string or explicit rows and cols")

        self._init_grid(rows, cols)
        self._sync_cells()

    def _init_grid(self, rows, cols):
        self._grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.cells = [[EMPTY_CELL for _ in range(cols)] for _ in range(rows)]

    def _sync_cells(self):
        for row in range(self.rows()):
            for col in range(self.cols()):
                self.cells[row][col] = self.get_piece(row, col)

    def rows(self):
        return len(self._grid)

    def cols(self):
        return len(self._grid[0])

    def is_inside(self, row, col):
        return self.is_within_bounds(row, col)

    def is_within_bounds(self, row, col):
        return 0 <= row < self.rows() and 0 <= col < self.cols()

    def piece_at(self, row, col):
        if not self.is_within_bounds(row, col):
            return None
        return self._grid[row][col]

    def get_piece(self, row, col):
        piece = self.piece_at(row, col)
        if piece is None:
            return EMPTY_CELL
        return piece.to_token()

    def is_empty(self, row, col):
        return self.piece_at(row, col) is None

    def all_pieces(self):
        return list(self._pieces_by_id.values())

    def add_piece(self, piece):
        row, col = piece.cell.as_tuple()

        if not self.is_within_bounds(row, col):
            raise ValueError("Piece cell is outside board bounds")

        if not self.is_empty(row, col):
            raise DuplicateOccupancyError(
                f"Cell {row}, {col} is already occupied"
            )

        if piece.id in self._pieces_by_id:
            raise DuplicatePieceIdError(f"Duplicate piece id: {piece.id}")

        self._grid[row][col] = piece
        self._pieces_by_id[piece.id] = piece
        self._sync_cells()

    def remove_piece(self, row, col):
        piece = self.piece_at(row, col)
        if piece is None:
            return None

        piece.state = PIECE_STATE_CAPTURED
        self._grid[row][col] = None
        del self._pieces_by_id[piece.id]
        self._sync_cells()
        return piece

    def set_piece(self, row, col, piece_token):
        if piece_token == EMPTY_CELL:
            if not self.is_empty(row, col):
                self.remove_piece(row, col)
            return

        from kungfu_chess.model.piece_factory import PieceFactory

        if not self.is_empty(row, col):
            self.remove_piece(row, col)

        factory = PieceFactory()
        factory._next_id = len(self._pieces_by_id) + 1
        piece = factory.create_from_token(piece_token, row, col)
        self.add_piece(piece)

    def move_piece(self, start, end):
        start_row, start_col = as_tuple(start)
        end_row, end_col = as_tuple(end)

        piece = self.piece_at(start_row, start_col)
        if piece is None:
            return

        if not self.is_empty(end_row, end_col):
            self.remove_piece(end_row, end_col)

        self._grid[start_row][start_col] = None
        piece.cell = Position(end_row, end_col)
        piece.state = PIECE_STATE_IDLE
        piece.promote_if_needed(self.rows())
        self._grid[end_row][end_col] = piece
        self._sync_cells()
