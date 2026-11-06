"""Centralized configuration for BDD End-to-End (E2E) browser tests."""

import os


def _resolve_url(env_keys: tuple[str, ...], default_url: str) -> str:
    for key in env_keys:
        val = os.environ.get(key)
        if val:
            return val.rstrip("/")
    return default_url.rstrip("/")


def _resolve_binary(env_key: str, candidates: tuple[str, ...]) -> str:
    val = os.environ.get(env_key)
    if val:
        return val
    for path in candidates:
        if os.path.exists(path):
            return path
    return ""


def _resolve_screenshot_dir() -> str:
    env_dir = os.environ.get("E2E_SCREENSHOT_DIR") or os.environ.get("GSP_SCREENSHOT_DIR")
    if env_dir:
        return env_dir
    default_linux = "/root/.gemini/antigravity-cli/brain/369e04c6-3e5f-4f99-a851-36fd57583133"
    if os.path.isdir("/root") and os.access("/root", os.W_OK):
        return default_linux
    return os.path.expanduser("~/.gemini/antigravity/brain/e2e_screenshots")


WEB_URL_CANDIDATES: tuple[str, ...] = (
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://172.22.0.1:5174",
)
API_URL_CANDIDATES: tuple[str, ...] = (
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8002",
    "http://172.22.0.1:8002",
)

WEB_BASE_URL: str = _resolve_url(("E2E_WEB_BASE_URL", "GSP_WEB_URL"), WEB_URL_CANDIDATES[0])
API_BASE_URL: str = _resolve_url(("E2E_API_BASE_URL", "GSP_API_URL"), API_URL_CANDIDATES[0])

DEFAULT_TIMEOUT: float = float(os.environ.get("E2E_DEFAULT_TIMEOUT", "15.0"))
SIMULATION_TIMEOUT: float = float(os.environ.get("E2E_SIMULATION_TIMEOUT", "30.0"))
POLL_FREQUENCY: float = 0.15

_headless_raw = os.environ.get("E2E_HEADLESS", os.environ.get("GSP_HEADLESS", "true"))
HEADLESS: bool = _headless_raw.lower() not in ("0", "false", "no")
WINDOW_WIDTH: int = 1440
WINDOW_HEIGHT: int = 900

CHROMIUM_BINARY: str = _resolve_binary(
    "CHROMIUM_BINARY",
    (
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ),
)
CHROMEDRIVER_BINARY: str = _resolve_binary(
    "CHROMEDRIVER_BINARY",
    (
        "/usr/bin/chromedriver",
        "/opt/homebrew/bin/chromedriver",
        "/usr/local/bin/chromedriver",
    ),
)

SCREENSHOT_DIR: str = _resolve_screenshot_dir()
