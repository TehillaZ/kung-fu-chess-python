import unittest

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.model.game_snapshot import (
    GameSnapshot,
    PieceSnapshot,
    build_snapshot,
    cell_center_pixel,
    interpolate_motion_pixel,
)
from kungfu_chess.model.piece import PIECE_STATE_IDLE, PIECE_STATE_MOVING
from kungfu_chess.realtime.motion import Motion


class TestGameSnapshot(unittest.TestCase):
    def test_cell_center_pixel(self):
        self.assertEqual(cell_center_pixel(0, 0, 100), (50, 50))
        self.assertEqual(cell_center_pixel(1, 2, 100), (250, 150))

    def test_interpolate_motion_pixel_at_start(self):
        motion = Motion("wR", (0, 0), (0, 1), 0, 1000, 0)

        self.assertEqual(interpolate_motion_pixel(motion, 0, 100), (50, 50))

    def test_interpolate_motion_pixel_at_midpoint(self):
        motion = Motion("wR", (0, 0), (0, 1), 0, 1000, 0)

        self.assertEqual(interpolate_motion_pixel(motion, 500, 100), (100, 50))

    def test_snapshot_reflects_idle_board(self):
        engine = GameEngine("wR .\n. .")
        snapshot = engine.snapshot()

        self.assertEqual(snapshot.rows, 2)
        self.assertEqual(snapshot.cols, 2)
        self.assertEqual(snapshot.cell_size, 100)
        self.assertFalse(snapshot.game_over)
        self.assertIsNone(snapshot.selected_row)
        self.assertEqual(len(snapshot.pieces), 1)
        self.assertEqual(snapshot.pieces[0].state, PIECE_STATE_IDLE)
        self.assertEqual((snapshot.pieces[0].pixel_x, snapshot.pieces[0].pixel_y), (50, 50))

    def test_snapshot_includes_selection(self):
        engine = GameEngine("wR .\n. .")
        engine.click(50, 50)

        snapshot = engine.snapshot()

        self.assertEqual(snapshot.selected_row, 0)
        self.assertEqual(snapshot.selected_col, 0)

    def test_snapshot_marks_active_motion_and_interpolates_pixels(self):
        engine = GameEngine("wR .\n. .")
        engine.request_move((0, 0), (0, 1))
        engine.wait(500)

        snapshot = engine.snapshot()
        moving = snapshot.pieces[0]

        self.assertEqual(moving.state, PIECE_STATE_MOVING)
        self.assertEqual((moving.logical_row, moving.logical_col), (0, 0))
        self.assertEqual((moving.pixel_x, moving.pixel_y), (100, 50))

    def test_snapshot_reports_game_over(self):
        engine = GameEngine("wR bK")
        engine.request_move((0, 0), (0, 1))
        engine.wait(1000)

        snapshot = engine.snapshot()

        self.assertTrue(snapshot.game_over)

    def test_build_snapshot_is_read_only_view(self):
        engine = GameEngine("wR .\n. .")
        snapshot = build_snapshot(
            engine._board,
            engine._game_state,
            engine._controller,
            engine._arbiter,
        )

        self.assertIsInstance(snapshot, GameSnapshot)
        self.assertIsInstance(snapshot.pieces[0], PieceSnapshot)


if __name__ == "__main__":
    unittest.main()
