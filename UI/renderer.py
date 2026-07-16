from pathlib import Path

import cv2
import numpy as np

from img import Img
from kungfu_chess.model.game_snapshot import cell_center_pixel
from kungfu_chess.model.piece import COLOR_WHITE, PIECE_STATE_MOVING
from sprite_manager import SpriteManager

HUD_HEIGHT = 48


class Renderer:
    """Draws a GameSnapshot using board and piece sprites."""

    def __init__(self, assets_dir=None, sprite_manager=None):
        project_root = Path(__file__).resolve().parent.parent
        self.assets_dir = Path(assets_dir) if assets_dir else project_root / "assets"
        self.sprite_manager = sprite_manager or SpriteManager(self.assets_dir)
        self._board_image = self._load_board_image()

    def render(self, snapshot):
        board_width = snapshot.cols * snapshot.cell_size
        board_height = snapshot.rows * snapshot.cell_size
        canvas_height = board_height + HUD_HEIGHT

        canvas = Img()
        canvas.img = self._resize_board(board_width, board_height, snapshot.cell_size)
        self._draw_selection(canvas, snapshot)

        for piece in snapshot.pieces:
            pixel_x, pixel_y = self._piece_pixel_position(piece, snapshot.cell_size)
            sprite = self.sprite_manager.get_sprite(piece, snapshot)
            if sprite is not None:
                top_left_x = pixel_x - sprite.img.shape[1] // 2
                top_left_y = pixel_y - sprite.img.shape[0] // 2
                sprite.draw_on(canvas, top_left_x, top_left_y)
            else:
                self._draw_fallback_piece(canvas, piece, pixel_x, pixel_y, snapshot.cell_size)

        self._draw_hud(canvas, snapshot, board_height)
        return canvas

    def _load_board_image(self):
        board_path = self.assets_dir / "board.png"
        if board_path.exists():
            return Img().read(str(board_path)).img
        return None

    def _resize_board(self, width, height, cell_size):
        if self._board_image is not None:
            board = cv2.resize(
                self._board_image,
                (width, height),
                interpolation=cv2.INTER_AREA,
            )
            if board.shape[2] == 4:
                board = cv2.cvtColor(board, cv2.COLOR_BGRA2BGR)
            return board

        image = np.zeros((height, width, 3), dtype=np.uint8)
        light = (210, 180, 140)
        dark = (160, 120, 80)

        for row in range(height // cell_size):
            for col in range(width // cell_size):
                color = light if (row + col) % 2 == 0 else dark
                x0 = col * cell_size
                y0 = row * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size
                image[y0:y1, x0:x1] = color

        return image

    def _piece_pixel_position(self, piece, cell_size):
        if piece.state == PIECE_STATE_MOVING:
            return piece.pixel_x, piece.pixel_y
        return cell_center_pixel(piece.logical_row, piece.logical_col, cell_size)

    def _draw_selection(self, canvas, snapshot):
        if snapshot.selected_row is None or snapshot.selected_col is None:
            return

        cell_size = snapshot.cell_size
        x0 = snapshot.selected_col * cell_size + 4
        y0 = snapshot.selected_row * cell_size + 4
        x1 = x0 + cell_size - 8
        y1 = y0 + cell_size - 8
        cv2.rectangle(canvas.img, (x0, y0), (x1, y1), (0, 220, 255), 3)

    def _draw_fallback_piece(self, canvas, piece, pixel_x, pixel_y, cell_size):
        radius = cell_size // 3
        fill = (240, 240, 240) if piece.color == COLOR_WHITE else (40, 40, 40)
        outline = (255, 120, 0) if piece.state == PIECE_STATE_MOVING else (20, 20, 20)
        cv2.circle(canvas.img, (pixel_x, pixel_y), radius, fill, -1)
        cv2.circle(canvas.img, (pixel_x, pixel_y), radius, outline, 2)

        text_color = (10, 10, 10) if piece.color == COLOR_WHITE else (250, 250, 250)
        cv2.putText(
            canvas.img,
            piece.kind,
            (pixel_x - 8, pixel_y + 8),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            text_color,
            2,
            cv2.LINE_AA,
        )

    def _draw_hud(self, canvas, snapshot, board_height):
        width = snapshot.cols * snapshot.cell_size
        hud = np.full((HUD_HEIGHT, width, 3), (30, 30, 30), dtype=np.uint8)
        canvas.img = np.vstack([canvas.img, hud])

        white_count, black_count = self._piece_counts(snapshot)
        status = "GAME OVER" if snapshot.game_over else "PLAYING"
        hud_text = (
            f"Time: {snapshot.clock}ms   "
            f"Score  W:{white_count}  B:{black_count}   "
            f"{status}"
        )
        cv2.putText(
            canvas.img,
            hud_text,
            (10, board_height + 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (240, 240, 240),
            1,
            cv2.LINE_AA,
        )

    def _piece_counts(self, snapshot):
        white_count = sum(1 for piece in snapshot.pieces if piece.color == COLOR_WHITE)
        black_count = len(snapshot.pieces) - white_count
        return white_count, black_count
