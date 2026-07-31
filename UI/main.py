"""
Graphic Kung Fu Chess entry point.

Run from project root:
  py UI/main.py
"""

import sys
from pathlib import Path

import cv2

UI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = UI_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(UI_DIR))

from kungfu_chess.engine.game_engine import GameEngine
from kungfu_chess.io.board_csv import load_board_csv
from renderer import Renderer

# Standard chess start: black at top (row 0), white at bottom — matches pawn rules.
BOARD_CSV_PATH = PROJECT_ROOT / "board.csv"
WINDOW_NAME = "Kung Fu Chess"
TICK_MS = 50

DEFAULT_BOARD = load_board_csv(BOARD_CSV_PATH)


def on_mouse(event, x, y, flags, state):
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    board_height = state["engine"]._board.rows() * state["engine"]._board.cell_size
    if y >= board_height:
        return
    state["engine"].click(x, y)


def main():
    board_string = DEFAULT_BOARD
    if len(sys.argv) > 1:
        board_string = "\n".join(sys.argv[1:])

    engine = GameEngine(board_string)
    renderer = Renderer()
    state = {"engine": engine}

    cv2.namedWindow(WINDOW_NAME)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse, state)

    print("Click a piece, then click destination. Press Q to quit.")

    while True:
        engine.wait(TICK_MS)

        snapshot = engine.snapshot()
        canvas = renderer.render(snapshot)
        canvas.display_frame(WINDOW_NAME)

        key = cv2.waitKey(TICK_MS) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
