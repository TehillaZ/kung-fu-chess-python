from kungfu_chess.model.piece import PIECE_STATE_IDLE, PIECE_STATE_MOVING


class PieceSnapshot:
    """Read-only piece view for rendering."""

    def __init__(
        self,
        piece_id,
        color,
        kind,
        pixel_x,
        pixel_y,
        logical_row,
        logical_col,
        state,
    ):
        self.piece_id = piece_id
        self.color = color
        self.kind = kind
        self.pixel_x = pixel_x
        self.pixel_y = pixel_y
        self.logical_row = logical_row
        self.logical_col = logical_col
        self.state = state

    def token(self):
        return f"{self.color}{self.kind}"

    def __eq__(self, other):
        if not isinstance(other, PieceSnapshot):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return (
            f"PieceSnapshot(id={self.piece_id!r}, token={self.token()!r}, "
            f"pixel=({self.pixel_x}, {self.pixel_y}), "
            f"cell=({self.logical_row}, {self.logical_col}), "
            f"state={self.state!r})"
        )


class GameSnapshot:
    """Read-only view of game state for rendering."""

    def __init__(
        self,
        rows,
        cols,
        cell_size,
        clock,
        game_over,
        selected_row,
        selected_col,
        pieces,
    ):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.clock = clock
        self.game_over = game_over
        self.selected_row = selected_row
        self.selected_col = selected_col
        self.pieces = tuple(pieces)

    def __eq__(self, other):
        if not isinstance(other, GameSnapshot):
            return NotImplemented
        return (
            self.rows,
            self.cols,
            self.cell_size,
            self.clock,
            self.game_over,
            self.selected_row,
            self.selected_col,
            self.pieces,
        ) == (
            other.rows,
            other.cols,
            other.cell_size,
            other.clock,
            other.game_over,
            other.selected_row,
            other.selected_col,
            other.pieces,
        )

    def __repr__(self):
        return (
            f"GameSnapshot({self.rows}x{self.cols}, clock={self.clock}, "
            f"game_over={self.game_over}, pieces={len(self.pieces)})"
        )


def cell_center_pixel(row, col, cell_size):
    return (
        col * cell_size + cell_size // 2,
        row * cell_size + cell_size // 2,
    )


def interpolate_motion_pixel(motion, clock, cell_size):
    start_row, start_col = motion.start
    end_row, end_col = motion.end
    elapsed = max(0, clock - motion.departure_time)
    duration = max(1, motion.arrival_time - motion.departure_time)
    progress = min(1.0, elapsed / duration)

    start_x, start_y = cell_center_pixel(start_row, start_col, cell_size)
    end_x, end_y = cell_center_pixel(end_row, end_col, cell_size)

    pixel_x = int(start_x + (end_x - start_x) * progress)
    pixel_y = int(start_y + (end_y - start_y) * progress)
    return pixel_x, pixel_y


def build_snapshot(board, game_state, controller, arbiter):
    cell_size = board.cell_size
    active_motion = None

    if arbiter.has_active_motion():
        active_motion = arbiter.pending_motions[0]

    pieces = []
    for piece in board.all_pieces():
        row, col = piece.cell.as_tuple()
        state = piece.state
        pixel_x, pixel_y = cell_center_pixel(row, col, cell_size)

        if (
            active_motion is not None
            and active_motion.start == (row, col)
            and active_motion.piece == piece.to_token()
        ):
            state = PIECE_STATE_MOVING
            pixel_x, pixel_y = interpolate_motion_pixel(
                active_motion,
                game_state.clock,
                cell_size,
            )

        pieces.append(
            PieceSnapshot(
                piece.id,
                piece.color,
                piece.kind,
                pixel_x,
                pixel_y,
                row,
                col,
                state,
            )
        )

    selected_row = None
    selected_col = None
    if controller.selected_pos is not None:
        selected_row, selected_col = controller.selected_pos

    return GameSnapshot(
        board.rows(),
        board.cols(),
        cell_size,
        game_state.clock,
        game_state.game_over,
        selected_row,
        selected_col,
        pieces,
    )
