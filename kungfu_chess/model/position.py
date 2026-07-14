class Position:
    """Represents a board row and column."""

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def as_tuple(self):
        return (self.row, self.col)

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.row == other.row and self.col == other.col
        if isinstance(other, tuple) and len(other) == 2:
            return self.row == other[0] and self.col == other[1]
        return False

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"Position(row={self.row}, col={self.col})"


def as_tuple(position):
    if isinstance(position, Position):
        return position.as_tuple()
    return position
