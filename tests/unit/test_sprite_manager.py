import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import cv2
import numpy as np

from kungfu_chess.model.game_snapshot import PieceSnapshot
from kungfu_chess.model.piece import (
    SPRITE_STATE_IDLE,
    SPRITE_STATE_MOVE,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = PROJECT_ROOT / "UI"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(UI_DIR))

from sprite_manager import SpriteManager, token_to_asset_folder


class TestSpriteManager(unittest.TestCase):
    def test_token_to_asset_folder(self):
        self.assertEqual(token_to_asset_folder("wR"), "RW")
        self.assertEqual(token_to_asset_folder("bK"), "KB")
        self.assertIsNone(token_to_asset_folder("."))

    def test_frame_index_uses_animation_progress(self):
        manager = SpriteManager()
        piece = PieceSnapshot(
            1,
            "w",
            "R",
            50,
            50,
            0,
            0,
            "moving",
            SPRITE_STATE_MOVE,
            0.5,
        )

        self.assertEqual(manager._frame_index(piece, 5), 2)

    def test_get_sprite_reads_numbered_frames(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            assets_dir = Path(temp_dir)
            sprites_dir = (
                assets_dir / "pieces1" / "RW" / "states" / "idle" / "sprites"
            )
            sprites_dir.mkdir(parents=True)

            for index in (1, 2, 3):
                frame_path = sprites_dir / f"{index}.png"
                cv2.imwrite(str(frame_path), np.zeros((16, 16, 3), dtype=np.uint8))

            manager = SpriteManager(assets_dir)
            piece = PieceSnapshot(
                1,
                "w",
                "R",
                50,
                50,
                0,
                0,
                "idle",
                SPRITE_STATE_IDLE,
                0.0,
            )
            snapshot = mock.MagicMock(cell_size=100)

            sprite = manager.get_sprite(piece, snapshot)

            self.assertIsNotNone(sprite)
            self.assertIsNotNone(sprite.img)


if __name__ == "__main__":
    unittest.main()
