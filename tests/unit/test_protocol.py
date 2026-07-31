import unittest

from server.protocol import (
    ProtocolError,
    decode_client_message,
    encode_error,
    encode_role,
    encode_snapshot,
)


class FakePiece:
    def __init__(self):
        self.piece_id = "p1"
        self.color = "w"
        self.kind = "P"
        self.pixel_x = 50
        self.pixel_y = 50
        self.logical_row = 0
        self.logical_col = 0
        self.state = "idle"
        self.sprite_state = "idle"
        self.animation_progress = 0.0


class FakeSnapshot:
    def __init__(self):
        self.rows = 2
        self.cols = 2
        self.cell_size = 100
        self.clock = 123
        self.game_over = False
        self.pieces = (FakePiece(),)


class TestDecodeClientMessage(unittest.TestCase):
    def test_decode_valid_move(self):
        message = decode_client_message(
            '{"type": "move", "from": [1, 2], "to": [3, 4]}'
        )
        self.assertEqual(message, {"type": "move", "from": (1, 2), "to": (3, 4)})

    def test_invalid_json_raises(self):
        with self.assertRaises(ProtocolError):
            decode_client_message("not json")

    def test_non_object_raises(self):
        with self.assertRaises(ProtocolError):
            decode_client_message("[1, 2, 3]")

    def test_unknown_type_raises(self):
        with self.assertRaises(ProtocolError):
            decode_client_message('{"type": "ping"}')

    def test_missing_cell_raises(self):
        with self.assertRaises(ProtocolError):
            decode_client_message('{"type": "move", "from": [1, 2]}')

    def test_malformed_cell_raises(self):
        with self.assertRaises(ProtocolError):
            decode_client_message(
                '{"type": "move", "from": [1], "to": [1, 2]}'
            )


class TestEncoders(unittest.TestCase):
    def test_encode_role(self):
        self.assertEqual(encode_role("w"), {"type": "role", "role": "w"})

    def test_encode_error(self):
        self.assertEqual(
            encode_error("bad_thing"), {"type": "error", "reason": "bad_thing"}
        )

    def test_encode_snapshot(self):
        encoded = encode_snapshot(FakeSnapshot())

        self.assertEqual(encoded["type"], "snapshot")
        self.assertEqual(encoded["clock"], 123)
        self.assertEqual(encoded["game_over"], False)
        self.assertEqual(len(encoded["pieces"]), 1)
        self.assertEqual(
            encoded["pieces"][0],
            {
                "id": "p1",
                "color": "w",
                "kind": "P",
                "row": 0,
                "col": 0,
                "pixel_x": 50,
                "pixel_y": 50,
                "state": "idle",
                "sprite_state": "idle",
                "animation_progress": 0.0,
            },
        )


if __name__ == "__main__":
    unittest.main()
