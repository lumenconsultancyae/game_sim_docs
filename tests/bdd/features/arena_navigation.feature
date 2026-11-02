@e2e @arena_selection @api_parity
Feature: Arena Discovery and Navigation
  As a bot developer using the Game Simulation Platform
  I want to browse all supported strategy arenas on the landing page and switch between them
  So that I can inspect simulations and tournaments across every registered game

  Scenario: View available strategy arenas on the landing page with UI-to-API parity
    Given I open the platform landing page
    Then the landing page displays the title "Game Simulation Platform" and badge "COMMAND & CONTROL"
    And all registered arenas from the backend API are displayed as unique cards without DOM anomalies

  Scenario: Enter an arena from the landing page and switch arenas via the header dropdown
    Given I open the platform landing page
    When I enter the "Exotec" arena from the landing page
    Then the active arena header displays "Exotec" and the URL hash is "exotec"
    When I switch to the "Troll Farm" arena using the header arena dropdown
    Then the active arena header displays "Troll Farm" and the URL hash is "troll_farm"
    When I click the Games home breadcrumb
    Then the landing page displays the title "Game Simulation Platform" and badge "COMMAND & CONTROL"
