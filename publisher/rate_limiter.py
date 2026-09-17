"""Enforces LinkedIn API rate limits and configurable posting cadence (max 2 posts/day)."""

from __future__ import annotations


def can_post() -> bool:
    raise NotImplementedError


def record_post() -> None:
    raise NotImplementedError
