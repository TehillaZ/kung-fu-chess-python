import unittest

from kungfu_chess.model.piece import (
    PIECE_STATE_CAPTURED,
    PIECE_STATE_IDLE,
    PIECE_STATE_MOVING,
    Piece,
)
from kungfu_chess.model.position import Position


class TestPiece(unittest.TestCase):
    def test_from_token_creates_piece_with_cell(self):
        piece = Piece.from_token("wK", "p1", Position(0, 0))

        self.assertEqual(piece.id, "p1")
        self.assertEqual(piece.color, "w")
        self.assertEqual(piece.kind, "K")
        self.assertEqual(piece.cell, Position(0, 0))
        self.assertEqual(piece.state, PIECE_STATE_IDLE)

    def test_to_token(self):
        piece = Piece("p2", "b", "R", Position(1, 2))

        self.assertEqual(piece.to_token(), "bR")

    def test_lifecycle_state_transitions(self):
        piece = Piece("p3", "w", "N", Position(0, 0))

        self.assertTrue(piece.is_idle())

        piece.state = PIECE_STATE_MOVING
        self.assertTrue(piece.is_moving())
        self.assertFalse(piece.is_idle())

        piece.state = PIECE_STATE_CAPTURED
        self.assertTrue(piece.is_captured())

    def test_piece_repr_is_readable(self):
        piece = Piece("p4", "w", "P", Position(2, 1))

        self.assertIn("wP", repr(piece))
        self.assertIn("p4", repr(piece))


if __name__ == "__main__":
    unittest.main()
