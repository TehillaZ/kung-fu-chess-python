import unittest

from kungfu_chess.engine.game_engine import GameEngine


class TestPawnMovement(unittest.TestCase):
    def test_white_pawn_moves_upward(self):
        engine = GameEngine(". .\n. .\nwP .")
        engine.execute_click(0, 200)
        engine.execute_click(0, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "."], ["wP", "."], [".", "."]])

    def test_black_pawn_moves_downward(self):
        engine = GameEngine("bP .\n. .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(0, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "."], ["bP", "."], [".", "."]])

    def test_pawn_captures_diagonally(self):
        engine = GameEngine(". .\n. bR\nwP .")
        engine.execute_click(0, 200)
        engine.execute_click(100, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "."], [".", "wP"], [".", "."]])

    def test_pawn_cannot_move_two_cells_when_not_on_start_rank(self):
        engine = GameEngine(". .\n. .\nwP .")
        engine.execute_click(0, 200)
        engine.execute_click(0, 0)
        engine.execute_wait(2000)
        self.assertEqual(engine.cells, [[".", "."], [".", "."], ["wP", "."]])

    def test_white_pawn_double_from_start_valid(self):
        engine = GameEngine(". . .\n. . .\n. . .\n. wP .\n. . .")
        engine.execute_click(150, 350)
        engine.execute_click(150, 150)
        engine.execute_wait(2000)
        self.assertEqual(
            engine.cells,
            [
                [".", ".", "."],
                [".", "wP", "."],
                [".", ".", "."],
                [".", ".", "."],
                [".", ".", "."],
            ],
        )

    def test_black_pawn_double_from_start_valid(self):
        engine = GameEngine(". . .\n. bP .\n. . .\n. . .\n. . .")
        engine.execute_click(150, 150)
        engine.execute_click(150, 350)
        engine.execute_wait(2000)
        self.assertEqual(
            engine.cells,
            [
                [".", ".", "."],
                [".", ".", "."],
                [".", ".", "."],
                [".", "bP", "."],
                [".", ".", "."],
            ],
        )

    def test_pawn_two_cell_move_blocked_if_path_not_clear(self):
        engine = GameEngine(". .\n. .\nwR .\nwP .")
        engine.execute_click(0, 300)
        engine.execute_click(0, 100)
        engine.execute_wait(2000)
        self.assertEqual(engine.cells, [[".", "."], [".", "."], ["wR", "."], ["wP", "."]])

    def test_white_pawn_promotes_to_queen(self):
        engine = GameEngine(". .\nwP .")
        engine.execute_click(0, 100)
        engine.execute_click(0, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [["wQ", "."], [".", "."]])

    def test_black_pawn_promotes_to_queen(self):
        engine = GameEngine("bP .\n. .")
        engine.execute_click(0, 0)
        engine.execute_click(0, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "."], ["bQ", "."]])

    def test_promoted_queen_moves_diagonal(self):
        engine = GameEngine(". . .\n. wP .\n. . .")
        engine.execute_click(150, 150)
        engine.execute_click(150, 50)
        engine.execute_wait(1000)
        engine.execute_click(150, 50)
        engine.execute_click(250, 150)
        engine.execute_wait(1000)
        self.assertEqual(
            engine.cells,
            [[".", ".", "."], [".", ".", "wQ"], [".", ".", "."]],
        )

    def test_pawn_cannot_capture_forward(self):
        engine = GameEngine("bR .\nwP .\n. .")
        engine.execute_click(0, 100)
        engine.execute_click(0, 0)
        self.assertEqual(engine.cells, [["bR", "."], ["wP", "."], [".", "."]])


if __name__ == "__main__":
    unittest.main()
