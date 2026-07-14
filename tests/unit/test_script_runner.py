import unittest

from tests.integration.text_script import run_text_script


class TestScriptRunner(unittest.TestCase):
    def test_process_vpl_input_print_board(self):
        input_data = """Board:\nwR .\n. .\nCommands:\nclick 0 0\nclick 100 0\nprint board"""
        self.assertEqual(run_text_script(input_data), "wR .\n. .")

    def test_process_vpl_input_validation_error(self):
        input_data = """Board:\nwR XY\n. .\nCommands:\nprint board"""
        self.assertEqual(run_text_script(input_data), "ERROR UNKNOWN_TOKEN")

    def test_one_cell_move_before_arrival_board_unchanged(self):
        input_data = """Board:\nwR . .\nCommands:\nclick 50 50\nclick 150 50\nwait 500\nprint board"""
        self.assertEqual(run_text_script(input_data), "wR . .")

    def test_two_cell_move_before_and_after_arrival(self):
        input_data = """Board:\nwR . .\nCommands:\nclick 50 50\nclick 250 50\nwait 1000\nprint board\nwait 1000\nprint board"""
        self.assertEqual(run_text_script(input_data), "wR . .\n. . wR")

    def test_opposite_colors_only_first_motion_runs(self):
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
        self.assertEqual(
            run_text_script(input_data),
            ". . wR\n. . .\nbR . .",
        )

    def test_spec_iteration_five_click_click_wait_print(self):
        input_data = """Board:
. wR .
. . .
. . bK
Commands:
click 150 50
click 150 250
wait 1000
print board
wait 1000
print board"""
        self.assertEqual(
            run_text_script(input_data),
            ". wR .\n. . .\n. . bK\n. . .\n. . .\n. wR bK",
        )

    def test_spec_iteration_six_capture_on_arrival(self):
        input_data = """Board:
wR bR
. .
Commands:
click 0 0
click 100 0
wait 1000
print board"""
        self.assertEqual(run_text_script(input_data), ". wR\n. .")

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
        self.assertEqual(run_text_script(input_data), ". wR\n. .")

    def test_clicking_another_piece_replaces_selection(self):
        input_data = """Board:
wR . wK
. . .
Commands:
click 50 50
click 250 50
click 250 150
wait 1000
print board"""
        self.assertEqual(run_text_script(input_data), "wR . .\n. . wK")

    def test_airborne_piece_captures_arriving_enemy(self):
        input_data = """Board:
. . .
wK bR .
. . .
Commands:
jump 50 150
click 150 150
click 50 150
wait 1000
print board"""
        self.assertEqual(run_text_script(input_data), ". . .\nwK . .\n. . .")


if __name__ == "__main__":
    unittest.main()
