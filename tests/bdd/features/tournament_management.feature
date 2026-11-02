@e2e @tournament @api_parity
Feature: Tournament Bot Selection, Live Standings, and Reset Workflow
  As a bot developer benchmarking multiple bot versions
  I want to configure participating bots, inspect tournament standings and matrices, and reset statistics
  So that I can evaluate bot Elo ratings and cleanly restart tournament cycles

  Scenario: Configure participating bots in the Tournament dashboard using selection controls
    Given I navigate to the "exotec" arena and open the Tournament tab
    When I click Select All in the Participating Bots panel
    Then the participating bots count matches the total bots returned by the backend API for "exotec"
    When I click Reset in the Participating Bots panel and toggle bot chip "v2"
    Then exactly 2 participating bot chips are selected

  Scenario: Inspect tournament standings and execute the Reset Stats confirmation flow
    Given I navigate to the "exotec" arena and open the Tournament tab
    And I select bots "v1" and "v2" for tournament participation
    When I start and stop the tournament once the leaderboard populates
    Then the Tournament Leaderboard and Head-to-Head Matrix display "v1" and "v2" with league badges
    When I open the Reset Stats confirmation prompt and cancel it
    Then the Tournament Leaderboard still displays "v1" and "v2"
    When I open the Reset Stats confirmation prompt and confirm resetting all stats
    Then the Tournament Leaderboard returns to the waiting state and the backend stats for "exotec" are empty
