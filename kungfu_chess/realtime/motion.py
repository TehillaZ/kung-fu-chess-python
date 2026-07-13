class Motion:
    """Represents an in-flight piece movement."""

    def __init__(self, piece, start, end, departure_time, arrival_time, order):
        self.piece = piece
        self.start = start
        self.end = end
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.order = order

    def as_dict(self):
        return {
            "piece": self.piece,
            "start": self.start,
            "end": self.end,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "order": self.order,
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
        )
