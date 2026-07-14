from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_snapshot import build_snapshot
from kungfu_chess.model.game_state import GameState
from kungfu_chess.model.position import as_tuple
from kungfu_chess.realtime.real_time_arbiter import RealTimeArbiter
from kungfu_chess.rules.rule_engine import RuleEngine


class GameEngine:
    """Coordinates controller, rules, and real-time movement."""

    def __init__(self, board_setup):
        self._board = Board(board_setup)
        self.board = self._board
        self._game_state = GameState()
        self._rule_engine = RuleEngine()
        self._arbiter = RealTimeArbiter()
        self._mapper = BoardMapper(self._board)
        self._controller = Controller(self._board, self, self._game_state)
        self._printer = BoardPrinter()

    @property
    def cells(self):
        return self._board.cells

    @property
    def clock(self):
        return self._game_state.clock

    @property
    def game_over(self):
        return self._game_state.game_over

    @property
    def pending_motions(self):
        return self._arbiter.pending_motions

    def request_move(self, source, destination):
        if self._game_state.game_over:
            return MoveResult(False, "game_over")

        if self._arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")

        source = as_tuple(source)
        destination = as_tuple(destination)

        validation = self._rule_engine.validate_move(
            self._board,
            source,
            destination,
        )
        if not validation.is_valid:
            return MoveResult(False, validation.reason)

        piece = self._board.get_piece(*source)
        self._arbiter.start_motion(
            piece,
            source,
            destination,
            self._game_state.clock,
        )
        return MoveResult(True, "ok")

    def request_jump(self, position):
        if self._game_state.game_over:
            return MoveResult(False, "game_over")

        if position is None:
            return MoveResult(False, "outside_board")

        if self._arbiter.has_active_motion():
            return MoveResult(False, "motion_in_progress")

        row, col = position.as_tuple()

        if self._board.is_empty(row, col):
            return MoveResult(False, "empty_source")

        piece = self._board.get_piece(row, col)
        self._arbiter.start_jump(piece, (row, col), self._game_state.clock)
        return MoveResult(True, "ok")

    def execute_click(self, x, y):
        position = self._mapper.pixel_to_cell(x, y)
        self._controller.click(position)

    def execute_jump(self, x, y):
        position = self._mapper.pixel_to_cell(x, y)
        self._controller.handle_jump(position)

    def click(self, x, y):
        """Pixel click entry point used by the text runner."""
        self.execute_click(x, y)

    def wait(self, milliseconds):
        """Advance simulated time and apply completed motions."""
        self.execute_wait(milliseconds)

    def execute_wait(self, milliseconds):
        self._game_state.advance_clock(milliseconds)
        self._apply_completed_motions()

    def print_board(self):
        self._printer.print_board(self._board)

    def snapshot(self):
        """Return a read-only view of the current game state for rendering."""
        return build_snapshot(
            self._board,
            self._game_state,
            self._controller,
            self._arbiter,
        )

    def _apply_completed_motions(self):
        events = self._arbiter.advance_time(
            self._board,
            self._game_state.clock,
            self._rule_engine,
        )

        if events.king_captured:
            self._game_state.end_game()
            self._arbiter.clear_pending_motions()
            self._controller.clear_selection()
