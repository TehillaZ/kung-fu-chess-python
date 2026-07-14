from kungfu_chess.model.board import EMPTY_CELL, Board
from kungfu_chess.model.piece import all_piece_tokens
from kungfu_chess.model.piece_factory import PieceFactory

VALID_TOKENS = {EMPTY_CELL} | all_piece_tokens()


class BoardParser:
    """Parses textual board descriptions into Board objects."""

    @classmethod
    def parse(cls, board_string, cell_size=100):
        rows = [
            row.split()
            for row in board_string.strip().split("\n")
            if row.strip()
        ]

        if not rows:
            raise ValueError("ERROR EMPTY_BOARD")

        cols = len(rows[0])
        board = Board(rows=len(rows), cols=cols, cell_size=cell_size)
        factory = PieceFactory()

        for row_index, row in enumerate(rows):
            if len(row) != cols:
                raise ValueError("ERROR ROW_WIDTH_MISMATCH")

            for col_index, token in enumerate(row):
                if token not in VALID_TOKENS:
                    raise ValueError("ERROR UNKNOWN_TOKEN")

                if token != EMPTY_CELL:
                    piece = factory.create_from_token(token, row_index, col_index)
                    board.add_piece(piece)

        return board


def validate_board_input(program_input):
    program_input = program_input.splitlines()

    board_lines = []
    inside_board = False

    for line in program_input:
        cleaned_line = line.strip()

        if cleaned_line.startswith("Commands:"):
            inside_board = False
            continue

        if inside_board and cleaned_line:
            board_lines.append(cleaned_line)

        if cleaned_line.startswith("Board:"):
            inside_board = True

    if not board_lines:
        return "ERROR EMPTY_BOARD"

    num_of_cols = len(board_lines[0].split())

    for line in board_lines:
        if len(line.split()) != num_of_cols:
            return "ERROR ROW_WIDTH_MISMATCH"

    for line in board_lines:
        tokens = line.split()
        for token in tokens:
            if token not in VALID_TOKENS:
                return "ERROR UNKNOWN_TOKEN"

    return None


def parse_board_and_commands(raw_input):
    board_lines = []
    command_lines = []
    is_command_block = False

    raw_lines = [
        line.strip()
        for line in raw_input.strip().split("\n")
        if line.strip()
    ]

    for line in raw_lines:
        if line.startswith("Board:"):
            continue
        if line.startswith("Commands:"):
            is_command_block = True
            continue

        if is_command_block:
            command_lines.append(line)
        else:
            board_lines.append(line)

    return "\n".join(board_lines), command_lines
