"""Page Object for UX/UI Redesign, URL State Sync, Inline Validation, Pagination, and Responsive Navigation."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from tests.bdd import config
from tests.bdd.pages.base_page import BasePage


class UxRedesignPage(BasePage):
    """Encapsulates WAI-ARIA dialogs, toast undo, inline form validation, pagination, and responsive checks."""

    SEED_INPUT = (By.CSS_SELECTOR, "[data-testid='seed-input']")
    SEED_ERROR = (By.CSS_SELECTOR, "[data-testid='seed-input-error']")
    RUN_SIM_BTN = (By.CSS_SELECTOR, "[data-testid='run-simulation-btn']")

    CODINGAME_TAB_BTN = (
        By.XPATH,
        "//div[contains(@class, 'tab-nav')]//button[contains(normalize-space(), 'CodinGame API')]",
    )
    TOGGLE_DEPLOY_BTN = (By.CSS_SELECTOR, "[data-testid='toggle-deploy-form-btn']")
    DEPLOY_DRAWER = (By.CSS_SELECTOR, "[data-testid='codingame-deploy-drawer']")
    TARGET_ID_INPUT = (By.CSS_SELECTOR, "[data-testid='codingame-target-id-input']")
    TARGET_ID_ERROR = (By.CSS_SELECTOR, "[data-testid='codingame-target-id-error']")
    SUBMIT_ARENA_BTN = (By.CSS_SELECTOR, "[data-testid='codingame-submit-btn']")

    LEADERBOARD_SEARCH = (By.CSS_SELECTOR, "[data-testid='leaderboard-search-input']")
    LEADERBOARD_EMPTY_FILTER = (By.CSS_SELECTOR, "[data-testid='leaderboard-empty-filter']")
    LEADERBOARD_CLEAR_FILTERS = (By.CSS_SELECTOR, "[data-testid='leaderboard-clear-filters']")
    PAGINATION_STATUS = (By.CSS_SELECTOR, "[data-testid='pagination-status']")
    PAGINATION_PAGE_SIZE = (By.CSS_SELECTOR, "[data-testid='pagination-page-size']")

    ALERT_DIALOG = (By.CSS_SELECTOR, "[role='alertdialog'][aria-modal='true']")
    TOAST_UNDO_BTN = (By.CSS_SELECTOR, "[data-testid='toast-undo-btn']")

    COMMAND_PALETTE_BTN = (By.CSS_SELECTOR, "[data-testid='open-command-palette-btn']")
    COMMAND_PALETTE_DIALOG = (By.CSS_SELECTOR, "[data-testid='command-palette-dialog']")
    COMMAND_PALETTE_INPUT = (By.CSS_SELECTOR, "[data-testid='command-palette-input']")

    MOBILE_MENU_TOGGLE = (By.CSS_SELECTOR, "[data-testid='mobile-menu-toggle']")
    OFFCANVAS_DRAWER = (By.CSS_SELECTOR, "[data-testid='offcanvas-drawer']")
    OFFCANVAS_DRAWER_TOURNAMENT = (By.CSS_SELECTOR, "[data-testid='drawer-tab-tournament']")

    def set_viewport(self, width: int, height: int) -> None:
        """Emulate viewport dimensions cleanly via CDP without hanging Headless Chromium."""
        self.driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {
                "width": width,
                "height": height,
                "deviceScaleFactor": 1,
                "mobile": width < 768,
            },
        )

    def has_zero_horizontal_overflow(self) -> bool:
        """Verify document.documentElement.scrollWidth <= window.innerWidth."""
        return bool(
            self.driver.execute_script(
                "return document.documentElement.scrollWidth <= window.innerWidth;"
            )
        )

    def get_url_search_param(self, key: str) -> str:
        """Read a query parameter from window.location.search."""
        return str(
            self.driver.execute_script(
                "return new URLSearchParams(window.location.search).get(arguments[0]) || '';",
                key,
            )
        )

    def reload_page(self) -> None:
        """Trigger a browser reload and wait for document readyState complete."""
        self.driver.refresh()
        self.wait_until(
            lambda d: d.execute_script("return document.readyState") == "complete",
            timeout=config.DEFAULT_TIMEOUT,
        )

    def submit_seed_and_check_validation(self, seed_value: str) -> None:
        """Enter a seed value and click Run Simulation."""
        self.fill_input(*self.SEED_INPUT, seed_value)
        self.click_locator(*self.RUN_SIM_BTN)

    def is_seed_validation_error_visible(self) -> bool:
        """Wait for the inline seed validation error alert to appear and verify aria-invalid."""
        self.wait_until(
            lambda d: self.is_visible(*self.SEED_ERROR),
            timeout=config.DEFAULT_TIMEOUT,
            message="Expected inline seed validation error alert",
        )
        aria_invalid = self.driver.find_element(*self.SEED_INPUT).get_attribute("aria-invalid")
        return aria_invalid == "true"

    def fix_seed_input_and_verify_error_clears(self, valid_seed: str) -> bool:
        """Type a valid seed and verify the inline error clears immediately."""
        self.fill_input(*self.SEED_INPUT, valid_seed)
        self.wait_until(
            lambda d: not self.is_visible(*self.SEED_ERROR),
            timeout=config.DEFAULT_TIMEOUT,
            message="Expected inline seed error to clear after valid input",
        )
        return True

    def open_codingame_tab(self) -> None:
        """Switch to the CodinGame API tab."""
        self.click_locator(*self.CODINGAME_TAB_BTN)
        self.wait_until(
            lambda d: self.is_visible(*self.TOGGLE_DEPLOY_BTN),
            timeout=config.DEFAULT_TIMEOUT,
            message="CodinGame panel did not render",
        )

    def is_deploy_drawer_collapsed(self) -> bool:
        """Return True when the progressive-disclosure deployment drawer is collapsed."""
        return not self.is_visible(*self.DEPLOY_DRAWER)

    def expand_deploy_drawer(self) -> None:
        """Click '+ Deploy / Configure Bot' to expand the deployment form."""
        self.click_locator(*self.TOGGLE_DEPLOY_BTN)
        self.wait_until(
            lambda d: self.is_visible(*self.DEPLOY_DRAWER),
            timeout=config.DEFAULT_TIMEOUT,
            message="Deployment form drawer did not expand",
        )

    def trigger_empty_target_id_error(self) -> bool:
        """Clear targetId in CodinGameDeployForm, submit, and verify inline role='alert' error."""
        el = self.driver.find_element(*self.TARGET_ID_INPUT)
        self.driver.execute_script(
            """
            const input = arguments[0];
            const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            setter.call(input, '');
            input.dispatchEvent(new Event('input', { bubbles: true }));
            """,
            el,
        )
        self.click_locator(*self.SUBMIT_ARENA_BTN)
        self.wait_until(
            lambda d: self.is_visible(*self.TARGET_ID_ERROR),
            timeout=config.DEFAULT_TIMEOUT,
            message="Target ID inline validation error did not appear",
        )
        return self.driver.find_element(*self.TARGET_ID_ERROR).get_attribute("role") == "alert"

    def filter_leaderboard_and_wait_for_url_sync(self, query: str) -> None:
        """Enter a search filter in the leaderboard toolbar and wait for URL ?q= synchronization."""
        self.fill_input(*self.LEADERBOARD_SEARCH, query)
        self.wait_until(
            lambda d: self.get_url_search_param("q") == query,
            timeout=config.DEFAULT_TIMEOUT,
            message=f"URL search param ?q={query} did not synchronize",
        )

    def change_page_size(self, size: int) -> None:
        """Select a new rows-per-page option in the PaginationBar."""
        select_el = self.driver.find_element(*self.PAGINATION_PAGE_SIZE)
        Select(select_el).select_by_value(str(size))
        self.wait_until(
            lambda d: self.get_url_search_param("pageSize") == str(size),
            timeout=config.DEFAULT_TIMEOUT,
        )

    def is_alert_dialog_open(self) -> bool:
        """Verify an accessible WAI-ARIA alertdialog modal is open."""
        return self.is_visible(*self.ALERT_DIALOG)

    def click_toast_undo_and_wait_for_restore(self) -> None:
        """Click the 'Undo Reset' button inside the toast notification and wait for leaderboard rows."""
        self.click_locator(*self.TOAST_UNDO_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "table.tournament-table tbody tr")) > 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Leaderboard rows were not restored after clicking Undo Reset",
        )

    def open_and_close_mobile_drawer(self) -> bool:
        """Open the responsive off-canvas navigation drawer and navigate to Tournament tab."""
        self.click_locator(*self.MOBILE_MENU_TOGGLE)
        self.wait_until(
            lambda d: self.is_visible(*self.OFFCANVAS_DRAWER),
            timeout=config.DEFAULT_TIMEOUT,
            message="Off-canvas navigation drawer did not open",
        )
        self.click_locator(*self.OFFCANVAS_DRAWER_TOURNAMENT)
        self.wait_until(
            lambda d: not self.is_visible(*self.OFFCANVAS_DRAWER),
            timeout=config.DEFAULT_TIMEOUT,
            message="Off-canvas navigation drawer did not auto-close on navigation",
        )
        return True
