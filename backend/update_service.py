# -*- coding: utf-8 -*-
"""backend/update_service.py — Check for app updates (Variant A: browser download)."""

from typing import Optional

import httpx

from backend.config import APP_VERSION, UPDATE_VERSION_URL, UPDATE_APK_URL

_TIMEOUT = 8  # seconds


def _parse_version(v: str) -> tuple:
    """Parse '1.2.3' into (1, 2, 3) for comparison."""
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except (ValueError, AttributeError):
        return (0,)


def check_for_update() -> Optional[str]:
    """Check remote version.json. Return new version string if update available, else None.

    Expected remote format: {"version": "1.1.0"}
    """
    if not UPDATE_VERSION_URL:
        return None
    try:
        resp = httpx.get(UPDATE_VERSION_URL, timeout=_TIMEOUT, follow_redirects=True)
        resp.raise_for_status()
        data = resp.json()
        remote_version = data.get("version", "")
        if _parse_version(remote_version) > _parse_version(APP_VERSION):
            return remote_version
    except Exception:
        pass
    return None


def get_apk_url() -> str:
    """Return the APK download URL from config."""
    return UPDATE_APK_URL
