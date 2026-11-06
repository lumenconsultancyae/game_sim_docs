@e2e @ux_redesign
Feature: Modern UX Architecture, URL State Sync, Inline Validation, and Responsive Navigation
  As a competitive programming engineer using the Game Simulation Platform
  I want bookmarkable URL state, inline form validation, accessible modals with undo toasts, and responsive navigation
  So that every workflow is fast, accessible, and free of native browser dialogs or horizontal overflow

  Scenario: Validate inline seed errors in Live View and progressive disclosure in CodinGame API
    Given I navigate to the "exotec" arena in Live View
    When I enter an invalid simulation seed "bad@#$!" and submit the live simulation form
    Then an inline seed validation alert is displayed with aria-invalid enabled
    When I correct the simulation seed to "42"
    Then the inline seed validation alert clears immediately
    When I switch to the CodinGame API tab
    Then the bot deployment form is collapsed by default behind the progressive disclosure button
    When I expand the bot deployment form and submit with an empty target ID
    Then an inline target ID validation alert is displayed

  Scenario: Synchronize tournament table search and pagination with URL parameters and undo reset via toast
    Given I navigate to the "exotec" arena and open the Tournament tab
    And I select bots "v1" and "v2" for tournament participation
    When I start and stop the tournament once the leaderboard populates
    And I change the leaderboard page size to 25 and filter the leaderboard by "v1"
    Then the URL search parameters include tab "tournament", pageSize "25", and query "v1"
    When I reload the browser page
    Then the URL search parameters still include tab "tournament", pageSize "25", and query "v1"
    When I filter the leaderboard by "nonexistent_bot_999" and click Clear Filters
    Then the leaderboard displays both "v1" and "v2"
    When I open the Reset Stats confirmation prompt
    Then an accessible alertdialog modal is displayed
    When I confirm resetting all stats and click Undo Reset in the toast notification
    Then the Tournament Leaderboard still displays "v1" and "v2"

  Scenario: Verify responsive off-canvas navigation drawer and zero horizontal overflow across viewports
    Given I navigate to the "exotec" arena in Live View
    Then the page has zero horizontal overflow at desktop 1440x900, tablet 768x1024, and mobile 390x844 viewports
    When I emulate a mobile 390x844 viewport and switch to the Tournament tab using the off-canvas navigation drawer
    Then the off-canvas navigation drawer auto-closes and the URL tab parameter is "tournament"
