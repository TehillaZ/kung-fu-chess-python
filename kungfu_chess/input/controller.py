from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.rules.piece_rules import piece_color


class Controller:
    """Handles click selection and delegates move requests to GameEngine."""

    def __init__(self, board, game_engine, game_state):
        self._board = board
        self._game_engine = game_engine
        self._game_state = game_state
        self.selected_pos = None

    def click(self, position):
        self.handle_click(position)

    def handle_click(self, position):
        if self._game_state.game_over:
            return

        if position is None:
            if self.selected_pos is not None:
                self.selected_pos = None
            return

        row, col = position.as_tuple()

        if self.selected_pos is None:
            if not self._board.is_empty(row, col):
                self.selected_pos = (row, col)
            return

        source = self.selected_pos
        if source != (row, col) and not self._board.is_empty(row, col):
            selected_piece = self._board.get_piece(*source)
            clicked_piece = self._board.get_piece(row, col)
            if (
                selected_piece != EMPTY_CELL
                and clicked_piece != EMPTY_CELL
                and piece_color(selected_piece) == piece_color(clicked_piece)
            ):
                self.selected_pos = (row, col)
                return

        self._game_engine.request_move(source, (row, col))
        self.selected_pos = None

    def handle_jump(self, position):
        self._game_engine.request_jump(position)

    def clear_selection(self):
        self.selected_pos = None
