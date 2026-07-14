class MoveResult:
    """Application-level result for a move request."""

    def __init__(self, is_accepted, reason):
        self.is_accepted = is_accepted
        self.reason = reason

    def __eq__(self, other):
        if not isinstance(other, MoveResult):
            return NotImplemented
        return (self.is_accepted, self.reason) == (other.is_accepted, other.reason)

    def __repr__(self):
        return (
            f"MoveResult(is_accepted={self.is_accepted!r}, "
            f"reason={self.reason!r})"
        )
