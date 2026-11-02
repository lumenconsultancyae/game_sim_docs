"""Centralized configuration for BDD End-to-End (E2E) browser tests."""

import os

WEB_BASE_URL: str = os.environ.get("E2E_WEB_BASE_URL", "http://127.0.0.1:5173")
API_BASE_URL: str = os.environ.get("E2E_API_BASE_URL", "http://127.0.0.1:8000")

DEFAULT_TIMEOUT: float = float(os.environ.get("E2E_DEFAULT_TIMEOUT", "15.0"))
SIMULATION_TIMEOUT: float = float(os.environ.get("E2E_SIMULATION_TIMEOUT", "30.0"))
POLL_FREQUENCY: float = 0.15

HEADLESS: bool = os.environ.get("E2E_HEADLESS", "true").lower() not in ("0", "false", "no")
WINDOW_WIDTH: int = 1440
WINDOW_HEIGHT: int = 900

CHROMIUM_BINARY: str = os.environ.get("CHROMIUM_BINARY", "/usr/bin/chromium")
CHROMEDRIVER_BINARY: str = os.environ.get("CHROMEDRIVER_BINARY", "/usr/bin/chromedriver")

SCREENSHOT_DIR: str = os.environ.get(
    "E2E_SCREENSHOT_DIR",
    "/root/.gemini/antigravity-cli/brain/369e04c6-3e5f-4f99-a851-36fd57583133",
)
