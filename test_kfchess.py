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
        sim.execute_wait(1000)
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


class TestPawnMovement(unittest.TestCase):
    def test_white_pawn_moves_upward(self):
        sim = ChessGameSimulator(". .\n. .\nwP .")
        sim.execute_click(0, 200)
        sim.execute_click(0, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "."], ["wP", "."], [".", "."]])

    def test_black_pawn_moves_downward(self):
        sim = ChessGameSimulator("bP .\n. .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(0, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "."], ["bP", "."], [".", "."]])

    def test_pawn_captures_diagonally(self):
        sim = ChessGameSimulator(". .\n. bR\nwP .")
        sim.execute_click(0, 200)
        sim.execute_click(100, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "."], [".", "wP"], [".", "."]])

    def test_pawn_cannot_move_two_cells(self):
        sim = ChessGameSimulator(". .\n. .\nwP .\n. .")
        sim.execute_click(0, 200)
        sim.execute_click(0, 0)
        self.assertEqual(sim.board, [[".", "."], [".", "."], ["wP", "."], [".", "."]])

    def test_pawn_cannot_capture_forward(self):
        sim = ChessGameSimulator("bR .\nwP .\n. .")
        sim.execute_click(0, 100)
        sim.execute_click(0, 0)
        self.assertEqual(sim.board, [["bR", "."], ["wP", "."], [".", "."]])


class TestTimedMovement(unittest.TestCase):
    def test_piece_stays_at_origin_before_arrival(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        self.assertEqual(sim.board, [["wR", "."], [".", "."]])

    def test_piece_moves_after_enough_wait(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR"], [".", "."]])

    def test_piece_stays_during_partial_wait(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(500)
        self.assertEqual(sim.board, [["wR", "."], [".", "."]])

    def test_print_board_before_arrival_shows_original_position(self):
        sim = ChessGameSimulator("wR .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            sim.print_board()
        self.assertEqual(buffer.getvalue().strip(), "wR .\n. .")

    def test_one_cell_move_before_arrival_board_unchanged(self):
        input_data = """Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nwait 500\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), "wR . .")

    def test_two_cell_move_before_and_after_arrival(self):
        input_data = """Board:\nwR . .\nCommands:\nclick 50 50\nclick 250 50\nwait 1000\nprint board\nwait 1000\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), "wR . .\n. . wR")


class TestMainProcess(unittest.TestCase):
    def test_process_vpl_input_print_board(self):
        input_data = """Board:\nwR .\n. .\nCommands:\nclick 0 0\nclick 100 0\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), "wR .\n. .")

    def test_process_vpl_input_validation_error(self):
        input_data = """Board:\nwR XY\n. .\nCommands:\nprint board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), "ERROR UNKNOWN_TOKEN")


if __name__ == "__main__":
    unittest.main()

