import os
import tempfile
import unittest

from kungfu_chess.io.board_csv import load_board_csv


class TestBoardCsv(unittest.TestCase):
    def test_missing_file_returns_empty_string(self):
        self.assertEqual(load_board_csv("does/not/exist.csv"), "")

    def test_loads_and_converts_commas_to_spaces(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False
        ) as handle:
            handle.write("wR,wN\nbP,bP\n")
            path = handle.name

        try:
            result = load_board_csv(path)
            self.assertEqual(result, "wR wN\nbP bP")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
