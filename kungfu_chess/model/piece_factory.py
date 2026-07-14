from kungfu_chess.model.piece import Piece
from kungfu_chess.model.position import Position


class PieceFactory:
    """Assigns stable unique piece IDs at creation time."""

    def __init__(self):
        self._next_id = 1

    def create_from_token(self, token, row, col):
        piece = Piece.from_token(
            token,
            self._make_id(),
            Position(row, col),
        )
        return piece

    def _make_id(self):
        piece_id = f"p{self._next_id}"
        self._next_id += 1
        return piece_id
