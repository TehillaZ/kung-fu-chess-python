import io
import unittest
from contextlib import redirect_stdout

from kungfu_chess.io.board_parser import BoardParser
from kungfu_chess.io.board_printer import BoardPrinter


class TestBoardPrinter(unittest.TestCase):
    def test_format_board_round_trip(self):
        board = BoardParser.parse("wK . bR\n. . .")
        printer = BoardPrinter()

        self.assertEqual(
            printer.format_board(board),
            "wK . bR\n. . .",
        )

    def test_print_board_writes_logical_occupancy(self):
        board = BoardParser.parse(". wR\n. .")
        buffer = io.StringIO()

        with redirect_stdout(buffer):
            BoardPrinter().print_board(board)

        self.assertEqual(buffer.getvalue().strip(), ". wR\n. .")


if __name__ == "__main__":
    unittest.main()
