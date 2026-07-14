import unittest

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.view.renderer import Renderer


class TestRenderer(unittest.TestCase):
    def test_renderer_does_not_mutate_engine_state(self):
        engine = GameEngine("wR .\n. .")
        engine.click(50, 50)
        engine.request_move((0, 0), (0, 1))
        engine.wait(250)

        before_board = [row[:] for row in engine.cells]
        before_clock = engine.clock
        before_selection = engine._controller.selected_pos
        before_pending = len(engine.pending_motions)
        snapshot = engine.snapshot()

        Renderer().render(snapshot)

        self.assertEqual(engine.cells, before_board)
        self.assertEqual(engine.clock, before_clock)
        self.assertEqual(engine._controller.selected_pos, before_selection)
        self.assertEqual(len(engine.pending_motions), before_pending)

    def test_renderer_formats_logical_board(self):
        engine = GameEngine("wR .\n. .")
        output = Renderer().render(engine.snapshot())

        self.assertEqual(output, "wR .\n. .")

    def test_renderer_appends_game_over(self):
        engine = GameEngine("wR bK")
        engine.request_move((0, 0), (0, 1))
        engine.wait(1000)

        output = Renderer().render(engine.snapshot())

        self.assertEqual(output, ". wR\nGAME OVER")


if __name__ == "__main__":
    unittest.main()
