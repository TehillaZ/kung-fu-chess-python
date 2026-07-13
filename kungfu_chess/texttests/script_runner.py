from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.io.board_parser import parse_board_and_commands, validate_board_input
from kungfu_chess.io.board_printer import BoardPrinter


class ScriptRunner:
    """Runs textual command scripts against the game engine."""

    def __init__(self):
        self.printer = BoardPrinter()

    def run(self, raw_input):
        error = validate_board_input(raw_input)
        if error is not None:
            print(error)
            return

        board_string, command_lines = parse_board_and_commands(raw_input)
        engine = GameEngine(board_string)

        for command in command_lines:
            if command.startswith("click"):
                _, x_str, y_str = command.split()
                engine.execute_click(int(x_str), int(y_str))
            elif command.startswith("jump"):
                _, x_str, y_str = command.split()
                engine.execute_jump(int(x_str), int(y_str))
            elif command.startswith("wait"):
                _, ms_str = command.split()
                engine.execute_wait(int(ms_str))
            elif command == "print board":
                self.printer.print_board(engine.board)

        return board_string, command_lines
