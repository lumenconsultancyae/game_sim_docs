"""Page Object for the Landing Page (GameSelection) and Header Arena Switcher."""

from __future__ import annotations

from typing import Dict, List
from selenium.webdriver.common.by import By

from tests.bdd import config
from tests.bdd.pages.base_page import BasePage


class ArenaSelectionPage(BasePage):
    """Encapsulates arena discovery on the landing page and arena switching in the header."""

    LANDING_CONTAINER = (By.CSS_SELECTOR, ".landing-container")
    LANDING_TITLE = (By.CSS_SELECTOR, ".landing-title")
    LANDING_BADGE = (By.CSS_SELECTOR, ".landing-badge")
    GAME_CARDS = (By.CSS_SELECTOR, ".game-grid .game-card")
    BREADCRUMB_HOME = (By.XPATH, "//div[contains(@class, 'breadcrumb-item') and .//span[text()='Games']]")
    ACTIVE_ARENA_HEADER = (By.CSS_SELECTOR, ".game-selector-container .breadcrumb-item.active h1")
    ARENA_DROPDOWN_TRIGGER = (By.CSS_SELECTOR, ".game-selector-container .breadcrumb-item.active")
    ARENA_DROPDOWN_MENU = (By.CSS_SELECTOR, ".game-dropdown-menu")
    ARENA_DROPDOWN_ITEMS = (By.CSS_SELECTOR, ".game-dropdown-menu .game-dropdown-item")

    def open_landing_page(self) -> None:
        """Navigate to the platform root landing page and wait for game cards to render."""
        if not self.driver.current_url.startswith(config.WEB_BASE_URL):
            self.driver.get(config.WEB_BASE_URL)
        else:
            self.driver.execute_script("if (window.location.hash) { window.location.hash = ''; }")
        self.wait_until(
            lambda d: len(d.find_elements(*self.GAME_CARDS)) > 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Landing page game cards did not render",
        )
        self.driver.execute_script(
            "const h = document.querySelector('.landing-header'); if (h) h.scrollIntoView({block: 'start'});"
        )

    def open_arena_by_id(self, game_id: str) -> None:
        """Navigate directly to a specific arena via hash routing and wait for header."""
        if not self.driver.current_url.startswith(config.WEB_BASE_URL):
            self.driver.get(f"{config.WEB_BASE_URL}/#{game_id}")
        else:
            self.driver.execute_script(f"window.location.hash = '{game_id}';")
        self.wait_until(
            lambda d: len(d.find_elements(*self.ACTIVE_ARENA_HEADER)) > 0
            and d.find_element(*self.ACTIVE_ARENA_HEADER).text.strip() not in ("", "Simulation"),
            timeout=config.DEFAULT_TIMEOUT,
            message=f"Arena header did not load for #{game_id}",
        )

    def get_landing_title(self) -> str:
        """Return the main heading text on the landing page."""
        return self.get_text(*self.LANDING_TITLE)

    def get_landing_badge(self) -> str:
        """Return the badge text on the landing page."""
        return self.get_text(*self.LANDING_BADGE)

    def get_arena_cards(self) -> List[Dict[str, str]]:
        """Return ordered list of arena card names and descriptions displayed on the landing page."""

        def _extract(drv) -> List[Dict[str, str]] | bool:
            cards = drv.find_elements(*self.GAME_CARDS)
            if not cards:
                return False
            result = []
            for card in cards:
                name = card.find_element(By.TAG_NAME, "h3").text.strip()
                desc = card.find_element(By.TAG_NAME, "p").text.strip()
                if not name:
                    return False
                result.append({"name": name, "description": desc})
            return result

        return list(self.wait_until(_extract, message="Failed to read arena cards"))

    def select_arena_card(self, arena_name: str) -> None:
        """Click the arena card matching the given display name and wait for the arena dashboard."""
        card_xpath = (
            f"//div[contains(@class, 'game-card') and .//h3[normalize-space()='{arena_name}']]"
        )
        self.click_locator(By.XPATH, card_xpath)
        self.wait_until(
            lambda d: len(d.find_elements(*self.ACTIVE_ARENA_HEADER)) > 0
            and d.find_element(*self.ACTIVE_ARENA_HEADER).text.strip() == arena_name,
            timeout=config.DEFAULT_TIMEOUT,
            message=f"Failed to transition into arena '{arena_name}'",
        )

    def get_active_arena_name(self) -> str:
        """Return the currently active arena name from the top breadcrumb header."""
        return self.get_text(*self.ACTIVE_ARENA_HEADER)

    def get_current_hash(self) -> str:
        """Return the current URL hash without the leading '#'."""
        return str(self.driver.execute_script("return window.location.hash.replace('#', '');") or "")

    def open_arena_switcher_dropdown(self) -> List[str]:
        """Open the header arena dropdown menu and return the list of arena names."""

        def _ensure_open(drv) -> List[str] | bool:
            if not drv.find_elements(*self.ARENA_DROPDOWN_MENU):
                trigger = drv.find_element(*self.ARENA_DROPDOWN_TRIGGER)
                drv.execute_script("arguments[0].click();", trigger)
                return False
            items = drv.find_elements(By.CSS_SELECTOR, ".game-dropdown-menu .game-name")
            if not items:
                return False
            names = [(el.get_attribute("textContent") or "").strip() for el in items]
            return names if all(names) else False

        return list(
            self.wait_until(_ensure_open, message="Arena dropdown items did not appear")
        )

    def switch_arena_via_dropdown(self, target_arena_name: str) -> None:
        """Select a target arena from the header switcher dropdown and wait for load."""
        self.open_arena_switcher_dropdown()
        item_xpath = (
            "//div[contains(@class, 'game-dropdown-item') and "
            f".//span[contains(@class, 'game-name') and normalize-space()='{target_arena_name}']]"
        )

        def _click_item(drv) -> bool:
            els = drv.find_elements(By.XPATH, item_xpath)
            if not els:
                return False
            drv.execute_script("arguments[0].click();", els[0])
            return True

        self.wait_until(_click_item, message=f"Dropdown item {target_arena_name} not found")
        self.wait_until(
            lambda d: (
                d.find_element(*self.ACTIVE_ARENA_HEADER).get_attribute("textContent") or ""
            ).strip()
            == target_arena_name,
            timeout=config.DEFAULT_TIMEOUT,
            message=f"Header did not update to '{target_arena_name}'",
        )

    def click_games_home_breadcrumb(self) -> None:
        """Click the 'Games' breadcrumb link to return to the landing page."""
        self.click_locator(*self.BREADCRUMB_HOME)
        self.wait_until(
            lambda d: len(d.find_elements(*self.GAME_CARDS)) > 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Did not return to landing page after clicking Games breadcrumb",
        )
