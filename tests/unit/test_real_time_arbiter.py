import unittest

from kungfu_chess.model.board import Board
from kungfu_chess.realtime.arrival_events import ArrivalEvents
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine


class TestRealTimeArbiter(unittest.TestCase):
    def setUp(self):
        self.board = Board("wR .\n. .")
        self.rule_engine = RuleEngine()
        self.arbiter = RealTimeArbiter()

    def test_piece_has_not_arrived_after_999_ms(self):
        self.arbiter.start_motion("wR", (0, 0), (0, 1), clock=0)

        events = self.arbiter.advance_time(self.board, 999, self.rule_engine)

        self.assertEqual(events, ArrivalEvents(king_captured=False))
        self.assertEqual(self.board.cells, [["wR", "."], [".", "."]])
        self.assertTrue(self.arbiter.has_active_motion())

    def test_piece_arrives_after_1000_ms_for_one_square(self):
        self.arbiter.start_motion("wR", (0, 0), (0, 1), clock=0)

        events = self.arbiter.advance_time(self.board, 1000, self.rule_engine)

        self.assertEqual(events, ArrivalEvents(king_captured=False))
        self.assertEqual(self.board.cells, [[".", "wR"], [".", "."]])
        self.assertFalse(self.arbiter.has_active_motion())

    def test_two_square_move_arrives_after_2000_ms(self):
        board = Board("wR . .")
        arbiter = RealTimeArbiter()
        arbiter.start_motion("wR", (0, 0), (0, 2), clock=0)

        arbiter.advance_time(board, 1000, self.rule_engine)
        self.assertEqual(board.cells, [["wR", ".", "."]])

        arbiter.advance_time(board, 2000, self.rule_engine)
        self.assertEqual(board.cells, [[".", ".", "wR"]])

    def test_partial_waits_equal_one_full_wait(self):
        arbiter = RealTimeArbiter()
        arbiter.start_motion("wR", (0, 0), (0, 1), clock=0)

        arbiter.advance_time(self.board, 400, self.rule_engine)
        arbiter.advance_time(self.board, 1000, self.rule_engine)

        self.assertEqual(self.board.cells, [[".", "wR"], [".", "."]])

    def test_motion_starts_immediately_at_current_clock(self):
        motion = self.arbiter.start_motion("wR", (0, 0), (0, 1), clock=250)

        self.assertEqual(motion.departure_time, 250)
        self.assertEqual(motion.arrival_time, 1250)

    def test_second_motion_not_scheduled_while_first_is_active(self):
        from kungfu_chess.engine.game_engine import GameEngine

        engine = GameEngine("wR .\n. bR")
        engine.request_move((0, 0), (0, 1))
        result = engine.request_move((1, 0), (1, 1))

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "motion_in_progress")
        engine.execute_wait(1000)
        self.assertEqual(engine.cells, [[".", "wR"], [".", "bR"]])

    def test_capture_on_arrival_removes_enemy_piece(self):
        board = Board("wR bR")
        arbiter = RealTimeArbiter()
        arbiter.start_motion("wR", (0, 0), (0, 1), clock=0)

        events = arbiter.advance_time(board, 1000, self.rule_engine)

        self.assertEqual(events, ArrivalEvents(king_captured=False))
        self.assertEqual(board.cells, [[".", "wR"]])

    def test_king_capture_reports_event(self):
        board = Board("wR bK")
        arbiter = RealTimeArbiter()
        arbiter.start_motion("wR", (0, 0), (0, 1), clock=0)

        events = arbiter.advance_time(board, 1000, self.rule_engine)

        self.assertEqual(events, ArrivalEvents(king_captured=True))
        self.assertEqual(board.cells, [[".", "wR"]])

    def test_knight_move_takes_1000_ms_regardless_of_distance(self):
        board = Board("wN . .\n. . .\n. . .")
        arbiter = RealTimeArbiter()
        arbiter.start_motion("wN", (0, 0), (2, 1), clock=0)

        arbiter.advance_time(board, 999, self.rule_engine)
        self.assertEqual(board.cells[0][0], "wN")

        arbiter.advance_time(board, 1000, self.rule_engine)
        self.assertEqual(board.get_piece(2, 1), "wN")


if __name__ == "__main__":
    unittest.main()
