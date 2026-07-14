import io
import unittest
from contextlib import redirect_stdout

from kungfu_chess.engine.game_engine import GameEngine


class TestGameEngineIntegration(unittest.TestCase):
    def test_move_piece_on_empty_target(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR"], [".", "."]])

    def test_illegal_rook_move(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 100)
        self.assertEqual(engine.cells, [["wR", "."], [".", "."]])

    def test_wait_increments_clock(self):
        engine = GameEngine("wK .\n. .")
        engine.execute_wait(250)
        self.assertEqual(engine.clock, 250)

    def test_piece_stays_at_origin_before_arrival(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        self.assertEqual(engine.cells, [["wR", "."], [".", "."]])

    def test_piece_moves_after_enough_wait(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR"], [".", "."]])

    def test_piece_stays_during_partial_wait(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(500)
        self.assertEqual(engine.cells, [["wR", "."], [".", "."]])

    def test_print_board_before_arrival_shows_original_position(self):
        engine = GameEngine("wR .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            engine.print_board()
        self.assertEqual(buffer.getvalue().strip(), "wR .\n. .")

    def test_cannot_redirect_piece_while_moving(self):
        engine = GameEngine("wR . .")
        engine.execute_click(50, 50)
        engine.execute_click(250, 50)
        engine.execute_click(50, 50)
        engine.execute_click(150, 50)
        engine.execute_wait(2000)
        self.assertEqual(engine.cells, [[".", ".", "wR"]])

    def test_can_move_immediately_after_arrival(self):
        engine = GameEngine("wR . .")
        engine.execute_click(50, 50)
        engine.execute_click(150, 50)
        engine.execute_wait(1000)
        engine.execute_click(150, 50)
        engine.execute_click(250, 50)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", ".", "wR"]])

    def test_enemy_collision_capture_on_arrival(self):
        engine = GameEngine("wR bR")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR"]])

    def test_second_move_rejected_while_capture_motion_is_active(self):
        engine = GameEngine("wR . bR")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_click(200, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR", "bR"]])

    def test_capturing_enemy_king_ends_game(self):
        engine = GameEngine("wR bK")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertTrue(engine.game_over)
        self.assertEqual(engine.cells, [[".", "wR"]])

    def test_moves_ignored_after_game_over(self):
        engine = GameEngine("wR bK\nwN .")
        engine.execute_click(0, 0)
        engine.execute_click(100, 0)
        engine.execute_wait(1000)
        self.assertTrue(engine.game_over)
        engine.execute_click(0, 100)
        engine.execute_click(100, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR"], ["wN", "."]])


if __name__ == "__main__":
    unittest.main()
