"""Step definitions for UX Redesign, URL State Sync, Inline Validation, Pagination, and Responsive Navigation."""

from __future__ import annotations

from behave import then, when
from selenium.webdriver.common.by import By


@when('I enter an invalid simulation seed "{seed_value}" and submit the live simulation form')
def step_submit_invalid_seed(context, seed_value: str) -> None:
    context.ux_page.submit_seed_and_check_validation(seed_value)


@then("an inline seed validation alert is displayed with aria-invalid enabled")
def step_verify_seed_validation_alert(context) -> None:
    assert context.ux_page.is_seed_validation_error_visible(), (
        "Expected inline seed validation alert with aria-invalid='true'"
    )


@when('I correct the simulation seed to "{valid_seed}"')
def step_fix_simulation_seed(context, valid_seed: str) -> None:
    context.ux_page.fix_seed_input_and_verify_error_clears(valid_seed)


@then("the inline seed validation alert clears immediately")
def step_verify_seed_alert_cleared(context) -> None:
    assert not context.ux_page.is_visible(*context.ux_page.SEED_ERROR), (
        "Expected inline seed validation error to be cleared"
    )


@when("I switch to the CodinGame API tab")
def step_switch_to_codingame_tab(context) -> None:
    context.ux_page.open_codingame_tab()


@then("the bot deployment form is collapsed by default behind the progressive disclosure button")
def step_verify_deploy_form_collapsed(context) -> None:
    assert context.ux_page.is_deploy_drawer_collapsed(), (
        "Expected bot deployment form to be collapsed by default"
    )


@when("I expand the bot deployment form and submit with an empty target ID")
def step_expand_and_submit_empty_target_id(context) -> None:
    context.ux_page.expand_deploy_drawer()
    assert context.ux_page.trigger_empty_target_id_error(), (
        "Expected role='alert' target ID validation error"
    )


@then("an inline target ID validation alert is displayed")
def step_verify_target_id_alert(context) -> None:
    assert context.ux_page.is_visible(*context.ux_page.TARGET_ID_ERROR), (
        "Expected inline target ID validation error to be visible"
    )


@when('I change the leaderboard page size to {size:d} and filter the leaderboard by "{query}"')
def step_change_page_size_and_filter(context, size: int, query: str) -> None:
    context.ux_page.change_page_size(size)
    context.ux_page.filter_leaderboard_and_wait_for_url_sync(query)


@then('the URL search parameters include tab "{tab}", pageSize "{page_size}", and query "{query}"')
def step_verify_url_search_params(context, tab: str, page_size: str, query: str) -> None:
    assert context.ux_page.get_url_search_param("tab") == tab
    assert context.ux_page.get_url_search_param("pageSize") == page_size
    assert context.ux_page.get_url_search_param("q") == query


@when("I reload the browser page")
def step_reload_browser_page(context) -> None:
    context.ux_page.reload_page()


@then('the URL search parameters still include tab "{tab}", pageSize "{page_size}", and query "{query}"')
def step_verify_url_search_params_after_reload(context, tab: str, page_size: str, query: str) -> None:
    assert context.ux_page.get_url_search_param("tab") == tab
    assert context.ux_page.get_url_search_param("pageSize") == page_size
    assert context.ux_page.get_url_search_param("q") == query


@when('I filter the leaderboard by "{query}" and click Clear Filters')
def step_filter_empty_and_clear(context, query: str) -> None:
    context.ux_page.filter_leaderboard_and_wait_for_url_sync(query)
    context.ux_page.wait_until(
        lambda d: context.ux_page.is_visible(*context.ux_page.LEADERBOARD_EMPTY_FILTER),
        message="Empty filter state did not render",
    )
    context.ux_page.click_locator(*context.ux_page.LEADERBOARD_CLEAR_FILTERS)


@then('the leaderboard displays both "{bot_a}" and "{bot_b}"')
def step_verify_both_bots_displayed(context, bot_a: str, bot_b: str) -> None:
    entries = context.tournament_page.get_leaderboard_entries()
    rendered = " ".join(e["name"] for e in entries)
    assert bot_a in rendered and bot_b in rendered, (
        f"Expected {bot_a} and {bot_b} in leaderboard, got {rendered}"
    )


@when("I open the Reset Stats confirmation prompt")
def step_open_reset_prompt(context) -> None:
    context.tournament_page.open_reset_stats_confirmation()


@then("an accessible alertdialog modal is displayed")
def step_verify_alert_dialog_modal(context) -> None:
    assert context.ux_page.is_alert_dialog_open(), (
        "Expected accessible modal with role='alertdialog' and aria-modal='true'"
    )


@when("I confirm resetting all stats and click Undo Reset in the toast notification")
def step_confirm_reset_and_undo(context) -> None:
    context.tournament_page.confirm_reset_stats()
    context.ux_page.click_toast_undo_and_wait_for_restore()


@then("the page has zero horizontal overflow at desktop 1440x900, tablet 768x1024, and mobile 390x844 viewports")
def step_verify_zero_overflow_across_viewports(context) -> None:
    for width, height in ((1440, 900), (768, 1024), (390, 844)):
        context.ux_page.set_viewport(width, height)
        assert context.ux_page.has_zero_horizontal_overflow(), (
            f"Detected horizontal overflow at viewport {width}x{height}"
        )
    context.ux_page.set_viewport(1440, 900)


@when("I emulate a mobile 390x844 viewport and switch to the Tournament tab using the off-canvas navigation drawer")
def step_mobile_drawer_navigation(context) -> None:
    context.ux_page.set_viewport(390, 844)
    context.ux_page.open_and_close_mobile_drawer()


@then('the off-canvas navigation drawer auto-closes and the URL tab parameter is "{expected_tab}"')
def step_verify_drawer_closed_and_tab(context, expected_tab: str) -> None:
    assert not context.ux_page.is_visible(*context.ux_page.OFFCANVAS_DRAWER)
    assert context.ux_page.get_url_search_param("tab") == expected_tab
    context.ux_page.set_viewport(1440, 900)
