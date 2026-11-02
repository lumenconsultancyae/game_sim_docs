"""Page Object for the Live View simulation and replay workflow."""

from __future__ import annotations

from typing import List, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from tests.bdd import config
from tests.bdd.pages.base_page import BasePage


class LiveSimulationPage(BasePage):
    """Encapsulates Bot A/B selection, seed/replay inputs, simulation execution, and playback."""

    LIVE_TAB_BTN = (By.XPATH, "//div[contains(@class, 'tab-nav')]//button[normalize-space()='Live View']")
    BOT_SLOTS = (By.CSS_SELECTOR, ".bot-slots .bot-slot-v2")
    BOT_DRAWER_OPEN = (By.CSS_SELECTOR, ".bot-drawer.open")
    DRAWER_BOT_CARDS = (By.CSS_SELECTOR, ".bot-drawer.open .drawer-bot-card")
    SEED_INPUT = (By.CSS_SELECTOR, "input[placeholder='Random Seed']")
    MATCH_SELECT = (By.XPATH, "//select[.//option[contains(text(), '-- Match --')]]")
    RUN_SIMULATION_BTN = (By.XPATH, "//button[contains(normalize-space(), 'Run Simulation') or normalize-space()='...']")
    TURN_COUNTER = (By.CSS_SELECTOR, ".playback-bar .turn-counter")
    JUMP_START_BTN = (By.CSS_SELECTOR, ".playback-controls button[title='Jump to Start']")
    PREV_TURN_BTN = (By.CSS_SELECTOR, ".playback-controls button[title='Previous Turn']")
    NEXT_TURN_BTN = (By.CSS_SELECTOR, ".playback-controls button[title='Next Turn']")
    JUMP_END_BTN = (By.CSS_SELECTOR, ".playback-controls button[title='Jump to End']")
    PLAY_PAUSE_BTN = (By.CSS_SELECTOR, ".playback-controls button.play-btn")
    LOGS_HEADER = (By.XPATH, "//div[.//h3[contains(normalize-space(), 'Execution Logs')]]")
    LOGS_ITEMS = (By.CSS_SELECTOR, ".logs-scroll > div")

    def ensure_live_view_active(self) -> None:
        """Switch to the Live View tab if not already active."""
        self.click_locator(*self.LIVE_TAB_BTN)
        self.wait_until(
            lambda d: len(d.find_elements(*self.BOT_SLOTS)) == 2,
            message="Live View bot slots did not appear",
        )

    def open_bot_slot_drawer(self, slot: str) -> List[str]:
        """Click Bot A ('A') or Bot B ('B') slot and wait for the bot drawer to populate."""
        slot_upper = slot.upper()
        slot_idx = 0 if slot_upper == "A" else 1
        expected_header = f"Select Bot {slot_upper}"

        def _open(drv) -> List[str] | bool:
            slots = drv.find_elements(*self.BOT_SLOTS)
            if len(slots) <= slot_idx:
                return False
            drawer_headers = drv.find_elements(By.CSS_SELECTOR, ".bot-drawer.open .drawer-header h3")
            current_header = (
                (drawer_headers[0].get_attribute("textContent") or "").strip()
                if drawer_headers
                else ""
            )
            if current_header != expected_header:
                drv.execute_script("arguments[0].click();", slots[slot_idx])
                return False
            cards = drv.find_elements(*self.DRAWER_BOT_CARDS)
            if not cards:
                return False
            names = [
                (
                    c.find_element(By.XPATH, "./div/div[1]").get_attribute(
                        "textContent"
                    )
                    or ""
                ).strip()
                for c in cards
            ]
            return names if all(names) else False

        return list(
            self.wait_until(_open, timeout=config.DEFAULT_TIMEOUT, message=f"Drawer for Bot {slot} did not populate")
        )

    def select_bot_in_drawer(self, slot: str, bot_name: str) -> None:
        """Open the drawer for the given slot ('A' or 'B') and click the requested bot card."""
        slot_idx = 0 if slot.upper() == "A" else 1
        self.open_bot_slot_drawer(slot)
        card_xpath = (
            "//div[contains(@class, 'bot-drawer') and contains(@class, 'open')]"
            f"//div[contains(@class, 'drawer-bot-card') and .//div[normalize-space()='{bot_name}']]"
        )

        def _click_card(drv) -> bool:
            cards = drv.find_elements(By.XPATH, card_xpath)
            if not cards:
                return False
            drv.execute_script("arguments[0].click();", cards[0])
            return True

        self.wait_until(_click_card, timeout=config.DEFAULT_TIMEOUT, message=f"Bot card {bot_name} not found")
        self.wait_until(
            lambda d: not d.find_elements(*self.BOT_DRAWER_OPEN)
            and self.get_selected_slot_labels()[slot_idx] == bot_name,
            timeout=config.DEFAULT_TIMEOUT,
            message=f"Slot {slot} did not update to {bot_name}",
        )

    def get_selected_slot_labels(self) -> Tuple[str, str]:
        """Return the current display labels inside Bot Slot A and Bot Slot B."""

        def _read_slots(drv) -> Tuple[str, str] | bool:
            slots = drv.find_elements(By.CSS_SELECTOR, ".bot-slots .bot-slot-v2 .name-label")
            if len(slots) != 2:
                return False
            a_lbl = (slots[0].get_attribute("textContent") or slots[0].text or "").strip()
            b_lbl = (slots[1].get_attribute("textContent") or slots[1].text or "").strip()
            return (a_lbl, b_lbl)

        return tuple(self.wait_until(_read_slots, message="Failed to read Bot A and Bot B slot labels"))  # type: ignore[return-value]

    def set_random_seed(self, seed_value: str) -> None:
        """Enter a deterministic seed string into the Random Seed input field."""
        self.fill_input(*self.SEED_INPUT, seed_value)

    def get_available_e2e_files(self) -> List[str]:
        """Return all non-empty option values in the E2E baseline match dropdown."""

        def _options(drv) -> List[str] | bool:
            select_el = drv.find_element(*self.MATCH_SELECT)
            options = [
                opt.get_attribute("value") or ""
                for opt in select_el.find_elements(By.TAG_NAME, "option")
            ]
            non_empty = [o for o in options if o]
            return non_empty if non_empty else False

        return list(self.wait_until(_options, message="E2E match select options did not populate"))

    def select_e2e_file(self, filename: str) -> None:
        """Select a specific baseline match file from the dropdown."""

        def _select(drv) -> bool:
            select_el = drv.find_element(*self.MATCH_SELECT)
            Select(select_el).select_by_value(filename)
            return select_el.get_attribute("value") == filename

        self.wait_until(_select, message=f"Failed to select E2E file {filename}")

    def run_simulation_and_wait(self) -> Tuple[int, int]:
        """Click Run Simulation and wait until history turns load and simulation finishes."""
        self.click_locator(*self.RUN_SIMULATION_BTN)

        def _sim_complete(drv) -> Tuple[int, int] | bool:
            # Ensure SIMULATING MATCH... overlay is gone and turn counter has max_turn > 0
            counter_els = drv.find_elements(*self.TURN_COUNTER)
            if not counter_els:
                return False
            text = counter_els[0].text.strip()
            if "/" not in text:
                return False
            parts = [p.strip() for p in text.split("/")]
            if len(parts) != 2 or not (parts[0].isdigit() and parts[1].isdigit()):
                return False
            current_turn, max_turn = int(parts[0]), int(parts[1])
            if max_turn <= 0:
                return False
            return (current_turn, max_turn)

        return tuple(
            self.wait_until(
                _sim_complete,
                timeout=config.SIMULATION_TIMEOUT,
                message="Simulation did not complete within timeout",
            )
        )  # type: ignore[return-value]

    def pause_playback_if_playing(self) -> None:
        """Ensure automatic turn playback is paused so turn navigation is deterministic."""
        # Clicking Jump to Start in App.tsx explicitly calls setIsPlaying(false) and setCurrentTurnIndex(0)
        self.click_locator(*self.JUMP_START_BTN)
        self.wait_until(
            lambda d: self.get_turn_counter()[0] == 0,
            timeout=config.DEFAULT_TIMEOUT,
            message="Failed to jump to turn 0 and pause playback",
        )

    def get_turn_counter(self) -> Tuple[int, int]:
        """Return (current_turn_index, max_turn_index) from the playback footer."""
        text = self.get_text(*self.TURN_COUNTER)
        parts = [p.strip() for p in text.split("/")]
        return (int(parts[0]), int(parts[1]))

    def step_next_turn(self) -> Tuple[int, int]:
        """Click the Next Turn button and return the updated (current_turn, max_turn)."""
        before_turn, _ = self.get_turn_counter()
        self.click_locator(*self.NEXT_TURN_BTN)
        self.wait_until(
            lambda d: self.get_turn_counter()[0] > before_turn,
            message="Turn counter did not advance after clicking Next Turn",
        )
        return self.get_turn_counter()

    def jump_to_end_turn(self) -> Tuple[int, int]:
        """Click the Jump to End button and return the updated (current_turn, max_turn)."""
        self.click_locator(*self.JUMP_END_BTN)
        self.wait_until(
            lambda d: self.get_turn_counter()[0] == self.get_turn_counter()[1] and self.get_turn_counter()[1] > 0,
            message="Turn counter did not reach final turn after clicking Jump to End",
        )
        return self.get_turn_counter()

    def toggle_full_log_history(self) -> str:
        """Click the Execution Logs header to toggle between single-turn and full-history logs."""
        toggle_btn = (By.XPATH, "//h3[contains(normalize-space(), 'Execution Logs')]/following-sibling::button")
        before_label = self.get_text(*toggle_btn)
        self.click_locator(By.XPATH, "//h3[contains(normalize-space(), 'Execution Logs')]/..")
        self.wait_until(
            lambda d: d.find_element(*toggle_btn).text.strip() != before_label,
            message="Execution logs mode toggle did not update button label",
        )
        return self.get_text(*toggle_btn)

    def get_execution_log_lines(self) -> List[str]:
        """Return visible log lines inside the Execution Logs scroll container."""
        return self.get_texts(*self.LOGS_ITEMS)

    def is_viewport_canvas_rendered(self) -> bool:
        """Return True if the Viewport scene container is rendered with non-zero dimensions."""

        def _rendered(drv) -> bool:
            script = """
            const scene = document.querySelector('.viewport-container > div > div');
            return Boolean(scene && scene.clientWidth > 0 && scene.clientHeight > 0);
            """
            return bool(drv.execute_script(script))

        return bool(self.wait_until(_rendered, message="Viewport scene did not render"))
