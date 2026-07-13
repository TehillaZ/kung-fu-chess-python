from kungfu_chess.io.board_parser import parse_board_and_commands, validate_board_input


class ScriptParser:
    """Parses textual Kung Fu Chess scripts."""

    def validate(self, raw_input):
        return validate_board_input(raw_input)

    def parse(self, raw_input):
        return parse_board_and_commands(raw_input)
