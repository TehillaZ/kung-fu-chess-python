from __future__ import annotations

import pathlib

import cv2
import numpy as np


def make_white_transparent(img_obj, threshold=240):
    """Turn near-white pixels transparent — temporary fix for opaque sprite backgrounds."""
    if img_obj.img is None:
        return img_obj

    img = img_obj.img
    if len(img.shape) == 2 or img.shape[2] == 4:
        return img_obj

    # BGR (3 channels) → BGRA (4 channels with alpha)
    bgra = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    white_mask = (
        (bgra[:, :, 0] > threshold)
        & (bgra[:, :, 1] > threshold)
        & (bgra[:, :, 2] > threshold)
    )
    bgra[white_mask, 3] = 0

    img_obj.img = bgra
    return img_obj


def remove_blue_overlay(img_obj, blue_min=200, other_max=40):
    """Paint over baked-in pure-blue debug text with surrounding piece colors.

    Making the text transparent leaves letter-shaped holes (board shows through).
    Inpainting fills those pixels so the text is actually gone.
    """
    if img_obj.img is None:
        return img_obj

    img = img_obj.img
    if len(img.shape) < 3:
        return img_obj

    has_alpha = img.shape[2] == 4
    bgr = img[:, :, :3].copy() if has_alpha else img.copy()
    alpha = img[:, :, 3].copy() if has_alpha else None

    blue_mask = (
        (bgr[:, :, 0] >= blue_min)
        & (bgr[:, :, 1] <= other_max)
        & (bgr[:, :, 2] <= other_max)
    )
    if not blue_mask.any():
        return img_obj

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(blue_mask.astype(np.uint8) * 255, kernel, iterations=2)
    bgr = cv2.inpaint(bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)

    img_obj.img = np.dstack([bgr, alpha]) if has_alpha else bgr
    return img_obj


class Img:
    def __init__(self):
        self.img = None

    def read(self, path: str | pathlib.Path,
             size: tuple[int, int] | None = None,
             keep_aspect: bool = False,
             interpolation: int = cv2.INTER_AREA) -> "Img":
        """
        Load `path` into self.img and **optionally resize**.

        Parameters
        ----------
        path : str | Path
            Image file to load.
        size : (width, height) | None
            Target size in pixels.  If None, keep original.
        keep_aspect : bool
            • False  → resize exactly to `size`
            • True   → shrink so the *longer* side fits `size` while
                       preserving aspect ratio (no cropping).
        interpolation : OpenCV flag
            E.g.  `cv2.INTER_AREA` for shrink, `cv2.INTER_LINEAR` for enlarge.

        Returns
        -------
        Img
            `self`, so you can chain:  `sprite = Img().read("foo.png", (64,64))`
        """
        path = str(path)
        self.img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if self.img is None:
            raise FileNotFoundError(f"Cannot load image: {path}")

        if size is not None:
            self.resize(size, keep_aspect=keep_aspect, interpolation=interpolation)

        return self

    def resize(
        self,
        size: tuple[int, int],
        keep_aspect: bool = False,
        interpolation: int = cv2.INTER_AREA,
    ) -> "Img":
        if self.img is None:
            raise ValueError("Image not loaded.")

        target_w, target_h = size
        h, w = self.img.shape[:2]

        if keep_aspect:
            scale = min(target_w / w, target_h / h)
            new_w, new_h = int(w * scale), int(h * scale)
        else:
            new_w, new_h = target_w, target_h

        if self.img.shape[2] == 4:
            # Resize color/alpha separately; keep transparent pixels colorless.
            bgr = self.img[:, :, :3].copy()
            alpha = self.img[:, :, 3]
            bgr[alpha == 0] = 0
            bgr = cv2.resize(bgr, (new_w, new_h), interpolation=interpolation)
            alpha = cv2.resize(alpha, (new_w, new_h), interpolation=interpolation)
            self.img = np.dstack([bgr, alpha])
        else:
            self.img = cv2.resize(self.img, (new_w, new_h), interpolation=interpolation)
        return self

    def draw_on(self, other_img, x, y):
        if self.img is None or other_img.img is None:
            raise ValueError("Both images must be loaded before drawing.")

        h, w = self.img.shape[:2]
        H, W = other_img.img.shape[:2]

        if x < 0 or y < 0 or y + h > H or x + w > W:
            raise ValueError("Logo does not fit at the specified position.")

        roi = other_img.img[y:y + h, x:x + w]
        src = self.img

        if src.shape[2] == 4:
            # Alpha-blend onto BGR or BGRA canvas without stripping transparency.
            alpha = src[:, :, 3:4].astype(np.float32) / 255.0
            src_bgr = src[:, :, :3].astype(np.float32)
            dst_bgr = roi[:, :, :3].astype(np.float32)
            blended = (1.0 - alpha) * dst_bgr + alpha * src_bgr
            roi[:, :, :3] = blended.astype(np.uint8)
        elif roi.shape[2] == 4 and src.shape[2] == 3:
            roi[:, :, :3] = src
            roi[:, :, 3] = 255
        else:
            other_img.img[y:y + h, x:x + w] = src

    def put_text(self, txt, x, y, font_size, color=(255, 255, 255, 255), thickness=1):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.putText(self.img, txt, (x, y),
                    cv2.FONT_HERSHEY_SIMPLEX, font_size,
                    color, thickness, cv2.LINE_AA)

    def show(self, window_name="Image"):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow(window_name, self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def display_frame(self, window_name="Image"):
        if self.img is None:
            raise ValueError("Image not loaded.")
        cv2.imshow(window_name, self.img)
