from pathlib import Path


def load_board_csv(path):
    """Read a comma-separated board file and return a BoardParser-ready string.

    Returns "" if the file does not exist, matching the empty-board-string
    convention already used by callers (BoardParser raises on empty input).
    """
    path = Path(path)
    if not path.exists():
        return ""

    rows = path.read_text().strip().splitlines()
    return "\n".join(row.replace(",", " ") for row in rows)
