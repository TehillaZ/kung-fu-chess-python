from kungfu_chess.model.board import EMPTY_CELL


class GameState:
    """Holds runtime game state such as clock and game-over flag."""

    def __init__(self):
        self.clock = 0
        self.game_over = False

    def advance_clock(self, milliseconds):
        self.clock += milliseconds

    def end_game(self):
        self.game_over = True


def is_king(piece):
    return len(piece) == 2 and piece[1] == "K"


def is_king_capture(target_piece):
    return target_piece != EMPTY_CELL and is_king(target_piece)
