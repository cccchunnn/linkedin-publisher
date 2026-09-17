"""LinkedIn OAuth 2.0 three-legged flow. Stores and refreshes tokens."""

from __future__ import annotations


def authorize() -> dict:
    raise NotImplementedError


def refresh_token(token_data: dict) -> dict:
    raise NotImplementedError


def load_token() -> dict | None:
    raise NotImplementedError


if __name__ == "__main__":
    authorize()
