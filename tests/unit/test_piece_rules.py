import unittest

from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position
from kungfu_chess.rules.piece_rules import legal_destinations


class TestPieceRules(unittest.TestCase):
    def test_rook_moves_across_empty_row_and_column(self):
        board = Board(". . .\n. wR .\n. . .")
        rook = board.piece_at(1, 1)

        self.assertEqual(
            legal_destinations(board, rook),
            {
                Position(0, 1),
                Position(2, 1),
                Position(1, 0),
                Position(1, 2),
            },
        )

    def test_rook_stops_before_friendly_blocker(self):
        board = Board(". wP .\n. wR .\n. . .")
        rook = board.piece_at(1, 1)

        self.assertNotIn(Position(0, 1), legal_destinations(board, rook))

    def test_rook_captures_enemy_blocker_but_does_not_pass_it(self):
        board = Board("bP . .\nbR . wR\n. . .")
        rook = board.piece_at(1, 2)

        destinations = legal_destinations(board, rook)

        self.assertIn(Position(1, 0), destinations)
        self.assertNotIn(Position(1, -1), destinations)

    def test_bishop_moves_diagonally_and_not_straight(self):
        board = Board(". . .\n. wB .\n. . .")
        bishop = board.piece_at(1, 1)

        destinations = legal_destinations(board, bishop)

        self.assertIn(Position(0, 0), destinations)
        self.assertIn(Position(2, 2), destinations)
        self.assertNotIn(Position(0, 1), destinations)

    def test_queen_combines_rook_and_bishop_movement(self):
        board = Board(". . .\n. wQ .\n. . .")
        queen = board.piece_at(1, 1)

        destinations = legal_destinations(board, queen)

        self.assertIn(Position(0, 1), destinations)
        self.assertIn(Position(0, 0), destinations)

    def test_knight_jumps_over_blockers(self):
        board = Board(". . .\n. wP .\nwP wN wP\n. wP .\n. . .")
        knight = board.piece_at(2, 1)

        destinations = legal_destinations(board, knight)

        self.assertIn(Position(0, 0), destinations)
        self.assertIn(Position(0, 2), destinations)
        self.assertIn(Position(4, 0), destinations)
        self.assertIn(Position(4, 2), destinations)

    def test_king_moves_one_cell_only(self):
        board = Board(". . .\n. wK .\n. . .")
        king = board.piece_at(1, 1)

        self.assertEqual(len(legal_destinations(board, king)), 8)

    def test_white_pawn_moves_and_captures_upward(self):
        board = Board("bR . .\n. wP .\n. . .")
        pawn = board.piece_at(1, 1)

        destinations = legal_destinations(board, pawn)

        self.assertIn(Position(0, 1), destinations)
        self.assertIn(Position(0, 0), destinations)

    def test_pawn_has_initial_two_step_from_start_rank(self):
        board = Board(". .\n. .\nwP .\n. .")
        pawn = board.piece_at(2, 0)

        destinations = legal_destinations(board, pawn)
        self.assertIn(Position(1, 0), destinations)
        self.assertIn(Position(0, 0), destinations)


if __name__ == "__main__":
    unittest.main()
