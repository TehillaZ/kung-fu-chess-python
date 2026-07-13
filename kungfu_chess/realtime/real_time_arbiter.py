from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.model.game_state import is_king_capture
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.rules.path_utils import (
    column_range,
    path_cells,
    ranges_overlap,
    row_range,
)

MS_PER_CELL = 1000
MS_PER_JUMP = 1000


def is_knight(piece):
    return len(piece) == 2 and piece[1] == "N"


def travel_time(start, end, ms_per_cell=MS_PER_CELL, is_jump=False):
    if is_jump:
        return MS_PER_JUMP

    start_row, start_col = start
    end_row, end_col = end
    distance = max(abs(end_row - start_row), abs(end_col - start_col))
    return distance * ms_per_cell


def find_active_jump_at(cell, event_time, motions):
    for motion in motions:
        if (
            motion.is_jump
            and not motion.landing_cancelled
            and motion.start == cell
            and motion.departure_time <= event_time <= motion.arrival_time
        ):
            return motion

    return None


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


class RealTimeArbiter:
    """Advances simulated time and applies completed motions."""

    def __init__(self, ms_per_cell=MS_PER_CELL):
        self.ms_per_cell = ms_per_cell

    def compute_departure_time(self, clock, piece, start, end, pending_motions, is_jump=False):
        departure_time = clock

        for motion in pending_motions:
            if motion.piece[0] == piece[0]:
                continue

            if not is_jump and not motion.is_jump:
                if has_common_route(start, end, motion.start, motion.end):
                    departure_time = max(departure_time, motion.arrival_time)

            if motion.end == end:
                if motion.is_jump and motion.start == motion.end:
                    continue

                departure_time = max(departure_time, motion.arrival_time)

        return departure_time

    def create_airborne_jump(self, piece, position, clock, pending_motions, order):
        departure_time = self.compute_departure_time(
            clock,
            piece,
            position,
            position,
            pending_motions,
            is_jump=True,
        )

        return Motion(
            piece,
            position,
            position,
            departure_time,
            departure_time + MS_PER_JUMP,
            order,
            is_jump=True,
        )

    def create_motion(self, piece, start, end, clock, pending_motions, order):
        is_jump = is_knight(piece)
        departure_time = self.compute_departure_time(
            clock,
            piece,
            start,
            end,
            pending_motions,
            is_jump,
        )
        move_time = travel_time(start, end, self.ms_per_cell, is_jump)

        return Motion(
            piece,
            start,
            end,
            departure_time,
            departure_time + move_time,
            order,
            is_jump=is_jump,
        )

    def can_apply_motion(self, motion, board, rule_engine):
        piece = board.get_piece(*motion.start)

        if piece == EMPTY_CELL or piece != motion.piece:
            return False

        if motion.is_jump and motion.start == motion.end:
            return True

        return rule_engine.is_legal_move(
            piece,
            motion.start,
            motion.end,
            board,
        )

    def apply_completed_motions(self, board, pending_motions, clock, rule_engine):
        ready_motions = [
            motion for motion in pending_motions
            if motion.arrival_time <= clock
        ]
        still_pending = [
            motion for motion in pending_motions
            if motion.arrival_time > clock
        ]

        ready_motions.sort(
            key=lambda motion: (motion.arrival_time, motion.is_jump, motion.order)
        )
        applied_destinations = set()
        king_captured = False
        tracked_motions = still_pending + ready_motions

        for motion in ready_motions:
            destination = motion.end

            if destination in applied_destinations:
                continue

            if not self.can_apply_motion(motion, board, rule_engine):
                continue

            if motion.is_jump and motion.landing_cancelled:
                continue

            if motion.is_jump and motion.start == motion.end:
                continue

            if not motion.is_jump:
                active_jump = find_active_jump_at(
                    destination,
                    motion.arrival_time,
                    tracked_motions,
                )
                if active_jump and active_jump.piece[0] != motion.piece[0]:
                    start_row, start_col = motion.start
                    board.set_piece(start_row, start_col, EMPTY_CELL)
                    active_jump.landing_cancelled = True
                    still_pending = [
                        pending for pending in still_pending
                        if pending.end != destination
                    ]

                    if is_king_capture(motion.piece):
                        king_captured = True
                        still_pending = []
                        break

                    continue

            captured_piece = board.get_piece(*destination)
            board.move_piece(motion.start, motion.end)
            applied_destinations.add(destination)
            still_pending = [
                pending for pending in still_pending
                if pending.end != destination
            ]

            if is_king_capture(captured_piece):
                king_captured = True
                still_pending = []
                break

        return still_pending, king_captured
