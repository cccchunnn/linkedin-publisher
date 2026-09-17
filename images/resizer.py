"""Ensures final image meets LinkedIn specs: 1200x627px, under 5MB, RGB color space."""

from __future__ import annotations

from pathlib import Path


def resize_for_linkedin(image_path: str, target_width: int = 1200, target_height: int = 627) -> str:
    raise NotImplementedError
