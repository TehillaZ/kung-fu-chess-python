from board import EMPTY_CELL


def is_pawn_move_legal(piece, start, end, board):
    color = piece[0]
    start_row, start_col = start
    end_row, end_col = end

    delta_row = end_row - start_row
    delta_col = end_col - start_col
    forward = -1 if color == "w" else 1

    target_piece = board.get_piece(end_row, end_col)

    if delta_col == 0 and delta_row == forward:
        return target_piece == EMPTY_CELL

    if abs(delta_col) == 1 and delta_row == forward:
        if target_piece == EMPTY_CELL:
            return False
        return target_piece[0] != color

    return False
