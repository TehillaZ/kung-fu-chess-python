from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.engine.move_result import MoveResult
from kungfu_chess.model.board import EMPTY_CELL
from kungfu_chess.rules.piece_rules import piece_color

COLOR_WHITE = "w"
COLOR_BLACK = "b"
ROLE_VIEWER = "viewer"
SEAT_COLORS = (COLOR_WHITE, COLOR_BLACK)

REASON_NOT_YOUR_PIECE = "not_your_piece"


class Room:
    """One game's seats, viewers, and engine. Knows nothing about sockets —
    connections are opaque hashable ids assigned by the transport layer."""

    def __init__(self, room_id, board_string, repository=None, game_id=None):
        self.room_id = room_id
        self._engine = GameEngine(board_string)
        self._repository = repository
        self._game_id = game_id
        self._seats = {color: None for color in SEAT_COLORS}
        self._viewers = set()
        self._move_seq = 0

    @property
    def game_id(self):
        return self._game_id

    @property
    def rows(self):
        return self._engine.board.rows()

    @property
    def cols(self):
        return self._engine.board.cols()

    def attach_game(self, game_id):
        """Bind this room to a persisted games row, created once rows/cols are known."""
        self._game_id = game_id

    def join(self, connection_id):
        role = ROLE_VIEWER
        for color in SEAT_COLORS:
            if self._seats[color] is None:
                self._seats[color] = connection_id
                role = color
                break
        else:
            self._viewers.add(connection_id)

        if self._repository is not None and self._game_id is not None:
            color = role if role in SEAT_COLORS else None
            self._repository.add_participant(
                self._game_id, connection_id, color, role
            )

        return role

    def leave(self, connection_id):
        for color, seated in self._seats.items():
            if seated == connection_id:
                self._seats[color] = None
                return
        self._viewers.discard(connection_id)

    def is_active(self):
        return all(self._seats[color] is not None for color in SEAT_COLORS)

    def role_of(self, connection_id):
        for color, seated in self._seats.items():
            if seated == connection_id:
                return color
        if connection_id in self._viewers:
            return ROLE_VIEWER
        return None

    def connections(self):
        connections = set(self._viewers)
        connections.update(
            seated for seated in self._seats.values() if seated is not None
        )
        return connections

    def request_move(self, connection_id, source, dest):
        role = self.role_of(connection_id)
        if role not in SEAT_COLORS:
            return MoveResult(False, REASON_NOT_YOUR_PIECE)

        piece_token = self._engine.board.get_piece(*source)
        if piece_token == EMPTY_CELL or piece_color(piece_token) != role:
            return MoveResult(False, REASON_NOT_YOUR_PIECE)

        result = self._engine.request_move(source, dest)

        if self._repository is not None and self._game_id is not None:
            self._move_seq += 1
            self._repository.record_move(
                self._game_id,
                self._move_seq,
                role,
                piece_token,
                source,
                dest,
                self._engine.clock,
                result.is_accepted,
                result.reason,
            )

        return result

    def tick(self, milliseconds):
        if not self.is_active():
            return
        self._engine.wait(milliseconds)

    def snapshot(self):
        return self._engine.snapshot()

    @property
    def game_over(self):
        return self._engine.game_over
