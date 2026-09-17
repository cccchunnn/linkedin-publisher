"""Validation pass: checks draft length, hashtag count, source attribution, no hype words."""

from __future__ import annotations

from models import Draft


def validate_draft(draft: Draft, config: dict) -> tuple[bool, list[str]]:
    raise NotImplementedError
