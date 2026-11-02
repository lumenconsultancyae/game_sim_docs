@e2e @live_simulation @api_parity
Feature: Live Bot Simulation and Baseline Match Replay
  As a competitive programming developer
  I want to run deterministic head-to-head bot simulations and replay official baseline logs in Live View
  So that I can visually inspect turn-by-turn state transitions, scores, and execution telemetry

  Scenario: Configure Bot A and Bot B with a deterministic seed and run a live match
    Given I navigate to the "exotec" arena in Live View
    When I select bot "v1" for slot "A" and bot "v2" for slot "B" from the bot drawer
    And I enter the simulation seed "12345" and start the live simulation
    Then the viewport canvas renders the match and playback loads multiple turns
    And I can step through turns and expand the execution logs without DOM anomalies

  Scenario: Replay an official baseline match log and navigate turn history
    Given I navigate to the "ghost_in_the_cell" arena in Live View
    When I select the first available baseline match file and start the live simulation
    Then the viewport canvas renders the match and playback loads multiple turns
    When I jump to the final turn of the match replay
    Then the playback turn counter is positioned at the final turn
