import unittest

from kungfu_chess.engine.game_engine import GameEngine


class TestKnightMovement(unittest.TestCase):
    def test_knight_move_lasts_1000ms(self):
        engine = GameEngine("wN . .\n. . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        engine.execute_wait(500)
        self.assertEqual(engine.cells, [["wN", ".", "."], [".", ".", "."], [".", ".", "."]])
        engine.execute_wait(500)
        self.assertEqual(engine.cells, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_knight_stays_at_origin_during_move(self):
        engine = GameEngine("wN . .\n. . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        self.assertEqual(engine.cells, [["wN", ".", "."], [".", ".", "."], [".", ".", "."]])

    def test_knight_lands_normally_when_no_enemy_arrives(self):
        engine = GameEngine("wN . .\n. . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_second_move_rejected_while_knight_is_moving(self):
        engine = GameEngine("wN . .\nbR . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        engine.execute_click(0, 100)
        engine.execute_click(0, 0)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", ".", "."], ["bR", ".", "wN"], [".", ".", "."]])

    def test_moving_knight_cannot_start_second_move(self):
        engine = GameEngine("wN . .\n. . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        engine.execute_click(0, 0)
        engine.execute_click(100, 200)
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_removed_piece_does_not_arrive(self):
        engine = GameEngine("wN . .\n. . .\n. . .")
        engine.execute_click(0, 0)
        engine.execute_click(200, 100)
        engine._board.set_piece(0, 0, ".")
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", ".", "."], [".", ".", "."], [".", ".", "."]])


if __name__ == "__main__":
    unittest.main()
