# BDD E2E & Unit Testing Guide

This document defines the testing architecture across `game_sim_docs` (browser-based BDD E2E tests) and `GameSimulationPlatform` (in-process unit tests), ensuring comprehensive coverage with zero redundant overlap.

---

## 1. Division of Test Ownership

| Test Suite | Location | Runner | Responsibility & Use Cases Covered |
| :--- | :--- | :--- | :--- |
| **BDD E2E Tests** | `game_sim_docs/tests/bdd/` | `behave` + Selenium Headless Chromium | **User-visible browser workflows (`4` features, `10` scenarios, `64` steps)**: SPA routing (`#/` $\leftrightarrow$ `#/<game_id>`), URL search-param synchronization (`?tab=`, `?q=`, `?pageSize=`), game switcher dropdowns, bot configuration drawer selection, live match simulation & timeline stepping, tournament execution, paginated leaderboard filtering & `Clear Filters`, accessible `role="alertdialog"` reset confirmation modal, non-blocking toast notification with `Undo Reset`, progressive disclosure & inline `role="alert"` form validation in CodinGame API view, `Cmd/Ctrl + K` command palette, responsive off-canvas navigation drawer (`1440px`, `768px`, `390px`), zero horizontal overflow, DOM text integrity (`NaN`/`undefined` checks), and zero `SEVERE` browser console errors. |
| **Frontend Unit & Architectural Gate Tests** | `GameSimulationPlatform/ui/src/` | `vitest` + React Testing Library | **Frontend components, hooks, schemas & static gates (`6` suites, `28` tests)**: `ToastProvider` (with Undo & XSS sanitization), `ConfirmModal` (`role="alertdialog"`), `PaginationBar`, `OffCanvasNavDrawer`, `CommandPalette`, `ErrorBoundary`, Zod schemas (`codingameTokenSchema`, `codingameDeploySchema`, `simulationFormSchema`), TanStack Query key factory & optimistic rollback, URL search-param sync, static check for `0` `alert`/`confirm`/`prompt` calls, `0` hardcoded hex colors in `.tsx`, all `var(--...)` custom properties defined in `tokens.css`, and `< 500` lines per file across `ui/src/`. |
| **Backend In-Process Unit Tests** | `GameSimulationPlatform/tests/` | `pytest` | **Algorithmic, validation & edge-case matrices (`615` tests)**: FastAPI route `400`/`404` error guardrails, corrupted `.e2e` replay rejection, bot class alias deduplication, `PrioritySemaphore` preemption & cancellation cleanup, `TournamentManager` win/loss/draw reason matrices, largest-remainder `100%` sub-percentage distribution (`distribute_sub_pcts`), Elo/Dominance calculations, Swiss pairing bye/rematch penalties, and bot pathfinding (`A*`, heatmaps, centrality). |

---

## 2. 3-Layer BDD Architecture (`tests/bdd/`)

The BDD test suite strictly enforces a 3-layer separation:

### Layer 1: Declarative Gherkin Features (`tests/bdd/features/*.feature`)
Scenarios are written in business-level domain language without CSS selectors, XPaths, URLs, or sleep timers:
1. **`arena_navigation.feature`**:
   - *Display available game arenas on the landing page*
   - *Enter an arena from the landing page and switch between arenas and views*
2. **`live_simulation.feature`**:
   - *Configure Bot A and Bot B with a deterministic seed and run a live match*
   - *Replay an official baseline match log and navigate turn history*
   - *Configure BotV29 and BotV28 in TryAngle-Catch and run a deterministic live match*
3. **`tournament_management.feature`**:
   - *Configure participating bots in the Tournament dashboard using selection controls*
   - *Inspect tournament standings and execute the Reset Stats confirmation flow*
4. **`ux_redesign.feature`**:
   - *Validate inline seed errors in Live View and progressive disclosure in CodinGame API*
   - *Synchronize tournament table search and pagination with URL parameters and undo reset via toast*
   - *Verify responsive off-canvas navigation drawer and zero horizontal overflow across viewports*

### Layer 2: Page Object Model (`tests/bdd/pages/`)
All DOM locators and explicit `WebDriverWait` synchronization live inside Page Objects inheriting from `BasePage`:
- **`BasePage` (`tests/bdd/pages/base_page.py`)**:
  - Retry-aware explicit waits (`find_visible`, `find_clickable`, `click`, `wait_for_url_contains`).
  - `get_dom_anomalies()`: Scans `document.body.innerText` for rendering defects (`NaN`, `undefined`, `[object Object]`).
  - Idempotent teardown helpers (`stop_and_reset_tournament_via_api`) for clean scenario isolation.
- **`ArenaSelectionPage` (`tests/bdd/pages/arena_selection_page.py`)**: Landing page game cards, arena header breadcrumb, game dropdown switcher, and `Live View` / `Tournament` mode toggles.
- **`LiveSimulationPage` (`tests/bdd/pages/live_simulation_page.py`)**: Bot Configuration Drawer (`Configure Bots`), bot card toggles, `Run Simulation` button, playback controls, turn counter (`Turn X / Y`), and viewport canvas dimension verification.
- **`TournamentPage` (`tests/bdd/pages/tournament_page.py`)**: Participating bot pills (`v1`, `v2`, ...), `Select All` / `Reset` selection actions, `Run Tournament` / `Stop Tournament`, leaderboard table rows, and the 2-step `Reset Stats` $\rightarrow$ `Yes, Reset` / `Cancel` confirmation flow.

### Layer 3: Step Definitions & Fail-Fast Lifecycle Hooks (`tests/bdd/features/`)
- **`environment.py`**:
  - `before_all`: Verifies backend (`GET /`) and frontend HTTP readiness before launching headless Chromium (`1440x900`).
  - `after_step`: Reads `driver.get_log("browser")` after every single Gherkin step and fails immediately if any `SEVERE` console error (such as React duplicate key warnings or unhandled runtime exceptions) occurs.
  - `after_scenario`: Stops any running tournament and resets tournament statistics so every scenario starts from a clean state.

---

## 3. Running the Test Suites

### 3.1 Running BDD E2E Tests (`game_sim_docs`)
With the `GameSimulationPlatform` API (`:8002` or `:8000`) and Web UI (`:5174` or `:5173`) running via `docker compose up -d`:

```bash
cd game_sim_docs
E2E_WEB_BASE_URL=http://127.0.0.1:5174 \
E2E_API_BASE_URL=http://127.0.0.1:8002 \
E2E_HEADLESS=true \
behave tests/bdd/features --no-capture
```

### 3.2 Running In-Process Unit & Integration Tests (`GameSimulationPlatform`)
```bash
cd GameSimulationPlatform
pytest -v tests/
```
