import unittest

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.move_result import MoveResult
from tests.integration.text_script import run_text_script


class TestInvalidMoves(unittest.TestCase):
    def setUp(self):
        self.engine = GameEngine("wR wP .\n. . .")

    def test_rejects_outside_board_destination(self):
        result = self.engine.request_move((0, 0), (0, 3))

        self.assertEqual(result, MoveResult(False, "outside_board"))

    def test_rejects_empty_source(self):
        result = self.engine.request_move((1, 2), (0, 0))

        self.assertEqual(result, MoveResult(False, "empty_source"))

    def test_rejects_friendly_destination(self):
        result = self.engine.request_move((0, 0), (0, 1))

        self.assertEqual(result, MoveResult(False, "friendly_destination"))

    def test_rejects_blocked_rook_path(self):
        result = self.engine.request_move((0, 0), (0, 2))

        self.assertEqual(result, MoveResult(False, "illegal_piece_move"))

    def test_rejects_diagonal_rook_move(self):
        engine = GameEngine("wR .\n. .")

        result = engine.request_move((0, 0), (1, 1))

        self.assertEqual(result, MoveResult(False, "illegal_piece_move"))

    def test_invalid_request_does_not_mutate_board(self):
        before = [row[:] for row in self.engine.cells]

        self.engine.request_move((0, 0), (0, 2))

        self.assertEqual(self.engine.cells, before)
        self.assertFalse(self.engine._arbiter.has_active_motion())

    def test_illegal_click_sequence_does_not_mutate_board(self):
        engine = GameEngine("wR .\n. .")
        before = [row[:] for row in engine.cells]

        engine.click(50, 50)
        engine.click(150, 150)
        engine.wait(1000)

        self.assertEqual(engine.cells, before)
        self.assertIsNone(engine._controller.selected_pos)

    def test_spec_iteration_eight_blocked_rook_path_unchanged_after_wait(self):
        input_data = """Board:
wR wP .
. . .
Commands:
click 50 50
click 250 50
wait 1000
print board"""
        self.assertEqual(
            run_text_script(input_data),
            "wR wP .\n. . .",
        )


if __name__ == "__main__":
    unittest.main()
