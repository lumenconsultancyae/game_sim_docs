"""Behave environment hooks for pre-flight health checks, WebDriver lifecycle, console monitoring, and teardown."""

from __future__ import annotations

import os
import sys
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Ensure repository root is importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tests.bdd import config
from tests.bdd.pages.arena_selection_page import ArenaSelectionPage
from tests.bdd.pages.live_simulation_page import LiveSimulationPage
from tests.bdd.pages.tournament_page import TournamentPage


def _verify_service_health() -> None:
    """Confirm API and Web frontend endpoints respond before launching browser scenarios."""
    for name, url in [("API", f"{config.API_BASE_URL}/"), ("Web UI", f"{config.WEB_BASE_URL}/")]:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            raise RuntimeError(f"Pre-flight check failed for {name} ({url}): HTTP {resp.status_code}")


def _collect_severe_console_errors(driver) -> list[str]:
    """Drain browser console logs and return unexpected SEVERE messages."""
    severe_messages = []
    try:
        logs = driver.get_log("browser")
    except Exception:
        return []
    for entry in logs:
        if entry.get("level") == "SEVERE":
            msg = entry.get("message", "")
            # Ignore benign favicon 404s if any
            if "favicon.ico" in msg:
                continue
            severe_messages.append(msg)
    return severe_messages


def before_all(context) -> None:
    """Verify local stack health and launch a shared Chromium WebDriver session."""
    _verify_service_health()

    chrome_options = Options()
    chrome_options.binary_location = config.CHROMIUM_BINARY
    chrome_options.page_load_strategy = "eager"
    if config.HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-networking")
    chrome_options.add_argument("--no-first-run")
    chrome_options.add_argument(f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}")
    chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL"})

    service = Service(executable_path=config.CHROMEDRIVER_BINARY)
    context.driver = webdriver.Chrome(service=service, options=chrome_options)
    context.arena_page = ArenaSelectionPage(context.driver)
    context.live_page = LiveSimulationPage(context.driver)
    context.tournament_page = TournamentPage(context.driver)
    context.driver.get(config.WEB_BASE_URL)


def before_scenario(context, scenario) -> None:
    """Initialize isolated per-scenario tracking and reset browser localStorage."""
    context.modified_games = set()
    context.console_errors = []
    # Drain any stale logs before scenario starts
    _collect_severe_console_errors(context.driver)
    if not context.driver.current_url.startswith(config.WEB_BASE_URL):
        context.driver.get(config.WEB_BASE_URL)
    context.driver.execute_script(
        "window.localStorage.clear(); if (window.location.hash) { window.location.hash = ''; }"
    )


def after_step(context, step) -> None:
    """Fail fast on any unexpected SEVERE browser console error after each step."""
    new_errors = _collect_severe_console_errors(context.driver)
    if new_errors:
        context.console_errors.extend(new_errors)
        raise AssertionError(
            f"Unexpected SEVERE browser console error(s) during step '{step.name}': {new_errors}"
        )


def after_scenario(context, scenario) -> None:
    """Guaranteed idempotent UI and backend tournament state cleanup."""
    try:
        context.arena_page.close_bot_drawer_if_open()
        context.arena_page.close_game_dropdown_if_open()
        context.arena_page.dismiss_reset_confirm_if_open()
    except Exception:
        pass

    try:
        requests.post(f"{config.API_BASE_URL}/stop-tournament", timeout=5)
        for game_id in getattr(context, "modified_games", set()):
            requests.post(
                f"{config.API_BASE_URL}/reset-tournament",
                params={"game_id": game_id},
                timeout=5,
            )
    except Exception:
        pass


def after_all(context) -> None:
    """Close the WebDriver session after all features finish."""
    if hasattr(context, "driver") and context.driver:
        context.driver.quit()
