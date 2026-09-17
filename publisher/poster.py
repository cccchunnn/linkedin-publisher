"""Creates posts via LinkedIn Marketing API. Uploads image then creates post with image attached."""

from __future__ import annotations


def upload_image(image_path: str, access_token: str) -> str:
    raise NotImplementedError


def create_post(post_body: str, image_urn: str, access_token: str) -> str:
    raise NotImplementedError


def publish_approved_drafts() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    publish_approved_drafts()
