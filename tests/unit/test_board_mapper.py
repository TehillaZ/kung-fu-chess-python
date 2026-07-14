import unittest

from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.model.board import Board
from kungfu_chess.model.position import Position


class TestBoardMapper(unittest.TestCase):
    def setUp(self):
        self.board = Board("wK . .\n. . .")
        self.mapper = BoardMapper(self.board)

    def test_click_50_50_maps_to_row_0_col_0(self):
        self.assertEqual(self.mapper.pixel_to_cell(50, 50), Position(0, 0))

    def test_click_150_50_maps_to_row_0_col_1(self):
        self.assertEqual(self.mapper.pixel_to_cell(150, 50), Position(0, 1))

    def test_click_50_150_maps_to_row_1_col_0(self):
        self.assertEqual(self.mapper.pixel_to_cell(50, 150), Position(1, 0))

    def test_x_0_to_99_maps_to_column_0(self):
        self.assertEqual(self.mapper.pixel_to_cell(0, 0), Position(0, 0))
        self.assertEqual(self.mapper.pixel_to_cell(99, 0), Position(0, 0))

    def test_x_100_to_199_maps_to_column_1(self):
        self.assertEqual(self.mapper.pixel_to_cell(100, 0), Position(0, 1))
        self.assertEqual(self.mapper.pixel_to_cell(199, 0), Position(0, 1))

    def test_y_100_to_199_maps_to_row_1(self):
        self.assertEqual(self.mapper.pixel_to_cell(0, 100), Position(1, 0))
        self.assertEqual(self.mapper.pixel_to_cell(0, 199), Position(1, 0))

    def test_outside_click_returns_none(self):
        self.assertIsNone(self.mapper.pixel_to_cell(300, 50))
        self.assertIsNone(self.mapper.pixel_to_cell(50, 300))

    def test_to_position_alias(self):
        self.assertEqual(self.mapper.to_position(150, 150), Position(1, 1))


if __name__ == "__main__":
    unittest.main()
