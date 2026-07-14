import unittest

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
from kungfu_chess.rules.rule_engine import MoveValidation


class FakeRuleEngine:
    def __init__(self, validation):
        self.validation = validation
        self.calls = []

    def validate_move(self, board, source, destination):
        self.calls.append((board, source, destination))
        return self.validation


class FakeArbiter:
    def __init__(self, active=False):
        self.active = active
        self.started_motions = []

    def has_active_motion(self):
        return self.active

    def start_motion(self, piece, start, end, clock):
        self.started_motions.append((piece, start, end, clock))
        self.active = True

    @property
    def pending_motions(self):
        return []


class GameEngineForTest(GameEngine):
    def __init__(self, board_setup, rule_engine, arbiter):
        self._board = Board(board_setup)
        self.board = self._board
        self._game_state = GameState()
        self._rule_engine = rule_engine
        self._arbiter = arbiter
        self._mapper = BoardMapper(self._board)
        self._controller = Controller(self._board, self, self._game_state)
        self._printer = BoardPrinter()


class TestGameEngine(unittest.TestCase):
    def test_request_move_delegates_validation_to_rule_engine(self):
        rule_engine = FakeRuleEngine(MoveValidation(True, "ok"))
        arbiter = FakeArbiter()
        engine = GameEngineForTest("wR .", rule_engine, arbiter)

        result = engine.request_move((0, 0), (0, 1))

        self.assertTrue(result.is_accepted)
        self.assertEqual(result.reason, "ok")
        self.assertEqual(len(rule_engine.calls), 1)
        self.assertEqual(arbiter.started_motions, [("wR", (0, 0), (0, 1), 0)])

    def test_invalid_command_does_not_start_motion(self):
        rule_engine = FakeRuleEngine(MoveValidation(False, "illegal_piece_move"))
        arbiter = FakeArbiter()
        engine = GameEngineForTest("wR .", rule_engine, arbiter)

        result = engine.request_move((0, 0), (1, 1))

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "illegal_piece_move")
        self.assertEqual(arbiter.started_motions, [])
        self.assertEqual(engine.cells, [["wR", "."]])

    def test_rejects_game_over_before_validation(self):
        rule_engine = FakeRuleEngine(MoveValidation(True, "ok"))
        arbiter = FakeArbiter()
        engine = GameEngineForTest("wR .", rule_engine, arbiter)
        engine._game_state.end_game()

        result = engine.request_move((0, 0), (0, 1))

        self.assertEqual(result, MoveResult(False, "game_over"))
        self.assertEqual(rule_engine.calls, [])
        self.assertEqual(arbiter.started_motions, [])

    def test_rejects_motion_in_progress_before_validation(self):
        rule_engine = FakeRuleEngine(MoveValidation(True, "ok"))
        arbiter = FakeArbiter(active=True)
        engine = GameEngineForTest("wR .", rule_engine, arbiter)

        result = engine.request_move((0, 0), (0, 1))

        self.assertEqual(result, MoveResult(False, "motion_in_progress"))
        self.assertEqual(rule_engine.calls, [])
        self.assertEqual(arbiter.started_motions, [])

    def test_board_unchanged_on_invalid_request(self):
        engine = GameEngine("wR .\n. .")
        before = [row[:] for row in engine.cells]

        engine.request_move((0, 0), (1, 1))

        self.assertEqual(engine.cells, before)

    def test_board_unchanged_on_click_before_wait(self):
        engine = GameEngine("wR .\n. .")
        before = [row[:] for row in engine.cells]

        engine.execute_click(0, 0)
        engine.execute_click(100, 0)

        self.assertEqual(engine.cells, before)
        self.assertTrue(engine._arbiter.has_active_motion())

    def test_king_capture_ends_game_and_clears_pending_motions(self):
        engine = GameEngine("wR bK\nwR .")
        engine.request_move((0, 0), (0, 1))
        engine.execute_wait(1000)

        self.assertTrue(engine.game_over)
        self.assertFalse(engine._arbiter.has_active_motion())
        self.assertEqual(engine.cells, [[".", "wR"], ["wR", "."]])

    def test_request_move_rejected_after_king_capture(self):
        engine = GameEngine("wR bK")
        engine.request_move((0, 0), (0, 1))
        engine.execute_wait(1000)

        result = engine.request_move((0, 0), (0, 1))

        self.assertEqual(result, MoveResult(False, "game_over"))


if __name__ == "__main__":
    unittest.main()
