from kungfu_chess.model.position import Position

PIECE_STATE_IDLE = "idle"
PIECE_STATE_MOVING = "moving"
PIECE_STATE_CAPTURED = "captured"

SPRITE_STATE_IDLE = "idle"
SPRITE_STATE_MOVE = "move"
SPRITE_STATE_JUMP = "jump"
SPRITE_STATE_WAIT = "wait"

COLOR_WHITE = "w"
COLOR_BLACK = "b"

KIND_KING = "K"
KIND_QUEEN = "Q"
KIND_ROOK = "R"
KIND_BISHOP = "B"
KIND_KNIGHT = "N"
KIND_PAWN = "P"

ALL_COLORS = (COLOR_WHITE, COLOR_BLACK)
ALL_KINDS = (
    KIND_KING,
    KIND_QUEEN,
    KIND_ROOK,
    KIND_BISHOP,
    KIND_KNIGHT,
    KIND_PAWN,
)

# Pawn promotion always becomes a queen in this game.
PROMOTION_KIND = KIND_QUEEN
WHITE_PROMOTION_ROW = 0
BLACK_PAWN_START_RANK = 1


def white_pawn_start_rank(board_rows):
    return board_rows - 2


def black_promotion_row(board_rows):
    return board_rows - 1


def is_white(color):
    return color == COLOR_WHITE


def is_black(color):
    return color == COLOR_BLACK


def make_token(color, kind):
    return f"{color}{kind}"


def all_piece_tokens():
    return {
        make_token(color, kind)
        for color in ALL_COLORS
        for kind in ALL_KINDS
    }


class Piece:
    """Logical chess piece with identity and lifecycle state."""

    def __init__(self, piece_id, color, kind, cell, state=PIECE_STATE_IDLE):
        self.id = piece_id
        self.color = color
        self.kind = kind
        self.cell = cell
        self.state = state

    @classmethod
    def from_token(cls, token, piece_id, cell):
        return cls(piece_id, token[0], token[1], cell)

    def to_token(self):
        return make_token(self.color, self.kind)

    def is_idle(self):
        return self.state == PIECE_STATE_IDLE

    def is_moving(self):
        return self.state == PIECE_STATE_MOVING

    def is_captured(self):
        return self.state == PIECE_STATE_CAPTURED

    def is_pawn(self):
        return self.kind == KIND_PAWN

    def is_king(self):
        return self.kind == KIND_KING

    def promote_if_needed(self, board_rows):
        """Promote a pawn that reached the opposite rank."""
        if not self.is_pawn():
            return False

        row = self.cell.row
        if is_white(self.color) and row == WHITE_PROMOTION_ROW:
            self.kind = PROMOTION_KIND
            return True

        if is_black(self.color) and row == black_promotion_row(board_rows):
            self.kind = PROMOTION_KIND
            return True

        return False

    def __repr__(self):
        return (
            f"Piece(id={self.id!r}, token={self.to_token()!r}, "
            f"cell={self.cell!r}, state={self.state!r})"
        )
