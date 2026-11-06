# game_sim_docs

Comprehensive architecture documentation and Behavior-Driven Development (BDD) end-to-end (E2E) test suite for the **Argiei Platform** and **GameSimulationPlatform** (`lumenconsultancyae/GameSimulationPlatform`).

---

## Repository Structure

```text
game_sim_docs/
├── README.md                                  # Repository overview & quick-start guide
├── docs/
│   ├── argiei_and_platform_architecture.md    # Argiei Platform & GameSimulationPlatform architecture
│   └── bdd_and_unit_testing_guide.md          # 3-layer BDD E2E & unit testing separation guide
└── tests/
    └── bdd/                                   # 3-layer Behave + Selenium BDD E2E test suite
        ├── config.py                          # Environment URLs, timeouts & viewport dimensions
        ├── pages/                             # Layer 2: Page Object Models (WebDriverWait-backed)
        │   ├── base_page.py                   # Atomic interaction helpers & DOM anomaly detection
        │   ├── arena_selection_page.py        # Landing catalog & arena switcher
        │   ├── live_simulation_page.py        # Bot configuration drawer & playback controls
        │   └── tournament_page.py             # Participating bot pills, leaderboard & 2-step reset
        └── features/                          # Layer 1 & 3: Gherkin features, hooks & step definitions
            ├── environment.py                 # Pre-flight readiness, SEVERE console checks & teardown
            ├── arena_navigation.feature       # Landing page discovery & arena switching scenarios
            ├── live_simulation.feature        # Bot drawer & live simulation playback scenarios
            ├── tournament_management.feature  # Tournament execution, leaderboard & reset scenarios
            └── steps/
                ├── arena_navigation_steps.py
                ├── live_simulation_steps.py
                └── tournament_steps.py
```

---

## Documentation Index

- **[Argiei & GameSimulationPlatform Architecture](docs/argiei_and_platform_architecture.md)**
  - Argiei Platform API & MCP tools (`argiei-platform`), project/workspace management, repository scaffolding, and Kanban lifecycle.
  - `GameSimulationPlatform` layered architecture: FastAPI backend (`src/ui/`), CodinGame REST API v1 client (`src/ui/codingame_client.py`), single-file/dual-seat bot bundler (`src/ui/bot_bundler.py`), multiprocessing worker pool, Swiss matchmaking & Elo/Dominance engine, React + Vite UI (`ui/`), and all 5 registered arena game engines (`exotec`, `ghost_in_the_cell`, `troll_farm`, `back_track_king`, `tryangle_catch` with bots `bot_v1`–`bot_v29`).
- **[BDD E2E & Unit Testing Guide](docs/bdd_and_unit_testing_guide.md)**
  - Strict separation of concerns between browser-level BDD E2E journeys (`game_sim_docs/tests/bdd/`) and in-process unit tests (`GameSimulationPlatform/tests/`).
  - Step-by-step instructions for running both suites locally or in Docker (`docker compose up -d`).

---

## Running the BDD E2E Test Suite

Ensure the `GameSimulationPlatform` stack is running (via `docker compose up -d` on `:8002`/`:5174` or local dev servers on `:8000`/`:5173`), then execute:

```bash
E2E_WEB_BASE_URL=http://127.0.0.1:5174 \
E2E_API_BASE_URL=http://127.0.0.1:8002 \
E2E_HEADLESS=true \
behave tests/bdd/features --no-capture
```
