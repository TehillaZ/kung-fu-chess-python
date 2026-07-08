import io
import unittest
from contextlib import redirect_stdout

from validator import validatefunc
from simulator import ChessGameSimulator
from p_input import parse_input


class TestValidate(unittest.TestCase):
    def test_validate_accepts_valid_board(self):
        input_data = """Board:\nwR .\n. .\nCommands:\nprint board"""
        self.assertIsNone(validatefunc(input_data))

    def test_validate_rejects_empty_board(self):
        input_data = """Board:\nCommands:\nprint board"""
        self.assertEqual(validatefunc(input_data), "ERROR EMPTY_BOARD")

    def test_validate_rejects_row_width_mismatch(self):
        input_data = """Board:\nwR .\nwR . .\nCommands:\nprint board"""
        self.assertEqual(validatefunc(input_data), "ERROR ROW_WIDTH_MISMATCH")

    def test_validate_rejects_unknown_token(self):
        input_data = """Board:\nwR XY\n. .\nCommands:\nprint board"""
        self.assertEqual(validatefunc(input_data), "ERROR UNKNOWN_TOKEN")


class TestChessGameSimulator(unittest.TestCase):
    def test_move_piece_on_empty_target(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)    # select rook
        sim.execute_click(100, 0)  # move rook right one cell
        self.assertEqual(sim.board, [[".", "wR"], [".", "."]])

    def test_illegal_rook_move(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 100)  # diagonal move is illegal for a rook
        self.assertEqual(sim.board, [["wR", "."], [".", "."]])

    def test_wait_increments_clock(self):
        sim = ChessGameSimulator("wK .\n. .")
        sim.execute_wait(250)
        self.assertEqual(sim.clock, 250)


class TestMainProcess(unittest.TestCase):
    def test_process_vpl_input_print_board(self):
        input_data = """Board:\nwR .\n. .\nCommands:\nclick 0 0\nclick 100 0\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), ". wR\n. .")

    def test_process_vpl_input_validation_error(self):
        input_data = """Board:\nwR XY\n. .\nCommands:\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), "ERROR UNKNOWN_TOKEN")


if __name__ == "__main__":
    unittest.main()
