from board import EMPTY_CELL


def travel_time(start, end, ms_per_cell):
    start_row, start_col = start
    end_row, end_col = end
    distance = max(abs(end_row - start_row), abs(end_col - start_col))
    return distance * ms_per_cell


def column_range(start, end):
    start_row, start_col = start
    end_row, end_col = end

    if start_row == end_row:
        return min(start_col, end_col), max(start_col, end_col)

    return None


def row_range(start, end):
    start_row, start_col = start
    end_row, end_col = end

    if start_col == end_col:
        return min(start_row, end_row), max(start_row, end_row)

    return None


def path_cells(start, end):
    start_row, start_col = start
    end_row, end_col = end
    cells = []

    row_step = 0 if end_row == start_row else (1 if end_row > start_row else -1)
    col_step = 0 if end_col == start_col else (1 if end_col > start_col else -1)

    row, col = start_row, start_col
    while True:
        cells.append((row, col))
        if (row, col) == (end_row, end_col):
            break
        row += row_step
        col += col_step

    return cells


def ranges_overlap(first_range, second_range):
    return (
        first_range[0] <= second_range[1]
        and second_range[0] <= first_range[1]
    )


def has_common_route(start1, end1, start2, end2):
    column_range1 = column_range(start1, end1)
    column_range2 = column_range(start2, end2)
    if column_range1 and column_range2:
        return ranges_overlap(column_range1, column_range2)

    row_range1 = row_range(start1, end1)
    row_range2 = row_range(start2, end2)
    if row_range1 and row_range2:
        return ranges_overlap(row_range1, row_range2)

    return bool(set(path_cells(start1, end1)) & set(path_cells(start2, end2)))


def compute_departure_time(clock, piece, start, end, pending_moves):
    departure_time = clock

    for pending in pending_moves:
        if pending["piece"][0] == piece[0]:
            continue

        if has_common_route(start, end, pending["start"], pending["end"]):
            departure_time = max(departure_time, pending["arrival_time"])

        if pending["end"] == end:
            departure_time = max(departure_time, pending["arrival_time"])

    return departure_time


def can_apply_pending_move(move, board, move_validator):
    piece = board.get_piece(*move["start"])

    if piece == EMPTY_CELL or piece != move["piece"]:
        return False

    return move_validator.is_legal_move(
        piece,
        move["start"],
        move["end"],
        board,
    )


def _remove_destination_conflicts(pending_moves, destination):
    return [
        move for move in pending_moves
        if move["end"] != destination
    ]


def apply_completed_moves(board, pending_moves, clock, move_validator):
    ready_moves = [
        move for move in pending_moves
        if move["arrival_time"] <= clock
    ]
    still_pending = [
        move for move in pending_moves
        if move["arrival_time"] > clock
    ]

    ready_moves.sort(key=lambda move: (move["arrival_time"], move["order"]))
    applied_destinations = set()

    for move in ready_moves:
        destination = move["end"]

        if destination in applied_destinations:
            continue

        if not can_apply_pending_move(move, board, move_validator):
            continue

        board.move_piece(move["start"], move["end"])
        applied_destinations.add(destination)
        still_pending = _remove_destination_conflicts(still_pending, destination)

    return still_pending
