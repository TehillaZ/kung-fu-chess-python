import unittest

from kungfu_chess.model.board import Board
from kungfu_chess.rules.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()

    def test_valid_move_returns_ok(self):
        board = Board("wR .")

        validation = self.engine.validate_move(board, (0, 0), (0, 1))

        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.reason, "ok")

    def test_rejects_outside_board(self):
        board = Board("wR .")

        validation = self.engine.validate_move(board, (0, 0), (0, 2))

        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.reason, "outside_board")

    def test_rejects_empty_source(self):
        board = Board(". wR")

        validation = self.engine.validate_move(board, (0, 0), (0, 1))

        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.reason, "empty_source")

    def test_rejects_friendly_destination(self):
        board = Board("wR wP")

        validation = self.engine.validate_move(board, (0, 0), (0, 1))

        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.reason, "friendly_destination")

    def test_rejects_illegal_piece_move(self):
        board = Board("wR .\n. .")

        validation = self.engine.validate_move(board, (0, 0), (1, 1))

        self.assertFalse(validation.is_valid)
        self.assertEqual(validation.reason, "illegal_piece_move")

    def test_validate_move_legacy_signature_still_supported(self):
        board = Board("wR .")

        validation = self.engine.validate_move("wR", (0, 0), (0, 1), board)

        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.reason, "ok")

    def test_rule_engine_does_not_mutate_board(self):
        board = Board("wR .\n. .")

        self.engine.validate_move(board, (0, 0), (1, 1))

        self.assertEqual(board.cells, [["wR", "."], [".", "."]])


if __name__ == "__main__":
    unittest.main()
