class ArrivalEvents:
    """Events produced when simulated time advances."""

    def __init__(self, king_captured=False):
        self.king_captured = king_captured

    def __eq__(self, other):
        if not isinstance(other, ArrivalEvents):
            return NotImplemented
        return self.king_captured == other.king_captured

    def __repr__(self):
        return f"ArrivalEvents(king_captured={self.king_captured!r})"
