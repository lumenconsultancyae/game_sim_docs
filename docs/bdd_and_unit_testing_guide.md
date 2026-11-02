# BDD E2E & Unit Testing Guide

This document defines the testing architecture across `game_sim_docs` (browser-based BDD E2E tests) and `GameSimulationPlatform` (in-process unit tests), ensuring comprehensive coverage with zero redundant overlap.

---

## 1. Division of Test Ownership

| Test Suite | Location | Runner | Responsibility & Use Cases Covered |
| :--- | :--- | :--- | :--- |
| **BDD E2E Tests** | `game_sim_docs/tests/bdd/` | `behave` + Selenium Headless Chromium | **User-visible browser workflows**: SPA hash routing (`#/` $\leftrightarrow$ `#/<game_id>`), game switcher dropdowns, bot configuration drawer selection, live match simulation & timeline stepping, tournament execution, leaderboard population, 2-step reset confirmation, DOM text integrity (`NaN`/`undefined` checks), and zero `SEVERE` browser console errors. |
| **In-Process Unit Tests** | `GameSimulationPlatform/tests/` | `pytest` | **Algorithmic, validation & edge-case matrices**: FastAPI route `400`/`404` error guardrails, corrupted `.e2e` replay rejection, bot class alias deduplication, `PrioritySemaphore` preemption & cancellation cleanup, `TournamentManager` win/loss/draw reason matrices, largest-remainder `100%` sub-percentage distribution (`distribute_sub_pcts`), Elo/Dominance calculations, Swiss pairing bye/rematch penalties, and bot pathfinding (`A*`, heatmaps, centrality). |

---

## 2. 3-Layer BDD Architecture (`tests/bdd/`)

The BDD test suite strictly enforces a 3-layer separation:

### Layer 1: Declarative Gherkin Features (`tests/bdd/features/*.feature`)
Scenarios are written in business-level domain language without CSS selectors, XPaths, URLs, or sleep timers:
1. **`arena_navigation.feature`**:
   - *Display available game arenas on the landing page*
   - *Enter an arena from the landing page and switch between arenas and views*
2. **`live_simulation.feature`**:
   - *Configure participating bots in the Bot Configuration Drawer*
   - *Run a live simulation between two bots and step through frames*
3. **`tournament_management.feature`**:
   - *Select bots, run a tournament, and inspect populated leaderboard metrics*
   - *Cancel and confirm resetting tournament statistics*

### Layer 2: Page Object Model (`tests/bdd/pages/`)
All DOM locators and explicit `WebDriverWait` synchronization live inside Page Objects inheriting from `BasePage`:
- **`BasePage` (`tests/bdd/pages/base_page.py`)**:
  - Retry-aware explicit waits (`find_visible`, `find_clickable`, `click`, `wait_for_url_contains`).
  - `assert_no_dom_text_anomalies()`: Scans `document.body.innerText` for rendering defects (`NaN`, `undefined`, `[object Object]`).
  - Idempotent teardown helpers (`stop_and_reset_tournament_via_api`) for clean scenario isolation.
- **`ArenaSelectionPage` (`tests/bdd/pages/arena_selection_page.py`)**: Landing page game cards, arena header breadcrumb, game dropdown switcher, and `Live View` / `Tournament` mode toggles.
- **`LiveSimulationPage` (`tests/bdd/pages/live_simulation_page.py`)**: Bot Configuration Drawer (`Configure Bots`), bot card toggles, `Run Simulation` button, playback controls, frame counter (`Frame X / Y`), and viewport canvas dimension verification.
- **`TournamentPage` (`tests/bdd/pages/tournament_page.py`)**: Participating bot pills (`v1`, `v2`, ...), `Select All` / `Reset` selection actions, `Run Tournament` / `Stop Tournament`, leaderboard table rows, and the 2-step `Reset Stats` $\rightarrow$ `Yes, Reset` / `Cancel` confirmation flow.

### Layer 3: Step Definitions & Fail-Fast Lifecycle Hooks (`tests/bdd/features/`)
- **`environment.py`**:
  - `before_all`: Verifies backend (`GET /`) and frontend HTTP readiness before launching headless Chromium (`1440x900`).
  - `after_step`: Reads `driver.get_log("browser")` after every single Gherkin step and fails immediately if any `SEVERE` console error (such as React duplicate key warnings or unhandled runtime exceptions) occurs.
  - `after_scenario`: Stops any running tournament and resets tournament statistics so every scenario starts from a clean state.

---

## 3. Running the Test Suites

### 3.1 Running BDD E2E Tests (`game_sim_docs`)
With the `GameSimulationPlatform` API (`:8000`) and Web UI (`:5173`) running:

```bash
cd /workspace/projects/codingame_competition_c186e7/default/game_sim_docs
GSP_WEB_URL=http://localhost:5173 \
GSP_API_URL=http://localhost:8000 \
GSP_HEADLESS=true \
behave tests/bdd/features --no-capture
```

### 3.2 Running In-Process Unit Tests (`GameSimulationPlatform`)
```bash
cd /workspace/projects/codingame_competition_c186e7/default/GameSimulationPlatform
pytest -v tests/test_*.py tests/utils/test_*.py
```
