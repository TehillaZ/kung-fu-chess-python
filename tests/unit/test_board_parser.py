import unittest

from kungfu_chess.io.board_parser import BoardParser, validate_board_input


class TestBoardParser(unittest.TestCase):
    def test_parse_rectangular_board(self):
        board = BoardParser.parse("wK . .\n. bR .")

        self.assertEqual(board.rows(), 2)
        self.assertEqual(board.cols(), 3)
        self.assertEqual(board.get_piece(0, 0), "wK")
        self.assertEqual(board.get_piece(1, 1), "bR")
        self.assertEqual(len(board.all_pieces()), 2)

    def test_parse_assigns_unique_piece_ids(self):
        board = BoardParser.parse("wK bK")

        ids = {piece.id for piece in board.all_pieces()}
        self.assertEqual(ids, {"p1", "p2"})

    def test_validate_accepts_valid_board(self):
        self.assertIsNone(
            validate_board_input("Board:\nwR .\n. .\nCommands:\nprint board")
        )

    def test_validate_rejects_empty_board(self):
        self.assertEqual(
            validate_board_input("Board:\nCommands:\nprint board"),
            "ERROR EMPTY_BOARD",
        )

    def test_validate_rejects_inconsistent_row_length(self):
        self.assertEqual(
            validate_board_input("Board:\nwK .\nwK . .\nCommands:\nprint board"),
            "ERROR ROW_WIDTH_MISMATCH",
        )

    def test_validate_rejects_unknown_token(self):
        self.assertEqual(
            validate_board_input("Board:\nwK XY\n. .\nCommands:\nprint board"),
            "ERROR UNKNOWN_TOKEN",
        )

    def test_parse_rejects_unknown_token(self):
        with self.assertRaises(ValueError) as error:
            BoardParser.parse("wK XY")

        self.assertEqual(str(error.exception), "ERROR UNKNOWN_TOKEN")


if __name__ == "__main__":
    unittest.main()
