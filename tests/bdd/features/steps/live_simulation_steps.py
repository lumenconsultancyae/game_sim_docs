"""Step definitions for Live Bot Simulation and Baseline Match Replay scenarios."""

from __future__ import annotations

from behave import given, then, when
import requests

from tests.bdd import config


@given('I navigate to the "{game_id}" arena in Live View')
def step_navigate_to_arena_live_view(context, game_id: str) -> None:
    context.current_game_id = game_id
    context.arena_page.open_arena_by_id(game_id)
    context.live_page.ensure_live_view_active()


@when('I select bot "{bot_a}" for slot "{slot_a}" and bot "{bot_b}" for slot "{slot_b}" from the bot drawer')
def step_select_bots_from_drawer(
    context, bot_a: str, slot_a: str, bot_b: str, slot_b: str
) -> None:
    drawer_bots = context.live_page.open_bot_slot_drawer(slot_a)
    context.live_page.save_step_screenshot("step3_bot_selection_drawer.png")
    assert bot_a in drawer_bots
    assert bot_b in drawer_bots

    context.live_page.select_bot_in_drawer(slot_a, bot_a)
    context.live_page.select_bot_in_drawer(slot_b, bot_b)

    selected_a, selected_b = context.live_page.get_selected_slot_labels()
    assert selected_a == bot_a
    assert selected_b == bot_b


@when('I enter the simulation seed "{seed_value}" and start the live simulation')
def step_enter_seed_and_run_simulation(context, seed_value: str) -> None:
    context.live_page.set_random_seed(seed_value)
    current_turn, max_turn = context.live_page.run_simulation_and_wait()
    context.last_sim_turns = (current_turn, max_turn)
    context.live_page.save_step_screenshot("step4_live_simulation_running.png")


@when("I select the first available baseline match file and start the live simulation")
def step_select_baseline_match_and_run(context) -> None:
    api_files = requests.get(
        f"{config.API_BASE_URL}/e2e-files",
        params={"game_id": context.current_game_id},
        timeout=5,
    ).json()
    ui_files = context.live_page.get_available_e2e_files()
    assert len(ui_files) > 0
    assert ui_files == api_files

    context.live_page.select_e2e_file(ui_files[0])
    current_turn, max_turn = context.live_page.run_simulation_and_wait()
    context.last_sim_turns = (current_turn, max_turn)


@then("the viewport canvas renders the match and playback loads multiple turns")
def step_verify_viewport_and_turns(context) -> None:
    _, max_turn = context.last_sim_turns
    assert max_turn > 0
    assert context.live_page.is_viewport_canvas_rendered() is True
    assert context.live_page.get_dom_anomalies() == []


@then("I can step through turns and expand the execution logs without DOM anomalies")
def step_verify_turn_stepping_and_logs(context) -> None:
    context.live_page.pause_playback_if_playing()
    cur_turn, max_turn = context.live_page.get_turn_counter()
    assert cur_turn == 0
    assert max_turn > 0

    next_turn, _ = context.live_page.step_next_turn()
    assert next_turn == 1

    new_toggle_label = context.live_page.toggle_full_log_history()
    assert new_toggle_label in ("Show Turn Only", "Show Full History")
    logs = context.live_page.get_execution_log_lines()
    assert len(logs) > 0
    assert context.live_page.get_dom_anomalies() == []


@when("I jump to the final turn of the match replay")
def step_jump_to_final_turn(context) -> None:
    context.live_page.pause_playback_if_playing()
    context.final_turn_state = context.live_page.jump_to_end_turn()


@then("the playback turn counter is positioned at the final turn")
def step_verify_at_final_turn(context) -> None:
    cur_turn, max_turn = context.final_turn_state
    assert max_turn > 0
    assert cur_turn == max_turn
    assert context.live_page.get_dom_anomalies() == []
