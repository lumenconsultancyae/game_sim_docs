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
  - `GameSimulationPlatform` layered architecture: FastAPI backend (`src/ui/`), multiprocessing worker pool, Swiss matchmaking & Elo/Dominance engine, React + Vite UI (`src/ui/web/`), and arena game engines (`exotec`, `back_track_king`, `fall_challenge_2020`, ` winter_challenge_2026_exotec`).
- **[BDD E2E & Unit Testing Guide](docs/bdd_and_unit_testing_guide.md)**
  - Strict separation of concerns between browser-level BDD E2E journeys (`game_sim_docs/tests/bdd/`) and in-process unit tests (`GameSimulationPlatform/tests/`).
  - Step-by-step instructions for running both suites locally or in Docker.

---

## Running the BDD E2E Test Suite

Ensure the `GameSimulationPlatform` backend (`http://localhost:8000`) and frontend (`http://localhost:5173`) are running, then execute:

```bash
GSP_WEB_URL=http://localhost:5173 \
GSP_API_URL=http://localhost:8000 \
GSP_HEADLESS=true \
behave tests/bdd/features --no-capture
```
