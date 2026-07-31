import unittest

from server.room import Room

# row0: bK .   row1: . .   row2: wP .
BOARD = "bK .\n. .\nwP ."


class FakeRepository:
    def __init__(self):
        self.games = []
        self.participants = []
        self.moves = []
        self.ended = []

    def create_game(self, room_id, rows, cols):
        game_id = len(self.games) + 1
        self.games.append((room_id, rows, cols))
        return game_id

    def add_participant(self, game_id, connection_id, color, role):
        self.participants.append((game_id, connection_id, color, role))

    def record_move(
        self, game_id, seq, color, piece_token, source, dest, clock_ms, accepted, reason
    ):
        self.moves.append(
            (game_id, seq, color, piece_token, source, dest, clock_ms, accepted, reason)
        )

    def end_game(self, game_id, winner_color):
        self.ended.append((game_id, winner_color))


def snapshot_positions(room):
    return {
        (piece.logical_row, piece.logical_col): piece.token()
        for piece in room.snapshot().pieces
    }


class TestRoomRoleAssignment(unittest.TestCase):
    def test_first_second_third_join_get_w_b_viewer(self):
        room = Room("r1", BOARD)

        self.assertEqual(room.join("c1"), "w")
        self.assertEqual(room.join("c2"), "b")
        self.assertEqual(room.join("c3"), "viewer")
        self.assertTrue(room.is_active())

    def test_role_of_reports_assigned_role(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")
        room.join("c3")

        self.assertEqual(room.role_of("c1"), "w")
        self.assertEqual(room.role_of("c2"), "b")
        self.assertEqual(room.role_of("c3"), "viewer")
        self.assertIsNone(room.role_of("ghost"))

    def test_connections_returns_all_seats_and_viewers(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")
        room.join("c3")

        self.assertEqual(room.connections(), {"c1", "c2", "c3"})


class TestRoomPause(unittest.TestCase):
    def test_leave_seated_player_pauses_room(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")
        self.assertTrue(room.is_active())

        room.leave("c1")
        self.assertFalse(room.is_active())

        clock_before = room.snapshot().clock
        room.tick(1000)
        self.assertEqual(room.snapshot().clock, clock_before)

    def test_leave_viewer_does_not_affect_activity(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")
        room.join("c3")

        room.leave("c3")
        self.assertTrue(room.is_active())
        self.assertIsNone(room.role_of("c3"))


class TestRoomMoveAuthorization(unittest.TestCase):
    def test_viewer_move_rejected_without_touching_engine(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")
        room.join("c3")

        result = room.request_move("c3", (2, 0), (1, 0))

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "not_your_piece")
        self.assertEqual(snapshot_positions(room)[(2, 0)], "wP")

    def test_wrong_color_move_rejected(self):
        room = Room("r1", BOARD)
        room.join("c1")  # w
        room.join("c2")  # b

        result = room.request_move("c2", (2, 0), (1, 0))

        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "not_your_piece")
        self.assertEqual(snapshot_positions(room)[(2, 0)], "wP")

    def test_move_from_empty_cell_rejected(self):
        room = Room("r1", BOARD)
        room.join("c1")
        room.join("c2")

        result = room.request_move("c1", (1, 0), (0, 0))
        self.assertFalse(result.is_accepted)
        self.assertEqual(result.reason, "not_your_piece")


class TestRoomMoveDelegationAndPersistence(unittest.TestCase):
    def test_accepted_move_delegates_to_engine_and_records(self):
        repository = FakeRepository()
        room = Room("r1", BOARD, repository=repository)
        room.attach_game(repository.create_game("r1", room.rows, room.cols))
        room.join("c1")
        room.join("c2")

        result = room.request_move("c1", (2, 0), (1, 0))
        self.assertTrue(result.is_accepted)

        room.tick(1000)
        self.assertEqual(snapshot_positions(room)[(1, 0)], "wP")

        self.assertEqual(len(repository.moves), 1)
        recorded = repository.moves[0]
        self.assertEqual(recorded[2], "w")
        self.assertEqual(recorded[3], "wP")
        self.assertEqual(recorded[4], (2, 0))
        self.assertEqual(recorded[5], (1, 0))
        self.assertTrue(recorded[7])

    def test_join_records_participant_when_repository_attached(self):
        repository = FakeRepository()
        room = Room("r1", BOARD, repository=repository)
        room.attach_game(repository.create_game("r1", room.rows, room.cols))

        room.join("c1")

        self.assertEqual(repository.participants, [(1, "c1", "w", "w")])

    def test_join_does_not_touch_repository_without_game_id(self):
        repository = FakeRepository()
        room = Room("r1", BOARD, repository=repository)

        room.join("c1")

        self.assertEqual(repository.participants, [])


if __name__ == "__main__":
    unittest.main()
