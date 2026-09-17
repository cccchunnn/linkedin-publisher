"""Converts fetched content into the unified Article schema regardless of source format."""

from __future__ import annotations

from models import Article


def normalize(raw_data: dict, source_id: str) -> Article:
    raise NotImplementedError
