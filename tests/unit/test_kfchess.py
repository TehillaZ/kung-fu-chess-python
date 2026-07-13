import io
import unittest
from contextlib import redirect_stdout

from kungfu_chess.engine.game_engine import ChessGameSimulator
from kungfu_chess.io.board_parser import validate_board_input as validatefunc
from kungfu_chess.texttests.script_runner import ScriptRunner


def parse_input(raw_input):
    return ScriptRunner().run(raw_input)

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

    def test_pawn_can_move_two_cells_from_start_row(self):
        sim = ChessGameSimulator(". .\n. .\n. .\nwP .")
        sim.execute_click(0, 300)
        sim.execute_click(0, 100)
        sim.execute_wait(2000)
        self.assertEqual(sim.board, [[".", "."], ["wP", "."], [".", "."], [".", "."]])

    def test_pawn_two_cell_move_blocked_if_path_not_clear(self):
        sim = ChessGameSimulator(". .\n. .\nwR .\nwP .")
        sim.execute_click(0, 300)
        sim.execute_click(0, 100)
        sim.execute_wait(2000)
        self.assertEqual(sim.board, [[".", "."], [".", "."], ["wR", "."], ["wP", "."]])

    def test_white_pawn_promotes_to_queen_on_last_row(self):
        sim = ChessGameSimulator(". .\nwP .")
        sim.execute_click(0, 100)
        sim.execute_click(0, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [["wQ", "."], [".", "."]])

    def test_black_pawn_promotes_to_queen_on_last_row(self):
        sim = ChessGameSimulator("bP .\n. .")
        sim.execute_click(0, 0)
        sim.execute_click(0, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "."], ["bQ", "."]])

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


class TestMovingPieceRedirect(unittest.TestCase):
    def test_cannot_redirect_piece_while_moving(self):
        sim = ChessGameSimulator("wR . .")
        sim.execute_click(50, 50)
        sim.execute_click(250, 50)   # schedule 2-cell move
        sim.execute_click(50, 50)    # select again while moving
        sim.execute_click(150, 50)   # try to redirect to 1 cell
        sim.execute_wait(2000)
        self.assertEqual(sim.board, [[".", ".", "wR"]])

    def test_can_move_immediately_after_arrival(self):
        sim = ChessGameSimulator("wR . .")
        sim.execute_click(50, 50)
        sim.execute_click(150, 50)   # 1-cell move, arrives in 1000ms
        sim.execute_wait(1000)
        sim.execute_click(150, 50)
        sim.execute_click(250, 50)   # move again immediately, no cooldown
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", ".", "wR"]])

    def test_opposite_colors_do_not_move_concurrently_on_common_route(self):
        input_data = """Board:
wR . .
. . .
bR . .
Commands:
click 50 50
click 250 50
click 50 250
click 250 250
wait 2000
print board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(
            buffer.getvalue().strip(),
            ". . wR\n. . .\nbR . .",
        )


class TestAdvancedRealtimeInteraction(unittest.TestCase):
    def test_enemy_collision_capture_on_arrival(self):
        sim = ChessGameSimulator("wR bR")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR"]])

    def test_invalid_premove_cancelled_when_path_blocked(self):
        sim = ChessGameSimulator("wR . .\n. wR .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 0)
        sim.execute_click(100, 100)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [["wR", "wR", "."], [".", ".", "."]])

    def test_friendly_piece_landing_cancels_premove(self):
        sim = ChessGameSimulator("wR . wR")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_click(200, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR", "wR"]])

    def test_destination_conflict_first_arrival_wins(self):
        sim = ChessGameSimulator("wR . wR")
        sim.execute_click(200, 0)
        sim.execute_click(100, 0)
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [["wR", "wR", "."]])

    def test_opposite_color_destination_collision(self):
        sim = ChessGameSimulator("wR . bR")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_click(200, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR", "bR"]])
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR", "bR"]])


class TestKnightJump(unittest.TestCase):
    def test_knight_jump_lasts_1000ms(self):
        sim = ChessGameSimulator("wN . .\n. . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        sim.execute_wait(500)
        self.assertEqual(sim.board, [["wN", ".", "."], [".", ".", "."], [".", ".", "."]])
        sim.execute_wait(500)
        self.assertEqual(sim.board, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_knight_stays_at_origin_during_jump(self):
        sim = ChessGameSimulator("wN . .\n. . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        self.assertEqual(sim.board, [["wN", ".", "."], [".", ".", "."], [".", ".", "."]])

    def test_knight_lands_normally_when_no_enemy_arrives(self):
        sim = ChessGameSimulator("wN . .\n. . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_airborne_knight_captures_arriving_enemy(self):
        sim = ChessGameSimulator("wN . .\nbR . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        sim.execute_click(0, 100)
        sim.execute_click(0, 0)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [["wN", ".", "."], [".", ".", "."], [".", ".", "."]])

    def test_moving_knight_cannot_jump(self):
        sim = ChessGameSimulator("wN . .\n. . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        sim.execute_click(0, 0)
        sim.execute_click(100, 200)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", ".", "."], [".", ".", "wN"], [".", ".", "."]])

    def test_captured_piece_cannot_jump(self):
        sim = ChessGameSimulator("wN . .\n. . .\n. . .")
        sim.execute_click(0, 0)
        sim.execute_click(200, 100)
        sim._board.set_piece(0, 0, ".")
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", ".", "."], [".", ".", "."], [".", ".", "."]])


class TestGameOver(unittest.TestCase):
    def test_capturing_enemy_king_ends_game(self):
        sim = ChessGameSimulator("wR bK")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertTrue(sim.game_over)
        self.assertEqual(sim.board, [[".", "wR"]])

    def test_moves_ignored_after_game_over(self):
        sim = ChessGameSimulator("wR bK\nwN .")
        sim.execute_click(0, 0)
        sim.execute_click(100, 0)
        sim.execute_wait(1000)
        self.assertTrue(sim.game_over)
        sim.execute_click(0, 100)
        sim.execute_click(100, 100)
        sim.execute_wait(1000)
        self.assertEqual(sim.board, [[".", "wR"], ["wN", "."]])

    def test_capture_king_ends_game_in_full_input(self):
        input_data = """Board:
wR bK
. .
Commands:
click 0 0
click 100 0
wait 1000
click 0 100
click 100 100
wait 1000
print board"""
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            parse_input(input_data)
        self.assertEqual(buffer.getvalue().strip(), ". wR\n. .")


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

