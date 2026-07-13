class Piece:
    """Logical chess piece with identity and lifecycle state."""

    def __init__(self, color, piece_type, piece_id, lifecycle="active"):
        self.color = color
        self.piece_type = piece_type
        self.piece_id = piece_id
        self.lifecycle = lifecycle

    @classmethod
    def from_token(cls, token, piece_id):
        return cls(token[0], token[1], piece_id)

    def to_token(self):
        return f"{self.color}{self.piece_type}"

    def is_active(self):
        return self.lifecycle == "active"
