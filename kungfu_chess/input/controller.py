from kungfu_chess.rules.piece_rules import is_friendly_piece


class Controller:
    """Handles click selection and move scheduling."""

    def __init__(self, board, rule_engine, arbiter, game_state):
        self._board = board
        self._rule_engine = rule_engine
        self._arbiter = arbiter
        self._game_state = game_state
        self.selected_pos = None
        self.pending_motions = []
        self._move_order = 0

    def has_pending_move_from(self, position):
        return any(motion.start == position for motion in self.pending_motions)

    def handle_click(self, position):
        if self._game_state.game_over or position is None:
            return

        row, col = position.as_tuple()

        if self.selected_pos is None:
            if not self._board.is_empty(row, col):
                self.selected_pos = (row, col)
            return

        previous_position = self.selected_pos
        piece = self._board.get_piece(*previous_position)
        target_piece = self._board.get_piece(row, col)

        if is_friendly_piece(piece, target_piece):
            self.selected_pos = (row, col)
            return

        if self._rule_engine.is_legal_move(
            piece,
            previous_position,
            (row, col),
            self._board,
        ):
            if not self.has_pending_move_from(previous_position):
                motion = self._arbiter.create_motion(
                    piece,
                    previous_position,
                    (row, col),
                    self._game_state.clock,
                    self.pending_motions,
                    self._move_order,
                )
                self.pending_motions.append(motion)
                self._move_order += 1

        self.selected_pos = None

    def clear_selection(self):
        self.selected_pos = None

    def clear_pending_motions(self):
        self.pending_motions = []
