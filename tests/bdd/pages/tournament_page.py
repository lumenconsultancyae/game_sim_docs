"""Page Object for the Tournament Dashboard workflow."""

from __future__ import annotations

import re
from typing import Dict, List
from selenium.webdriver.common.by import By

from tests.bdd import config
from tests.bdd.pages.base_page import BasePage


class TournamentPage(BasePage):
    """Encapsulates Tournament tab navigation, bot chip controls, leaderboard, and reset flows."""

    TOURNAMENT_TAB_BTN = (
        By.XPATH,
        "//div[contains(@class, 'tab-nav')]//button[normalize-space()='Tournament']",
    )
    TOURNAMENT_DASHBOARD = (By.CSS_SELECTOR, "main.tournament-dashboard")
    PARTICIPATING_HEADER = (
        By.XPATH,
        "//div[contains(translate(normalize-space(), 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 'PARTICIPATING BOTS (')]",
    )
    SELECT_ALL_BTN = (By.XPATH, "//button[normalize-space()='Select All']")
    RESET_SELECTION_BTN = (By.XPATH, "//button[normalize-space()='Reset']")
    BOT_CHIPS = (By.CSS_SELECTOR, ".bot-chip")
    SELECTED_BOT_CHIPS = (By.CSS_SELECTOR, ".bot-chip.selected")
    RUN_TOURNAMENT_BTN = (By.XPATH, "//button[contains(normalize-space(), 'Run Tournament')]")
    STOP_TOURNAMENT_BTN = (By.XPATH, "//button[contains(normalize-space(), 'Stop')]")
    RESET_STATS_BTN = (By.XPATH, "//button[normalize-space()='Reset Stats']")
    RESET_CONFIRM_LABEL = (By.XPATH, "//span[normalize-space()='RESET ALL?']")
    CONFIRM_YES_RESET_BTN = (By.XPATH, "//button[normalize-space()='Yes, Reset']")
    CONFIRM_CANCEL_BTN = (By.XPATH, "//button[normalize-space()='Cancel']")
    LEADERBOARD_ROWS = (By.CSS_SELECTOR, "table.tournament-table tbody tr")
    EMPTY_LEADERBOARD = (By.CSS_SELECTOR, ".empty-leaderboard-state")
    MATRIX_TITLE = (By.CSS_SELECTOR, ".win-rate-matrix-title")
    EMPTY_MATRIX = (By.CSS_SELECTOR, ".empty-matrix-state")

    def open_tournament_tab(self) -> None:
        """Click the Tournament tab button and wait for the tournament dashboard layout."""
        self.click_locator(*self.TOURNAMENT_TAB_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.TOURNAMENT_DASHBOARD)) > 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Tournament dashboard did not render",
        )

    def get_participating_bots_count(self) -> int:
        """Parse and return the integer N from 'Participating Bots (N)'."""

        def _parse_count(drv) -> int | bool:
            els = drv.find_elements(*self.PARTICIPATING_HEADER)
            if not els:
                return False
            text = els[0].get_attribute("textContent") or els[0].text
            match = re.search(r"Participating Bots\s*\((\d+)\)", text, re.IGNORECASE)
            if not match:
                return False
            return int(match.group(1))

        res = self.wait_until(_parse_count, message="Failed to parse Participating Bots counter")
        return 0 if res is False else int(res)

    def get_all_bot_chip_names(self) -> List[str]:
        """Return display names of all rendered bot chips."""
        self.wait_until(
            lambda d: len(d.find_elements(*self.BOT_CHIPS)) > 0,
            message="Bot chips did not load in Tournament view",
        )
        return self.get_texts(*self.BOT_CHIPS)

    def get_selected_bot_chip_names(self) -> List[str]:
        """Return display names of currently selected bot chips."""
        return self.get_texts(*self.SELECTED_BOT_CHIPS)

    def click_select_all_bots(self) -> int:
        """Click the 'Select All' button and wait until all bot chips are selected."""
        total_chips = len(self.get_all_bot_chip_names())
        self.click_locator(*self.SELECT_ALL_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.SELECTED_BOT_CHIPS)) == total_chips,
            message="Select All did not select every bot chip",
        )
        return self.get_participating_bots_count()

    def click_reset_bot_selection(self) -> int:
        """Click the 'Reset' bot selection button and wait until exactly 1 chip remains selected."""
        self.click_locator(*self.RESET_SELECTION_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.SELECTED_BOT_CHIPS)) == 1,
            message="Reset button did not reduce selection to 1 bot chip",
        )
        return self.get_participating_bots_count()

    def toggle_bot_chip(self, bot_display_name: str) -> None:
        """Click a specific bot chip by its display name."""
        chip_xpath = f"//div[contains(@class, 'bot-chip') and normalize-space()='{bot_display_name}']"
        self.click_locator(By.XPATH, chip_xpath)

    def start_and_stop_tournament_once_leaderboard_renders(self) -> List[Dict[str, str]]:
        """Start the tournament, wait for initial leaderboard rows to stream in, then click Stop."""
        self.click_locator(*self.RUN_TOURNAMENT_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.LEADERBOARD_ROWS)) > 0,
            timeout=config.SIMULATION_TIMEOUT,
            message="Leaderboard rows did not appear after starting tournament",
        )
        if self.is_visible(*self.STOP_TOURNAMENT_BTN):
            self.click_locator(*self.STOP_TOURNAMENT_BTN)
            self.wait_until(
                lambda d: len(d.find_elements(*self.RUN_TOURNAMENT_BTN)) > 0,
                timeout=config.DEFAULT_TIMEOUT,
                message="Tournament did not transition back to stopped state",
            )
        return self.get_leaderboard_entries()

    def get_leaderboard_entries(self) -> List[Dict[str, str]]:
        """Read rendered rows from the Tournament Leaderboard table."""

        def _read_rows(drv) -> List[Dict[str, str]] | bool:
            rows = drv.find_elements(*self.LEADERBOARD_ROWS)
            if not rows:
                return False
            entries = []
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 5:
                    return False
                entries.append(
                    {
                        "rank": cells[0].text.strip(),
                        "league": cells[1].text.strip(),
                        "name": cells[2].text.strip(),
                        "dominance": cells[3].text.strip(),
                        "elo": cells[4].text.strip(),
                    }
                )
            return entries

        return list(self.wait_until(_read_rows, message="Failed to read leaderboard table rows"))

    def is_h2h_matrix_rendered(self) -> bool:
        """Return True when the Head-to-Head WinRateMatrix table is visible."""
        return self.is_visible(*self.MATRIX_TITLE)

    def is_empty_leaderboard_shown(self) -> bool:
        """Return True when 'Waiting for tournament results...' placeholder is visible."""
        return self.is_visible(*self.EMPTY_LEADERBOARD)

    def open_reset_stats_confirmation(self) -> bool:
        """Click 'Reset Stats' and wait for the inline 'RESET ALL?' confirmation prompt."""
        self.click_locator(*self.RESET_STATS_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.RESET_CONFIRM_LABEL)) > 0,
            message="RESET ALL? confirmation prompt did not appear",
        )
        return True

    def cancel_reset_stats(self) -> None:
        """Click 'Cancel' on the inline reset confirmation prompt and verify it closes."""
        self.click_locator(*self.CONFIRM_CANCEL_BTN)
        self.wait_until(
            lambda d: not d.find_elements(*self.RESET_CONFIRM_LABEL),
            message="RESET ALL? prompt did not close after clicking Cancel",
        )

    def confirm_reset_stats(self) -> None:
        """Click 'Yes, Reset' and wait for the leaderboard to return to its empty waiting state."""
        self.click_locator(*self.CONFIRM_YES_RESET_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.EMPTY_LEADERBOARD)) > 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Leaderboard did not clear after confirming Yes, Reset",
        )
