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


def ranges_overlap(first_range, second_range):
    return (
        first_range[0] <= second_range[1]
        and second_range[0] <= first_range[1]
    )


def is_path_clear(start, end, board):
    start_row, start_col = start
    end_row, end_col = end

    row_step = 1 if end_row > start_row else -1 if end_row < start_row else 0
    col_step = 1 if end_col > start_col else -1 if end_col < start_col else 0

    current_row, current_col = start_row + row_step, start_col + col_step

    while (current_row, current_col) != (end_row, end_col):
        if not board.is_empty(current_row, current_col):
            return False
        current_row += row_step
        current_col += col_step

    return True
