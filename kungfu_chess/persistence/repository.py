from datetime import datetime, timezone

STATUS_ACTIVE = "active"
STATUS_FINISHED = "finished"


def _now():
    return datetime.now(timezone.utc).isoformat()


class GameRepository:
    """Records games, participants, and moves to SQLite. No caller writes raw SQL."""

    def __init__(self, connection):
        self._connection = connection

    def create_game(self, room_id, rows, cols):
        cursor = self._connection.execute(
            "INSERT INTO games (room_id, created_at, rows, cols, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (room_id, _now(), rows, cols, STATUS_ACTIVE),
        )
        self._connection.commit()
        return cursor.lastrowid

    def add_participant(self, game_id, connection_id, color, role):
        self._connection.execute(
            "INSERT INTO game_players (game_id, connection_id, color, role, joined_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (game_id, connection_id, color, role, _now()),
        )
        self._connection.commit()

    def record_move(
        self,
        game_id,
        seq,
        color,
        piece_token,
        source,
        dest,
        clock_ms,
        accepted,
        reason,
    ):
        from_row, from_col = source
        to_row, to_col = dest
        self._connection.execute(
            "INSERT INTO moves ("
            "  game_id, seq, color, piece_token,"
            "  from_row, from_col, to_row, to_col,"
            "  clock_ms, accepted, reason"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                game_id,
                seq,
                color,
                piece_token,
                from_row,
                from_col,
                to_row,
                to_col,
                clock_ms,
                int(bool(accepted)),
                reason,
            ),
        )
        self._connection.commit()

    def end_game(self, game_id, winner_color):
        self._connection.execute(
            "UPDATE games SET status = ?, winner_color = ?, ended_at = ? WHERE id = ?",
            (STATUS_FINISHED, winner_color, _now(), game_id),
        )
        self._connection.commit()
