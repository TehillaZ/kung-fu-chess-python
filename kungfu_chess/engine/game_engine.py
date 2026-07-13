from kungfu_chess.input.board_mapper import BoardMapper
from kungfu_chess.input.controller import Controller
from kungfu_chess.io.board_printer import BoardPrinter
from kungfu_chess.model.board import Board
from kungfu_chess.model.game_state import GameState
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
        self._controller = Controller(
            self._board,
            self._rule_engine,
            self._arbiter,
            self._game_state,
        )
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

    def execute_click(self, x, y):
        position = self._mapper.to_position(x, y)
        self._controller.handle_click(position)

    def execute_wait(self, milliseconds):
        self._game_state.advance_clock(milliseconds)
        self._apply_completed_motions()

    def print_board(self):
        self._printer.print_board(self._board)

    def _apply_completed_motions(self):
        pending_motions, king_captured = self._arbiter.apply_completed_motions(
            self._board,
            self._controller.pending_motions,
            self._game_state.clock,
            self._rule_engine,
        )
        self._controller.pending_motions = pending_motions

        if king_captured:
            self._game_state.end_game()
            self._controller.clear_pending_motions()
            self._controller.clear_selection()


class ChessGameSimulator(GameEngine):
    """Backward-compatible alias used by existing tests."""

    def __init__(self, board_setup):
        super().__init__(board_setup)
        self.board = self._board.cells
