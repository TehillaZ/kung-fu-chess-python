
import cv2
from img import Img

class GraphicRenderer:
    def draw_board(canvas):

        height, width = canvas.img.shape[:2]

        square_width = width // 8
        square_height = height // 8

        initial_position = [
            ["RB", "NB", "BB", "QB", "KB", "BB", "NB", "RB"],  
            ["PB", "PB", "PB", "PB", "PB", "PB", "PB", "PB"],  
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ["PW", "PW", "PW", "PW", "PW", "PW", "PW", "PW"],  
            ["RW", "NW", "BW", "QW", "KW", "BW", "NW", "RW"], 
        ]

        for row in range(8):
            for col in range(8):
                piece = initial_position[row][col]

                if piece:
                    path = f"../assets/pieces2/{piece}/states/idle/sprites/1.png"

                    img = Img().read(
                        path,
                        size=(square_width, square_height),
                        keep_aspect=True
                    )

                    img.draw_on(
                        canvas,
                        col * square_width,
                        row * square_height
                    )


if __name__ == "__main__":

    background = "../assets/board.png"
    canvas = Img().read(background)

    GraphicRenderer.draw_board(canvas)

    canvas.show()