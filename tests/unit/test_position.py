import unittest

from kungfu_chess.model.position import Position


class TestPosition(unittest.TestCase):
    def test_equal_positions_are_equal(self):
        self.assertEqual(Position(1, 2), Position(1, 2))

    def test_different_positions_are_not_equal(self):
        self.assertNotEqual(Position(0, 0), Position(0, 1))
        self.assertNotEqual(Position(0, 0), Position(1, 0))

    def test_position_equals_tuple(self):
        self.assertEqual(Position(2, 3), (2, 3))

    def test_position_repr_is_readable(self):
        self.assertEqual(repr(Position(1, 4)), "Position(row=1, col=4)")


if __name__ == "__main__":
    unittest.main()
