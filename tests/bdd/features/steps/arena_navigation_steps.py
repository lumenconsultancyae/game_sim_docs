"""Step definitions for Arena Discovery and Navigation scenarios."""

from __future__ import annotations

from behave import given, then, when
import requests

from tests.bdd import config


@given("I open the platform landing page")
def step_open_landing_page(context) -> None:
    context.arena_page.open_landing_page()
    context.arena_page.save_step_screenshot("step1_landing_page_ready.png")


@then('the landing page displays the title "{expected_title}" and badge "{expected_badge}"')
def step_verify_landing_title_and_badge(
    context, expected_title: str, expected_badge: str
) -> None:
    assert context.arena_page.get_landing_title() == expected_title
    assert context.arena_page.get_landing_badge() == expected_badge


@then("all registered arenas from the backend API are displayed as unique cards without DOM anomalies")
def step_verify_landing_cards_parity(context) -> None:
    root_resp = requests.get(f"{config.API_BASE_URL}/", timeout=5)
    assert root_resp.status_code == 200
    game_ids = root_resp.json()["games"]

    expected_names = []
    for gid in game_ids:
        meta_resp = requests.get(f"{config.API_BASE_URL}/metadata", params={"game_id": gid}, timeout=5)
        assert meta_resp.status_code == 200
        expected_names.append(meta_resp.json()["name"])

    cards = context.arena_page.get_arena_cards()
    rendered_names = [c["name"] for c in cards]

    # Verify zero duplicate cards and exact parity with API metadata
    assert len(rendered_names) == len(set(rendered_names)), f"Duplicate arena cards: {rendered_names}"
    assert set(rendered_names) == set(expected_names)
    assert context.arena_page.get_dom_anomalies() == []


@when('I enter the "{arena_name}" arena from the landing page')
def step_enter_arena_from_landing(context, arena_name: str) -> None:
    context.arena_page.select_arena_card(arena_name)
    context.arena_page.save_step_screenshot("step2_entered_arena_live_view.png")


@then('the active arena header displays "{expected_name}" and the URL hash is "{expected_hash}"')
def step_verify_active_arena_header_and_hash(
    context, expected_name: str, expected_hash: str
) -> None:
    assert context.arena_page.get_active_arena_name() == expected_name
    assert context.arena_page.get_current_hash() == expected_hash
    assert context.arena_page.get_dom_anomalies() == []


@when('I switch to the "{target_arena}" arena using the header arena dropdown')
def step_switch_arena_via_dropdown(context, target_arena: str) -> None:
    dropdown_names = context.arena_page.open_arena_switcher_dropdown()
    assert target_arena in dropdown_names
    context.arena_page.switch_arena_via_dropdown(target_arena)


@when("I click the Games home breadcrumb")
def step_click_games_home_breadcrumb(context) -> None:
    context.arena_page.click_games_home_breadcrumb()
