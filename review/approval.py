"""Manages draft status transitions. Only drafts with status='approved' can be published."""

from __future__ import annotations


def approve_draft(draft_id: int) -> None:
    raise NotImplementedError


def skip_draft(draft_id: int) -> None:
    raise NotImplementedError


def get_pending_drafts() -> list[dict]:
    raise NotImplementedError


def get_approved_drafts() -> list[dict]:
    raise NotImplementedError
