from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.model.game_state import is_king_capture
from kungfu_chess.model.piece import KIND_KNIGHT
from kungfu_chess.realtime.arrival_events import ArrivalEvents
from kungfu_chess.realtime.motion import Motion
from kungfu_chess.rules.piece_rules import piece_color

MS_PER_CELL = 1000
MS_PER_JUMP = 1000


def is_knight(piece):
    if hasattr(piece, "kind"):
        return piece.kind == KIND_KNIGHT
    return len(piece) == 2 and piece[1] == KIND_KNIGHT


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
            motion.is_inplace_jump()
            and not motion.landing_cancelled
            and motion.start == cell
            and motion.departure_time <= event_time <= motion.arrival_time
        ):
            return motion

    return None


class RealTimeArbiter:
    """Advances simulated time and applies completed motions."""

    def __init__(self, ms_per_cell=MS_PER_CELL):
        self.ms_per_cell = ms_per_cell
        self._pending_motions = []
        self._move_order = 0

    def has_active_motion(self):
        """True when a blocking (non in-place jump) motion is in progress."""
        return any(
            not motion.is_inplace_jump()
            for motion in self._pending_motions
        )

    @property
    def pending_motions(self):
        return list(self._pending_motions)

    def clear_pending_motions(self):
        self._pending_motions = []

    def _schedule_motion(self, piece, start, end, clock, is_jump=False):
        move_time = travel_time(start, end, self.ms_per_cell, is_jump=is_jump)
        motion = Motion(
            piece,
            start,
            end,
            clock,
            clock + move_time,
            self._move_order,
            is_jump=is_jump,
            is_knight_move=is_jump and start != end and is_knight(piece),
        )
        self._pending_motions.append(motion)
        self._move_order += 1
        return motion

    def start_motion(self, piece, start, end, clock):
        is_jump = is_knight(piece)
        return self._schedule_motion(piece, start, end, clock, is_jump=is_jump)

    def start_jump(self, piece, position, clock):
        return self._schedule_motion(
            piece,
            position,
            position,
            clock,
            is_jump=True,
        )

    def can_apply_motion(self, motion, board, rule_engine):
        piece = board.get_piece(*motion.start)

        if piece == EMPTY_CELL or piece != motion.piece:
            return False

        if motion.is_inplace_jump():
            return True

        return rule_engine.is_legal_move(
            piece,
            motion.start,
            motion.end,
            board,
        )

    def advance_time(self, board, clock, rule_engine):
        return self.apply_completed_motions(board, clock, rule_engine)

    def apply_completed_motions(self, board, clock, rule_engine):
        ready_motions = [
            motion for motion in self._pending_motions
            if motion.arrival_time <= clock
        ]
        still_pending = [
            motion for motion in self._pending_motions
            if motion.arrival_time > clock
        ]

        ready_motions.sort(
            key=lambda motion: (motion.arrival_time, motion.is_inplace_jump(), motion.order)
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

            if motion.is_inplace_jump() and motion.landing_cancelled:
                continue

            if motion.is_inplace_jump():
                continue

            active_jump = find_active_jump_at(
                destination,
                motion.arrival_time,
                tracked_motions,
            )
            if active_jump and piece_color(active_jump.piece) != piece_color(motion.piece):
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

        self._pending_motions = still_pending
        return ArrivalEvents(king_captured=king_captured)
