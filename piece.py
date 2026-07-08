class Piece:

    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type

    def set_color(self, color):
        self.color = color

    def set_type(self, type):
        self.type = type
    
    def get_color(self):
        return self.color
    
    def get_type(self):
        return self.type