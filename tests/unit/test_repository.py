import unittest

from kungfu_chess.persistence.db import connect
from kungfu_chess.persistence.repository import GameRepository


class TestGameRepository(unittest.TestCase):
    def setUp(self):
        self.connection = connect(":memory:")
        self.repository = GameRepository(self.connection)

    def test_create_game_inserts_active_row(self):
        game_id = self.repository.create_game("room1", 8, 8)

        row = self.connection.execute(
            "select room_id, rows, cols, status from games where id = ?",
            (game_id,),
        ).fetchone()
        self.assertEqual(row, ("room1", 8, 8, "active"))

    def test_add_participant_inserts_row(self):
        game_id = self.repository.create_game("room1", 8, 8)
        self.repository.add_participant(game_id, "conn1", "w", "w")

        row = self.connection.execute(
            "select connection_id, color, role from game_players where game_id = ?",
            (game_id,),
        ).fetchone()
        self.assertEqual(row, ("conn1", "w", "w"))

    def test_record_move_inserts_row(self):
        game_id = self.repository.create_game("room1", 8, 8)
        self.repository.record_move(
            game_id, 1, "w", "wP", (6, 0), (5, 0), 1000, True, "ok"
        )

        row = self.connection.execute(
            "select seq, color, piece_token, from_row, from_col, to_row, "
            "to_col, accepted, reason from moves where game_id = ?",
            (game_id,),
        ).fetchone()
        self.assertEqual(row, (1, "w", "wP", 6, 0, 5, 0, 1, "ok"))

    def test_end_game_sets_status_and_winner(self):
        game_id = self.repository.create_game("room1", 8, 8)
        self.repository.end_game(game_id, "w")

        row = self.connection.execute(
            "select status, winner_color from games where id = ?",
            (game_id,),
        ).fetchone()
        self.assertEqual(row, ("finished", "w"))


if __name__ == "__main__":
    unittest.main()
