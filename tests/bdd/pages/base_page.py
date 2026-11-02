"""Base Page Object encapsulating retry-aware WebDriver operations and DOM health checks."""

from __future__ import annotations

import os
from typing import Any, Callable, List, TypeVar

from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from tests.bdd import config

T = TypeVar("T")

IGNORED_EXCEPTIONS = (NoSuchElementException, StaleElementReferenceException)


class BasePage:
    """Driver-agnostic base adapter for explicit waits, atomic actions, and teardown helpers."""

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver

    def wait_until(
        self,
        predicate: Callable[[WebDriver], T],
        timeout: float = config.DEFAULT_TIMEOUT,
        message: str = "",
    ) -> T:
        """Execute a retry-aware predicate ignoring transient DOM re-render exceptions."""
        wait = WebDriverWait(
            self.driver,
            timeout=timeout,
            poll_frequency=config.POLL_FREQUENCY,
            ignored_exceptions=IGNORED_EXCEPTIONS,
        )
        return wait.until(predicate, message=message)

    def click_locator(
        self, by: str, selector: str, timeout: float = config.DEFAULT_TIMEOUT
    ) -> None:
        """Atomically locate and click a visible, enabled element across React re-renders."""

        def _click(drv: WebDriver) -> bool:
            el = drv.find_element(by, selector)
            if not (el.is_displayed() and el.is_enabled()):
                return False
            try:
                el.click()
            except WebDriverException:
                drv.execute_script("arguments[0].click();", el)
            return True

        self.wait_until(_click, timeout=timeout, message=f"Click timed out for {selector}")

    def fill_input(
        self, by: str, selector: str, value: str, timeout: float = config.DEFAULT_TIMEOUT
    ) -> None:
        """Atomically locate, clear, and populate a text input."""

        def _fill(drv: WebDriver) -> bool:
            el = drv.find_element(by, selector)
            if not (el.is_displayed() and el.is_enabled()):
                return False
            el.clear()
            el.send_keys(value)
            return True

        self.wait_until(_fill, timeout=timeout, message=f"Input fill timed out for {selector}")

    def get_text(
        self, by: str, selector: str, timeout: float = config.DEFAULT_TIMEOUT
    ) -> str:
        """Atomically locate an element and return its trimmed textContent."""

        def _read(drv: WebDriver) -> str | bool:
            el = drv.find_element(by, selector)
            text = (el.get_attribute("textContent") or el.text or "").strip()
            return text if text else False

        res = self.wait_until(_read, timeout=timeout, message=f"Text read timed out for {selector}")
        return str(res)

    def get_texts(self, by: str, selector: str) -> List[str]:
        """Return trimmed textContent for all matching elements currently in the DOM."""
        try:
            elements = self.driver.find_elements(by, selector)
            out = []
            for el in elements:
                txt = (el.get_attribute("textContent") or el.text or "").strip()
                if txt:
                    out.append(txt)
            return out
        except StaleElementReferenceException:
            elements = self.driver.find_elements(by, selector)
            return [
                (el.get_attribute("textContent") or el.text or "").strip()
                for el in elements
                if (el.get_attribute("textContent") or el.text or "").strip()
            ]

    def is_visible(self, by: str, selector: str) -> bool:
        """Return True if at least one matching element is present and displayed."""
        try:
            elements = self.driver.find_elements(by, selector)
            return any(el.is_displayed() for el in elements)
        except StaleElementReferenceException:
            return False

    def save_step_screenshot(self, filename: str) -> str:
        """Capture a screenshot into the configured artifact directory."""
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
        path = os.path.join(config.SCREENSHOT_DIR, filename)
        self.driver.save_screenshot(path)
        return path

    def get_dom_anomalies(self) -> List[str]:
        """Inspect live DOM for unresolved placeholders, NaN/undefined tokens, or broken images."""
        script = """
        const anomalies = [];
        const bodyText = document.body ? document.body.innerText : '';
        if (bodyText.includes('undefined')) anomalies.push('Found literal "undefined" in visible text');
        if (bodyText.includes('NaN')) anomalies.push('Found literal "NaN" in visible text');
        if (bodyText.includes('{{') || bodyText.includes('}}')) {
            anomalies.push('Found unresolved template braces in visible text');
        }
        const images = Array.from(document.querySelectorAll('img'));
        for (const img of images) {
            if (!img.complete || img.naturalWidth === 0) {
                anomalies.push(`Broken image: ${img.src}`);
            }
        }
        return anomalies;
        """
        return list(self.driver.execute_script(script) or [])

    # -----------------------------------------------------------------------
    # Idempotent Conditional Teardown Helpers
    # -----------------------------------------------------------------------

    def close_bot_drawer_if_open(self) -> None:
        """Close the slide-out bot selection drawer if it is currently open."""
        if self.is_visible(By.CSS_SELECTOR, ".bot-drawer.open"):
            try:
                self.click_locator(By.CSS_SELECTOR, ".bot-drawer.open .drawer-header button", timeout=3.0)
                self.wait_until(
                    lambda d: not d.find_elements(By.CSS_SELECTOR, ".bot-drawer.open"),
                    timeout=3.0,
                )
            except TimeoutException:
                pass

    def close_game_dropdown_if_open(self) -> None:
        """Close the header arena switcher dropdown if it is currently open."""
        if self.is_visible(By.CSS_SELECTOR, ".game-dropdown-menu"):
            try:
                self.click_locator(By.CSS_SELECTOR, ".game-selector-container .breadcrumb-item.active", timeout=3.0)
                self.wait_until(
                    lambda d: not d.find_elements(By.CSS_SELECTOR, ".game-dropdown-menu"),
                    timeout=3.0,
                )
            except TimeoutException:
                pass

    def dismiss_reset_confirm_if_open(self) -> None:
        """Cancel the inline 'RESET ALL?' tournament confirmation prompt if present."""
        cancel_xpath = "//button[normalize-space()='Cancel']"
        if self.is_visible(By.XPATH, cancel_xpath):
            try:
                self.click_locator(By.XPATH, cancel_xpath, timeout=3.0)
            except TimeoutException:
                pass
