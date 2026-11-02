"""Step definitions for Tournament Bot Selection, Live Standings, and Reset Workflow scenarios."""

from __future__ import annotations

from behave import given, then, when
import requests

from tests.bdd import config


@given('I navigate to the "{game_id}" arena and open the Tournament tab')
def step_navigate_to_tournament_tab(context, game_id: str) -> None:
    context.current_game_id = game_id
    context.modified_games.add(game_id)
    # Ensure a clean starting tournament state for this arena
    requests.post(
        f"{config.API_BASE_URL}/reset-tournament",
        params={"game_id": game_id},
        timeout=5,
    )
    context.arena_page.open_arena_by_id(game_id)
    context.tournament_page.open_tournament_tab()


@when("I click Select All in the Participating Bots panel")
def step_click_select_all(context) -> None:
    context.selected_count = context.tournament_page.click_select_all_bots()


@then('the participating bots count matches the total bots returned by the backend API for "{game_id}"')
def step_verify_participating_count_matches_api(context, game_id: str) -> None:
    resp = requests.get(f"{config.API_BASE_URL}/bots", params={"game_id": game_id}, timeout=5)
    assert resp.status_code == 200
    api_bots = [b for b in resp.json() if b.get("name", "").strip()]
    assert context.selected_count == len(api_bots)
    assert len(context.tournament_page.get_selected_bot_chip_names()) == len(api_bots)


@when('I click Reset in the Participating Bots panel and toggle bot chip "{bot_name}"')
def step_reset_and_toggle_chip(context, bot_name: str) -> None:
    count_after_reset = context.tournament_page.click_reset_bot_selection()
    assert count_after_reset == 1
    context.tournament_page.toggle_bot_chip(bot_name)


@then("exactly {expected_count:d} participating bot chips are selected")
def step_verify_selected_chip_count(context, expected_count: int) -> None:
    assert context.tournament_page.get_participating_bots_count() == expected_count
    assert len(context.tournament_page.get_selected_bot_chip_names()) == expected_count
    assert context.tournament_page.get_dom_anomalies() == []


@given('I select bots "{bot_a}" and "{bot_b}" for tournament participation')
def step_select_two_bots_for_tournament(context, bot_a: str, bot_b: str) -> None:
    context.tournament_page.click_reset_bot_selection()
    target_bots = {bot_a, bot_b}
    # First select target bots so size > 1 before deselecting any non-target default chip
    currently_selected = set(context.tournament_page.get_selected_bot_chip_names())
    for bot_name in (bot_a, bot_b):
        if bot_name not in currently_selected:
            context.tournament_page.toggle_bot_chip(bot_name)
    # Deselect any chip not in target_bots
    for extra_bot in list(context.tournament_page.get_selected_bot_chip_names()):
        if extra_bot not in target_bots:
            context.tournament_page.toggle_bot_chip(extra_bot)
    assert set(context.tournament_page.get_selected_bot_chip_names()) == target_bots


@when("I start and stop the tournament once the leaderboard populates")
def step_start_and_stop_tournament(context) -> None:
    context.leaderboard_rows = (
        context.tournament_page.start_and_stop_tournament_once_leaderboard_renders()
    )
    context.tournament_page.save_step_screenshot("step5_tournament_leaderboard_populated.png")


@then('the Tournament Leaderboard and Head-to-Head Matrix display "{bot_a}" and "{bot_b}" with league badges')
def step_verify_leaderboard_and_matrix(context, bot_a: str, bot_b: str) -> None:
    entries = context.tournament_page.get_leaderboard_entries()
    rendered_names = {e["name"] for e in entries}
    assert {bot_a, bot_b}.issubset(rendered_names)
    for entry in entries:
        assert entry["league"] != ""
        assert float(entry["elo"]) > 0
    assert context.tournament_page.is_h2h_matrix_rendered() is True
    assert context.tournament_page.get_dom_anomalies() == []


@when("I open the Reset Stats confirmation prompt and cancel it")
def step_open_and_cancel_reset(context) -> None:
    context.tournament_page.open_reset_stats_confirmation()
    context.tournament_page.save_step_screenshot("step6_tournament_reset_confirm_prompt.png")
    context.tournament_page.cancel_reset_stats()


@then('the Tournament Leaderboard still displays "{bot_a}" and "{bot_b}"')
def step_verify_leaderboard_preserved(context, bot_a: str, bot_b: str) -> None:
    entries = context.tournament_page.get_leaderboard_entries()
    rendered_names = {e["name"] for e in entries}
    assert {bot_a, bot_b}.issubset(rendered_names)


@when("I open the Reset Stats confirmation prompt and confirm resetting all stats")
def step_open_and_confirm_reset(context) -> None:
    context.tournament_page.open_reset_stats_confirmation()
    context.tournament_page.confirm_reset_stats()
    context.tournament_page.save_step_screenshot("step7_tournament_after_reset.png")


@then('the Tournament Leaderboard returns to the waiting state and the backend stats for "{game_id}" are empty')
def step_verify_reset_state_and_api_parity(context, game_id: str) -> None:
    assert context.tournament_page.is_empty_leaderboard_shown() is True
    stats_resp = requests.get(
        f"{config.API_BASE_URL}/tournament-stats",
        params={"game_id": game_id},
        timeout=5,
    )
    assert stats_resp.status_code == 200
    stats_data = stats_resp.json()
    assert stats_data["leaderboard"] == []
    assert stats_data["tournaments_count"] == 0
    assert context.tournament_page.get_dom_anomalies() == []
