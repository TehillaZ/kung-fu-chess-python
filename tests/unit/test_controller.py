import unittest

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.input.controller import Controller
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.position import Position


class FakeGameEngine:
    def __init__(self):
        self.move_requests = []

    def request_move(self, source, destination):
        self.move_requests.append((source, destination))
        return MoveResult(True, "ok")


class TestController(unittest.TestCase):
    def setUp(self):
        self.board = Board("wK . .\n. bR .")
        self.game_engine = FakeGameEngine()
        self.game_state = GameState()
        self.controller = Controller(self.board, self.game_engine, self.game_state)

    def test_first_click_on_piece_selects_it(self):
        self.controller.click(Position(0, 0))

        self.assertEqual(self.controller.selected_pos, (0, 0))
        self.assertEqual(self.game_engine.move_requests, [])

    def test_first_click_on_empty_cell_does_nothing(self):
        self.controller.click(Position(0, 1))

        self.assertIsNone(self.controller.selected_pos)
        self.assertEqual(self.game_engine.move_requests, [])

    def test_outside_click_with_no_selection_is_ignored(self):
        self.controller.click(None)

        self.assertIsNone(self.controller.selected_pos)
        self.assertEqual(self.game_engine.move_requests, [])

    def test_outside_click_with_selection_clears_selection(self):
        self.controller.click(Position(0, 0))
        self.controller.click(None)

        self.assertIsNone(self.controller.selected_pos)
        self.assertEqual(self.game_engine.move_requests, [])

    def test_second_click_requests_move_and_clears_selection(self):
        self.controller.click(Position(0, 0))
        self.controller.click(Position(1, 1))

        self.assertEqual(self.game_engine.move_requests, [((0, 0), (1, 1))])
        self.assertIsNone(self.controller.selected_pos)

    def test_second_click_clears_selection_after_invalid_destination(self):
        self.controller.click(Position(0, 0))
        self.controller.click(Position(0, 0))

        self.assertEqual(self.game_engine.move_requests, [((0, 0), (0, 0))])
        self.assertIsNone(self.controller.selected_pos)

    def test_second_click_on_friendly_piece_replaces_selection(self):
        self.board.set_piece(0, 1, "wR")
        self.controller.click(Position(0, 0))
        self.controller.click(Position(0, 1))

        self.assertEqual(self.controller.selected_pos, (0, 1))
        self.assertEqual(self.game_engine.move_requests, [])

    def test_clicking_another_piece_replaces_selection_and_moves(self):
        engine = GameEngine("wR . wK\n. . .")
        engine.execute_click(50, 50)
        engine.execute_click(250, 50)
        engine.execute_click(250, 150)
        engine.execute_wait(1000)

        self.assertEqual(engine.cells, [["wR", ".", "."], [".", ".", "wK"]])

    def test_clicks_ignored_after_game_over(self):
        self.game_state.end_game()
        self.controller.click(Position(0, 0))
        self.controller.click(Position(1, 1))

        self.assertEqual(self.game_engine.move_requests, [])

    def test_illegal_move_clears_selection_with_real_engine(self):
        engine = GameEngine("wR .\n. .")
        controller = engine._controller

        controller.click(engine._mapper.pixel_to_cell(50, 50))
        controller.click(engine._mapper.pixel_to_cell(150, 150))

        self.assertIsNone(controller.selected_pos)


if __name__ == "__main__":
    unittest.main()
