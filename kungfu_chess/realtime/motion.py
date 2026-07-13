class Motion:
    """Represents an in-flight piece movement."""

    def __init__(
        self,
        piece,
        start,
        end,
        departure_time,
        arrival_time,
        order,
        is_jump=False,
        landing_cancelled=False,
    ):
        self.piece = piece
        self.start = start
        self.end = end
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.order = order
        self.is_jump = is_jump
        self.landing_cancelled = landing_cancelled

    def as_dict(self):
        return {
            "piece": self.piece,
            "start": self.start,
            "end": self.end,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "order": self.order,
            "is_jump": self.is_jump,
            "landing_cancelled": self.landing_cancelled,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["piece"],
            data["start"],
            data["end"],
            data["departure_time"],
            data["arrival_time"],
            data["order"],
            data.get("is_jump", False),
            data.get("landing_cancelled", False),
        )
