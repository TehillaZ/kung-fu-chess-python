import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UI_DIR = PROJECT_ROOT / "UI"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(UI_DIR))

from kungfu_chess.engine.game_engine import GameEngine
from renderer import Renderer


class TestGraphicRenderer(unittest.TestCase):
    def test_render_snapshot_produces_image(self):
        engine = GameEngine("wR .\n. .")
        renderer = Renderer()

        canvas = renderer.render(engine.snapshot())

        self.assertIsNotNone(canvas.img)
        self.assertGreater(canvas.img.shape[0], 100)
        self.assertGreater(canvas.img.shape[1], 100)


if __name__ == "__main__":
    unittest.main()
