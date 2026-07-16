from pathlib import Path

from img import Img, make_white_transparent, remove_blue_overlay
from kungfu_chess.model.piece import (
    COLOR_BLACK,
    COLOR_WHITE,
    SPRITE_STATE_IDLE,
    SPRITE_STATE_JUMP,
    SPRITE_STATE_MOVE,
    SPRITE_STATE_WAIT,
)

STATE_FALLBACK_ORDER = (
    SPRITE_STATE_IDLE,
    SPRITE_STATE_MOVE,
    SPRITE_STATE_JUMP,
    SPRITE_STATE_WAIT,
)


def token_to_asset_folder(token):
    """Map engine token (wR) to asset folder name (RW)."""
    if token == "." or len(token) != 2:
        return None

    color_suffix = "W" if token[0] == COLOR_WHITE else "B"
    return f"{token[1]}{color_suffix}"


class SpriteManager:
    """Selects the correct sprite frame for a piece's visual state."""

    def __init__(self, assets_dir=None):
        project_root = Path(__file__).resolve().parent.parent
        self.assets_dir = Path(assets_dir) if assets_dir else project_root / "assets"
        self._frame_cache = {}
        self._sprite_cache = {}

    def get_sprite(self, piece, snapshot):
        """Return an Img sized for one board cell."""
        token = piece.token()
        state = piece.sprite_state or SPRITE_STATE_IDLE
        frame_paths = self._resolve_frame_paths(token, state)

        if not frame_paths:
            return None

        frame_index = self._frame_index(piece, len(frame_paths))
        sprite_path = frame_paths[frame_index]
        cache_key = (sprite_path, snapshot.cell_size)
        cached = self._sprite_cache.get(cache_key)
        if cached is not None:
            return cached

        # Paint over debug text first, then key out white background.
        sprite = Img().read(str(sprite_path))
        remove_blue_overlay(sprite)
        make_white_transparent(sprite)
        sprite.resize(
            (snapshot.cell_size, snapshot.cell_size),
            keep_aspect=True,
        )
        self._sprite_cache[cache_key] = sprite
        return sprite

    def _resolve_frame_paths(self, token, state):
        cache_key = (token, state)
        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key]

        folder = token_to_asset_folder(token)
        if folder is None:
            self._frame_cache[cache_key] = []
            return []

        candidates = [state]
        for fallback in STATE_FALLBACK_ORDER:
            if fallback not in candidates:
                candidates.append(fallback)

        for candidate in candidates:
            sprites_dir = (
                self.assets_dir
                / "pieces1"
                / folder
                / "states"
                / candidate
                / "sprites"
            )
            frame_paths = self._list_frame_paths(sprites_dir)
            if frame_paths:
                self._frame_cache[cache_key] = frame_paths
                return frame_paths

        self._frame_cache[cache_key] = []
        return []

    def _list_frame_paths(self, sprites_dir):
        if not sprites_dir.is_dir():
            return []

        frame_paths = []
        for path in sprites_dir.glob("*.png"):
            try:
                frame_paths.append((int(path.stem), path))
            except ValueError:
                continue

        frame_paths.sort(key=lambda item: item[0])
        return [path for _, path in frame_paths]

    def _frame_index(self, piece, frame_count):
        if frame_count <= 1:
            return 0

        if piece.sprite_state == SPRITE_STATE_IDLE:
            return 0

        progress = max(0.0, min(1.0, piece.animation_progress))
        return min(frame_count - 1, int(progress * (frame_count - 1)))
