import unittest

from kungfu_chess.model.board import (
    Board,
    DuplicateOccupancyError,
    DuplicatePieceIdError,
)
from kungfu_chess.model.piece import PIECE_STATE_CAPTURED, Piece
from kungfu_chess.model.position import Position


class TestBoard(unittest.TestCase):
    def test_dimensions_inferred_from_string(self):
        board = Board("wK . .\n. bR .")

        self.assertEqual(board.rows(), 2)
        self.assertEqual(board.cols(), 3)

    def test_piece_lookup_returns_token(self):
        board = Board("wK .\n. .")

        self.assertEqual(board.get_piece(0, 0), "wK")
        self.assertEqual(board.piece_at(0, 0).id, "p1")

    def test_empty_cell_lookup(self):
        board = Board("wK .\n. .")

        self.assertTrue(board.is_empty(0, 1))
        self.assertIsNone(board.piece_at(0, 1))
        self.assertEqual(board.get_piece(0, 1), ".")

    def test_add_piece_rejects_duplicate_occupancy(self):
        board = Board(rows=2, cols=2)
        board.add_piece(Piece("p1", "w", "K", Position(0, 0)))

        with self.assertRaises(DuplicateOccupancyError):
            board.add_piece(Piece("p2", "b", "K", Position(0, 0)))

    def test_add_piece_rejects_duplicate_id(self):
        board = Board(rows=2, cols=2)
        board.add_piece(Piece("p1", "w", "K", Position(0, 0)))

        with self.assertRaises(DuplicatePieceIdError):
            board.add_piece(Piece("p1", "b", "R", Position(1, 0)))

    def test_move_piece_updates_cells_and_piece_cell(self):
        board = Board("wR .\n. .")
        piece = board.piece_at(0, 0)

        board.move_piece((0, 0), (0, 1))

        self.assertTrue(board.is_empty(0, 0))
        self.assertEqual(board.get_piece(0, 1), "wR")
        self.assertEqual(piece.cell, Position(0, 1))

    def test_move_piece_captures_enemy_and_marks_captured_state(self):
        board = Board("wR bR")
        captured = board.piece_at(0, 1)

        board.move_piece((0, 0), (0, 1))

        self.assertEqual(board.get_piece(0, 1), "wR")
        self.assertTrue(board.is_empty(0, 0))
        self.assertEqual(captured.state, PIECE_STATE_CAPTURED)
        self.assertNotIn(captured.id, {piece.id for piece in board.all_pieces()})

    def test_remove_piece_clears_cell_and_marks_captured(self):
        board = Board("wN .\n. .")
        piece = board.piece_at(0, 0)

        removed = board.remove_piece(0, 0)

        self.assertIs(removed, piece)
        self.assertTrue(board.is_empty(0, 0))
        self.assertEqual(piece.state, PIECE_STATE_CAPTURED)
        self.assertNotIn("p1", {p.id for p in board.all_pieces()})

    def test_is_inside_matches_bounds(self):
        board = Board("wK .\n. .")

        self.assertTrue(board.is_inside(0, 0))
        self.assertTrue(board.is_inside(1, 1))
        self.assertFalse(board.is_inside(2, 0))


if __name__ == "__main__":
    unittest.main()
