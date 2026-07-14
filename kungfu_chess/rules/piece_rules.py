from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.model.piece import (
    BLACK_PAWN_START_RANK,
    KIND_BISHOP,
    KIND_KING,
    KIND_KNIGHT,
    KIND_PAWN,
    KIND_QUEEN,
    KIND_ROOK,
    is_white,
    white_pawn_start_rank,
)
from kungfu_chess.model.position import Position

SLIDING_DIRECTIONS = {
    KIND_ROOK: ((-1, 0), (1, 0), (0, -1), (0, 1)),
    KIND_BISHOP: ((-1, -1), (-1, 1), (1, -1), (1, 1)),
    KIND_QUEEN: (
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1),
    ),
}
KING_DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
)
KNIGHT_DELTAS = (
    (-2, -1), (-2, 1), (-1, -2), (-1, 2),
    (1, -2), (1, 2), (2, -1), (2, 1),
)


def is_friendly_piece(moving_piece, target_piece):
    return (
        target_piece != EMPTY_CELL
        and piece_color(moving_piece) == piece_color(target_piece)
    )


def can_capture(moving_piece, target_piece):
    if target_piece == EMPTY_CELL:
        return True

    return piece_color(moving_piece) != piece_color(target_piece)


def piece_color(piece):
    if hasattr(piece, "color"):
        return piece.color
    return piece[0]


def piece_kind(piece):
    if hasattr(piece, "kind"):
        return piece.kind
    return piece[1] if len(piece) == 2 else piece


def piece_cell(piece, fallback=None):
    if hasattr(piece, "cell"):
        return piece.cell.as_tuple()
    return fallback


def target_token(board, row, col):
    if not board.is_within_bounds(row, col):
        return EMPTY_CELL
    return board.get_piece(row, col)


def add_if_legal_destination(destinations, board, piece, row, col):
    if not board.is_within_bounds(row, col):
        return

    target_piece = target_token(board, row, col)
    if can_capture(piece, target_piece):
        destinations.add(Position(row, col))


def legal_destinations_for_sliding_piece(board, piece, directions):
    destinations = set()
    start_row, start_col = piece_cell(piece)

    for row_step, col_step in directions:
        row = start_row + row_step
        col = start_col + col_step

        while board.is_within_bounds(row, col):
            target_piece = target_token(board, row, col)

            if target_piece == EMPTY_CELL:
                destinations.add(Position(row, col))
            else:
                if can_capture(piece, target_piece):
                    destinations.add(Position(row, col))
                break

            row += row_step
            col += col_step

    return destinations


def legal_destinations_for_king(board, piece):
    destinations = set()
    start_row, start_col = piece_cell(piece)

    for row_delta, col_delta in KING_DIRECTIONS:
        add_if_legal_destination(
            destinations,
            board,
            piece,
            start_row + row_delta,
            start_col + col_delta,
        )

    return destinations


def legal_destinations_for_knight(board, piece):
    destinations = set()
    start_row, start_col = piece_cell(piece)

    for row_delta, col_delta in KNIGHT_DELTAS:
        add_if_legal_destination(
            destinations,
            board,
            piece,
            start_row + row_delta,
            start_col + col_delta,
        )

    return destinations


def is_pawn_on_start_rank(board, color, row):
    if is_white(color):
        return row == white_pawn_start_rank(board.rows())
    return row == BLACK_PAWN_START_RANK


def pawn_forward_delta(color):
    return -1 if is_white(color) else 1


def legal_destinations_for_pawn(board, piece):
    destinations = set()
    color = piece_color(piece)
    start_row, start_col = piece_cell(piece)
    forward = pawn_forward_delta(color)

    forward_row = start_row + forward
    if board.is_within_bounds(forward_row, start_col):
        if target_token(board, forward_row, start_col) == EMPTY_CELL:
            destinations.add(Position(forward_row, start_col))

            double_row = start_row + 2 * forward
            if (
                is_pawn_on_start_rank(board, color, start_row)
                and board.is_within_bounds(double_row, start_col)
                and target_token(board, double_row, start_col) == EMPTY_CELL
            ):
                destinations.add(Position(double_row, start_col))

    for col_delta in (-1, 1):
        capture_row = start_row + forward
        capture_col = start_col + col_delta
        if not board.is_within_bounds(capture_row, capture_col):
            continue

        target_piece = target_token(board, capture_row, capture_col)
        if target_piece != EMPTY_CELL and can_capture(piece, target_piece):
            destinations.add(Position(capture_row, capture_col))

    return destinations


def legal_destinations(board, piece):
    piece_type = piece_kind(piece)

    if piece_type in SLIDING_DIRECTIONS:
        return legal_destinations_for_sliding_piece(
            board,
            piece,
            SLIDING_DIRECTIONS[piece_type],
        )
    if piece_type == KIND_KNIGHT:
        return legal_destinations_for_knight(board, piece)
    if piece_type == KIND_KING:
        return legal_destinations_for_king(board, piece)
    if piece_type == KIND_PAWN:
        return legal_destinations_for_pawn(board, piece)

    return set()


def is_piece_move_legal(piece, start, end, board):
    if not hasattr(piece, "cell"):
        piece = board.piece_at(*start)

    if piece is None:
        return False

    return Position(*end) in legal_destinations(board, piece)


def is_pawn_move_legal(piece, start, end, board):
    return is_piece_move_legal(piece, start, end, board)


def build_piece_validators(rules_loader=None):
    return {
        KIND_KING: is_piece_move_legal,
        KIND_ROOK: is_piece_move_legal,
        KIND_BISHOP: is_piece_move_legal,
        KIND_QUEEN: is_piece_move_legal,
        KIND_KNIGHT: is_piece_move_legal,
        KIND_PAWN: is_pawn_move_legal,
    }
