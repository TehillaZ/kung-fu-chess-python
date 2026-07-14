from kungfu_chess.io.board_printer import BoardPrinter


class Renderer:
    """Formats a read-only GameSnapshot as text (no GUI toolkit)."""

    def __init__(self, printer=None):
        self._printer = printer or BoardPrinter()
        self._last_output = None

    def render(self, snapshot):
        rows = [["." for _ in range(snapshot.cols)] for _ in range(snapshot.rows)]

        for piece in snapshot.pieces:
            rows[piece.logical_row][piece.logical_col] = piece.token()

        lines = [" ".join(row) for row in rows]
        if snapshot.game_over:
            lines.append("GAME OVER")

        self._last_output = "\n".join(lines)
        return self._last_output

    def print(self, snapshot):
        print(self.render(snapshot))
