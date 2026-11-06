# UX/UI Redesign, Interaction Overhaul & Modern Frontend Architecture Report

## 1. Executive Summary

This report documents the comprehensive UX/UI redesign, interaction overhaul, and modern React frontend architectural upgrade of the **Game Simulation Platform** (`GameSimulationPlatform/ui`). Every primary route, view, modal, form, data table, and responsive navigation flow was audited across **Desktop (`1440x900`)**, **Tablet (`768x1024`)**, and **Mobile (`390x844`)** viewports before and after the redesign.

### Key Architectural & UX Upgrades

| Dimension | Baseline ("Before") State | Upgraded ("After") State |
| :--- | :--- | :--- |
| **Routing & URL State Synchronization** | Ad-hoc `window.location.hash` listener; active tab (`live` / `tournament` / `codingame`), leaderboard search query, sort column/direction, and pagination were trapped in ephemeral component state and lost on browser reload. | Declarative **React Router (`react-router-dom`)** integration with `<BrowserRouter>` and `useSearchParams` synchronizing `?tab=`, `?q=`, `?page=`, `?pageSize=`, `?sort=`, and `?dir=` alongside `#<game_id>` deep-linking and `React.lazy` + `<Suspense>` route-level code splitting. |
| **Server vs. Client State (`TanStack Query`)** | Raw `useEffect` + `fetch()` chains across `App.tsx`, `GameSelection.tsx`, and `CodinGamePanel.tsx` with duplicated server cache in `useState` and zero request deduplication or optimistic rollback. | Centralized **Query Key Factory** (`platformKeys` in `src/api/queryKeys.ts`), typed query/mutation hooks (`src/api/queries.ts`), hover prefetching (`queryClient.prefetchQuery`), and **optimistic tournament reset** (`useResetTournamentMutation`) with instant cache snapshot rollback on error or user **Undo**. |
| **Resilient Async Lifecycle** | Blank containers or layout shift during initial fetch; uncaught render errors could crash the entire workspace; single generic empty text on filtered tables. | Layout-stable `<Skeleton />` loaders (`src/components/ui/Skeleton.tsx`), per-route `<ErrorBoundary />` (`src/components/ui/ErrorBoundary.tsx`) wired to TanStack Query retry, and contextual empty states distinguishing *"no tournament matches run yet"* (`+ Run Tournament` CTA) from *"no bots match active filter"* (`Clear Filters` button). |
| **Visual Identity, Semantic Tokens & Logical CSS** | Over 100 hardcoded hex literals (`#ff4b4b`, `#10b981`, `#fbbf24`, `#38bdf8`, `#0f172a`, `#ef4444`) scattered across `.tsx` files; `index.css` was a monolithic 1,039-line stylesheet; physical directional properties (`margin-left`, `text-align: left`) broke RTL layouts. | Unified semantic design token system (`src/styles/tokens.css`) and modular stylesheets (`layout.css`, `components.css`, `views.css`, `responsive.css`); **zero hardcoded hex values in `.tsx` components**; `font-variant-numeric: tabular-nums` on all numeric/KPI/rating columns; CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `text-align: start`) for automatic LTR/RTL mirroring; `<kbd className="kbd-hint">` keycap badges; `@media print` stylesheet. |
| **Zero Native Dialogs & Accessible UI Primitives** | Unstyled inline confirmation bar and raw error banners without focus management or WAI-ARIA dialog semantics; no Undo path after resetting tournament statistics. | **Zero `window.alert` / `window.confirm` / `window.prompt` calls** enforced by static unit gate; non-blocking **Toast Notification Queue** (`ToastProvider.tsx`, `role="status"`, `aria-live="polite"`) with **Undo Reset** callback; **Accessible Confirmation Modal** (`ConfirmModal.tsx` built on `@radix-ui/react-dialog`, `role="alertdialog"`, `aria-modal="true"`) with contextual summary, focus trapping, `Enter` to confirm, and `Escape`/backdrop dismissal. |
| **Schema-First Inline Form Validation** | `CodinGamePanel` submitted forms without field-level validation, allowing empty session tokens or empty target arena IDs to hit the API or fail silently. | Shared **Zod** schemas (`src/schemas/validation.ts`) wired to **React Hook Form** (`react-hook-form` + `@hookform/resolvers/zod`) in `CodinGamePanel.tsx` and `CodinGameDeployForm.tsx`, rendering inline field errors (`role="alert"`, `aria-invalid="true"`, `aria-describedby`) beneath invalid inputs, auto-focusing the first invalid control, and clearing errors immediately on input. |
| **Table Pagination, Progressive Disclosure & Navigation** | Leaderboard and battle tables rendered all rows unbounded; multi-field CodinGame deployment form was permanently expanded above telemetry cards; navigation controls crowded smaller viewports without an off-canvas drawer or command palette. | Reusable `<PaginationBar />` (`10` / `25` / `50` / `100` rows, `"Showing X–Y of Z"`, Prev/Next) with sticky table headers and debounced search; CodinGame deployment form collapsed by default behind `+ Deploy / Configure Bot` progressive disclosure button; global `Cmd/Ctrl + K` `<CommandPalette />`; responsive `<OffCanvasNavDrawer />` (`<= 1024px`) with auto-close on route change and zero horizontal overflow across `1440px`, `768px`, and `390px`. |
| **Modular File Size Gate (`< 500` LOC) & XSS Safety** | `CodinGamePanel.tsx` (795 lines), `App.tsx` (688 lines), `Viewport.tsx` (681 lines), and `index.css` (1,039 lines) violated the 500-line modularity boundary. | Every TypeScript, React, and CSS module in `ui/src/` is strictly **under 480 lines**; centralized `sanitizeText()` / `sanitizeIdentifier()` utilities in `src/utils/sanitize.ts` with zero `dangerouslySetInnerHTML` or `innerHTML` usage. |

---

## 2. Frontend Architecture & State Management Diagrams

### 2.1 Declarative React Router & URL Search-Parameter Synchronization

```mermaid
flowchart LR
  subgraph sg_url ["Browser URL State (Bookmarkable & Deep-Linkable)"]
    U1["Hash Arena ID (#exotec, #tryangle_catch)"]
    U2["Workspace Tab (?tab=live | tournament | codingame)"]
    U3["Table Query & Sort (?q=v1&sort=mu&dir=desc)"]
    U4["Pagination State (?page=1&pageSize=25)"]
  end

  subgraph sg_router ["React Router & Navigation Primitives"]
    R1["BrowserRouter + AppShell (App.tsx)"]
    R2["WorkspaceHeader & Breadcrumb Selector"]
    R3["OffCanvasNavDrawer (Tablet & Mobile <= 1024px)"]
    R4["CommandPalette (Global Cmd/Ctrl + K)"]
  end

  subgraph sg_views ["Lazy-Loaded Route Views & Synchronized Tables"]
    V1["GameSelection Catalog"]
    V2["LiveSimulationView"]
    V3["TournamentDashboardView + Leaderboard"]
    V4["CodinGamePanel (React.lazy + Suspense)"]
  end

  U1 <--> R1
  U2 <--> R1
  U3 <--> V3
  U4 <--> V3
  R2 --> R1
  R3 --> R1
  R4 --> R1
  R1 --> V1
  R1 --> V2
  R1 --> V3
  R1 --> V4
```

### 2.2 TanStack Query Cache, Query Key Factory & Optimistic Mutation Flow

```mermaid
sequenceDiagram
  participant User as User / Browser UI
  participant Comp as TournamentDashboardView
  participant Stream as useTournamentStream + ToastProvider
  participant QC as TanStack Query Cache (platformKeys)
  participant API as FastAPI Backend (/api)

  User->>Comp: Click "Reset Stats" button
  Comp->>User: Open ConfirmModal (role="alertdialog", aria-modal="true")
  User->>Comp: Confirm "Yes, Reset" (or press Enter)
  Comp->>Stream: Invoke resetTournament() / useResetTournamentMutation
  Stream->>QC: Snapshot previous Leaderboard, H2H, and Participating Bots
  Stream->>QC: Optimistically clear Leaderboard & H2H state to empty
  Stream->>API: POST /api/reset-tournament?game_id=exotec
  API-->>Stream: 200 OK {"status": "success"}
  Stream->>User: Render Toast (role="status") with "Undo Reset" action button
  alt User clicks "Undo Reset" within Toast
    User->>Stream: Click "Undo Reset"
    Stream->>QC: Restore captured Leaderboard, H2H & Participating Bots snapshot
    Stream->>User: Dismiss Toast & render restored Leaderboard rows immediately
  else API Mutation Error
    API-->>Stream: 500 / Network Error
    Stream->>QC: Roll back cache to previous snapshot automatically
    Stream->>User: Render Error Toast notification
  end
```

### 2.3 Modular Component & Stylesheet Hierarchy (`< 500` Lines Per File)

```mermaid
flowchart TD
  subgraph sg_entry ["Application Entry & Providers"]
    M1["main.tsx (QueryClientProvider + BrowserRouter + ToastProvider)"]
    M2["App.tsx (Workspace Shell & ErrorBoundary)"]
  end

  subgraph sg_data ["Data Layer, Schemas & Utilities"]
    D1["api/queryKeys.ts (platformKeys Factory)"]
    D2["api/queries.ts (useRootCatalogQuery, useResetTournamentMutation)"]
    D3["schemas/validation.ts (Zod Validation Schemas)"]
    D4["utils/sanitize.ts (XSS Sanitization)"]
  end

  subgraph sg_ui ["Accessible Headless UI Primitives (components/ui/)"]
    P1["ToastProvider.tsx (Stacked Toasts + Undo)"]
    P2["ConfirmModal.tsx (Radix AlertDialog)"]
    P3["CommandPalette.tsx (Cmd/Ctrl+K Quick Jump)"]
    P4["OffCanvasNavDrawer.tsx (Responsive Slide-Over)"]
    P5["PaginationBar.tsx (Bounded Table Pagination)"]
    P6["Skeleton.tsx & ErrorBoundary.tsx"]
  end

  subgraph sg_domain ["Domain Views & Sub-Modules"]
    V1["GameSelection.tsx (Catalog Search & Skeleton)"]
    V2["live/LiveSimulationView.tsx + Viewport.tsx + viewport/ArenaRenderers.tsx"]
    V3["tournament/TournamentDashboardView.tsx + Leaderboard.tsx + WinRateMatrix.tsx"]
    V4["CodinGamePanel.tsx + codingame/CodinGameDeployForm.tsx + CodinGameTelemetryGrid.tsx"]
  end

  M1 --> M2
  M2 --> D1
  M2 --> D2
  M2 --> P1
  M2 --> P2
  M2 --> P3
  M2 --> P4
  M2 --> P6
  M2 --> V1
  M2 --> V2
  M2 --> V3
  M2 --> V4
  V3 --> P5
  V4 --> D3
  V4 --> P5
  V1 --> D4
```

---

## 3. Side-by-Side Before & After Visual Comparison (`22` Paired Captures)

Every screenshot pair below was captured in Headless Chromium across **Desktop (`1440x900`)**, **Tablet (`768x1024`)**, and **Mobile (`390x844`)** viewports.

### 3.1 Landing Page & Arena Discovery Catalog (`01` – `03`)

| # | Viewport & State | Before (`docs/screenshots/ux_improvements/before/`) | After (`docs/screenshots/ux_improvements/after/`) | UX & Architectural Improvements |
| :-: | :--- | :--- | :--- | :--- |
| **01** | **Landing Catalog — Desktop (`1440x900`)** | ![Before Landing Desktop](screenshots/ux_improvements/before/01_landing_desktop.png) | ![After Landing Desktop](screenshots/ux_improvements/after/01_landing_desktop.png) | **Before**: Fetched `/api/games` via raw `useEffect` + `fetch()` without caching, skeleton states, or search filtering; hardcoded hex colors on arena icons. **After**: Powered by `useRootCatalogQuery()` (`TanStack Query`), semantic CSS custom properties (`--color-accent-*`), instant client-side arena search bar (`[data-testid="catalog-search-input"]`), and `<Skeleton />` loading cards. |
| **02** | **Landing Catalog — Tablet (`768x1024`)** | ![Before Landing Tablet](screenshots/ux_improvements/before/02_landing_tablet.png) | ![After Landing Tablet](screenshots/ux_improvements/after/02_landing_tablet.png) | **Before**: Fixed padding and card dimensions left uneven vertical rhythm on `768x1024` portrait tablets. **After**: Fluid CSS Grid (`repeat(auto-fit, minmax(280px, 1fr))`) with balanced card spacing, search filter input, and consistent button hierarchy. |
| **03** | **Landing Catalog — Mobile (`390x844`)** | ![Before Landing Mobile](screenshots/ux_improvements/before/03_landing_mobile.png) | ![After Landing Mobile](screenshots/ux_improvements/after/03_landing_mobile.png) | **Before**: Oversized hero typography crowded the `390px` viewport without search filtering. **After**: Responsive `clamp()` typography, compact vertical rhythm, full-width search bar, and zero horizontal overflow (`scrollWidth <= innerWidth`). |

### 3.2 Live Simulation Workspace & Bot Drawer (`04` – `08`)

| # | Viewport & State | Before (`docs/screenshots/ux_improvements/before/`) | After (`docs/screenshots/ux_improvements/after/`) | UX & Architectural Improvements |
| :-: | :--- | :--- | :--- | :--- |
| **04** | **Live Simulation View — Desktop (`1440x900`)** | ![Before Live View Desktop](screenshots/ux_improvements/before/04_live_view_desktop.png) | ![After Live View Desktop](screenshots/ux_improvements/after/04_live_view_desktop.png) | **Before**: Header lacked keyboard command palette access (`Ctrl+K`) and LTR/RTL layout toggle; simulation controls used ad-hoc inline styles. **After**: Unified `<WorkspaceHeader />` with `Ctrl+K` `<kbd className="kbd-hint">` badge, RTL toggle, semantic tokens, and decomposed `<LiveSimulationView />` + `<Viewport />` (`< 450` lines each). |
| **05** | **Live Simulation View — Tablet (`768x1024`)** | ![Before Live View Tablet](screenshots/ux_improvements/before/05_live_view_tablet.png) | ![After Live View Tablet](screenshots/ux_improvements/after/05_live_view_tablet.png) | **Before**: Desktop tab bar crowded the top header on `768px` tablet viewports with no slide-over navigation drawer. **After**: Hamburger toggle (`[data-testid="mobile-menu-toggle"]`) replaces desktop tab strip at `<= 1024px`, giving the breadcrumb, arena selector, and `Ctrl+K` trigger clean breathing room. |
| **06** | **Live Simulation View — Mobile (`390x844`)** | ![Before Live View Mobile](screenshots/ux_improvements/before/06_live_view_mobile.png) | ![After Live View Mobile](screenshots/ux_improvements/after/06_live_view_mobile.png) | **Before**: Header tabs and breadcrumb collided on `390px` mobile screens. **After**: Compact mobile header with accessible off-canvas drawer trigger, stacked simulation controls, and zero horizontal overflow. |
| **07** | **Bot Selection Drawer — Desktop (`1440x900`)** | ![Before Bot Drawer Desktop](screenshots/ux_improvements/before/07_bot_drawer_desktop.png) | ![After Bot Drawer Desktop](screenshots/ux_improvements/after/07_bot_drawer_desktop.png) | **Before**: Drawer action buttons used hardcoded inline colors and raw copy feedback without TanStack Query prefetching or toast notifications. **After**: Hovering the copy icon prefetches the bot bundle via `queryClient.prefetchQuery`, and copying triggers a non-blocking `role="status"` toast notification. |
| **08** | **Active Live Match Replay — Desktop (`1440x900`)** | ![Before Active Simulation Desktop](screenshots/ux_improvements/before/08_live_simulation_active_desktop.png) | ![After Active Simulation Desktop](screenshots/ux_improvements/after/08_live_simulation_active_desktop.png) | **Before**: `Viewport.tsx` was a 681-line file mixing canvas/SVG arena renderers with playback chrome and hardcoded hex colors. **After**: Arena renderers extracted into `src/components/viewport/ArenaRenderers.tsx` (332 lines) and `Viewport.tsx` (448 lines) with `tabular-nums` turn counters and semantic badge tokens. |

### 3.3 Tournament Dashboard, URL-Synchronized Table Pagination & Accessible Reset Modal (`09` – `13`)

| # | Viewport & State | Before (`docs/screenshots/ux_improvements/before/`) | After (`docs/screenshots/ux_improvements/after/`) | UX & Architectural Improvements |
| :-: | :--- | :--- | :--- | :--- |
| **09** | **Tournament Empty State — Desktop (`1440x900`)** | ![Before Tournament Empty Desktop](screenshots/ux_improvements/before/09_tournament_empty_desktop.png) | ![After Tournament Empty Desktop](screenshots/ux_improvements/after/09_tournament_empty_desktop.png) | **Before**: Generic `"Waiting for tournament results..."` text with no primary call-to-action button inside the empty leaderboard card; active tab was not persisted in the URL. **After**: Contextual empty state with a primary `+ Run Tournament` CTA (`[data-testid="empty-start-tournament-cta"]`) and URL synchronization (`/?tab=tournament#exotec`). |
| **10** | **Populated Tournament Leaderboard & Pagination — Desktop (`1440x900`)** | ![Before Tournament Populated Desktop](screenshots/ux_improvements/before/10_tournament_populated_desktop.png) | ![After Tournament Populated Desktop](screenshots/ux_improvements/after/10_tournament_populated_desktop.png) | **Before**: Unpaginated leaderboard table forced internal/page scrolling for large bot pools (`16+` bots), lacked a search filter, and `WinRateMatrix` column headers duplicated bot names without `vs` prefixes. **After**: Equipped with debounced search (`?q=`), URL-synced `<PaginationBar />` (`Showing 1–10 of 16 bots`, `Rows: 10 / 25 / 50 / 100`, `Prev / Page 1 / 2 / Next`), sticky `<thead>`, `tabular-nums` alignment, and distinct `vs {bot}` matrix headers. |
| **11** | **Populated Tournament View — Tablet (`768x1024`)** | ![Before Tournament Tablet](screenshots/ux_improvements/before/11_tournament_tablet.png) | ![After Tournament Tablet](screenshots/ux_improvements/after/11_tournament_tablet.png) | **Before**: 3-column header grid and split leaderboard squeezed horizontally on `768px` tablet viewports. **After**: Responsive `@media (max-width: 1024px)` breakpoints stack the progression chart and paginated leaderboard cleanly with zero horizontal page overflow. |
| **12** | **Populated Tournament View — Mobile (`390x844`)** | ![Before Tournament Mobile](screenshots/ux_improvements/before/12_tournament_mobile.png) | ![After Tournament Mobile](screenshots/ux_improvements/after/12_tournament_mobile.png) | **Before**: Header tabs and unpaginated table overflowed on `390px` mobile screens. **After**: Single-column mobile layout with bounded horizontal table scroll container, pagination bar, and off-canvas navigation drawer toggle. |
| **13** | **Destructive Reset Confirmation Modal — Desktop (`1440x900`)** | ![Before Reset Confirmation Desktop](screenshots/ux_improvements/before/13_reset_confirmation_desktop.png) | ![After Reset Confirmation Desktop](screenshots/ux_improvements/after/13_reset_confirmation_desktop.png) | **Before**: Clicking `Reset Stats` swapped the button inline for a tiny `RESET ALL? Yes / No` strip with no dialog semantics, focus trap, or impact summary. **After**: Accessible Radix UI `<ConfirmModal />` (`role="alertdialog"`, `aria-modal="true"`) centered over a blurred backdrop with contextual summary (`Arena: Exotec • 16 ranked bots • 240 simulated matches`), `Enter` to confirm, and `Escape`/backdrop click to cancel. |

### 3.4 CodinGame Arena Integration, Progressive Disclosure & Inline Form Validation (`14` – `18`)

| # | Viewport & State | Before (`docs/screenshots/ux_improvements/before/`) | After (`docs/screenshots/ux_improvements/after/`) | UX & Architectural Improvements |
| :-: | :--- | :--- | :--- | :--- |
| **14** | **CodinGame API View (Progressive Disclosure Collapsed) — Desktop (`1440x900`)** | ![Before CodinGame Desktop](screenshots/ux_improvements/before/14_codingame_desktop.png) | ![After CodinGame Desktop](screenshots/ux_improvements/after/14_codingame_desktop.png) | **Before**: Multi-field bot deployment form was permanently expanded at the top of the view, pushing telemetry cards down; `Recent Arena Battles` rendered all 50 battles in an unpaginated list. **After**: Creation/deployment form is collapsed by default behind `+ Deploy / Configure Bot` (`[data-testid="toggle-deploy-form-btn"]`), keeping `Arena Progress & Quotas` (`2/2 today`, `10/10 hr`, `Gold`, `#179`) and paginated `Recent Arena Battles` (`Showing 1–10 of 50 battles`) immediately visible above the fold. |
| **15** | **CodinGame Deployment Form Expanded — Desktop (`1440x900`)** | ![Before CodinGame Expanded Desktop](screenshots/ux_improvements/before/15_codingame_form_expanded_desktop.png) | ![After CodinGame Expanded Desktop](screenshots/ux_improvements/after/15_codingame_form_expanded_desktop.png) | **Before**: `CodinGamePanel.tsx` was a single 795-line component with raw `useState` inputs and hardcoded colors. **After**: Decomposed into `CodinGamePanel.tsx` (353 lines), `CodinGameDeployForm.tsx` (397 lines), `CodinGameTelemetryGrid.tsx` (346 lines), and `useCodinGameTelemetry.ts` (296 lines), expanding on demand with semantic tokens and accessible form labels. |
| **16** | **Inline Schema Validation Error State — Desktop (`1440x900`)** | ![Before CodinGame Validation Error Desktop](screenshots/ux_improvements/before/16_codingame_validation_error_desktop.png) | ![After CodinGame Validation Error Desktop](screenshots/ux_improvements/after/16_codingame_validation_error_desktop.png) | **Before**: Submitting with an empty `Target Public ID` disabled the button or failed without field-level feedback, `role="alert"`, or `aria-invalid="true"`. **After**: Shared `codingameDeploySchema` (`Zod` + `React Hook Form`) highlights the invalid input with a danger border (`aria-invalid="true"`), renders `Target public ID is required` (`role="alert"`) directly beneath the field, focuses the first invalid control, and clears the error immediately as the user types. |
| **17** | **CodinGame API View — Tablet (`768x1024`)** | ![Before CodinGame Tablet](screenshots/ux_improvements/before/17_codingame_tablet.png) | ![After CodinGame Tablet](screenshots/ux_improvements/after/17_codingame_tablet.png) | **Before**: Expanded forms and unpaginated battle rows required long vertical scrolling on `768x1024` tablets. **After**: Collapsed-by-default progressive disclosure and 10-row battle/leaderboard pagination keep the entire view compact on tablet screens. |
| **18** | **CodinGame API View — Mobile (`390x844`)** | ![Before CodinGame Mobile](screenshots/ux_improvements/before/18_codingame_mobile.png) | ![After CodinGame Mobile](screenshots/ux_improvements/after/18_codingame_mobile.png) | **Before**: Top navigation tabs and action buttons wrapped awkwardly on `390px` mobile viewports. **After**: Clean single-column card stack, responsive header with off-canvas menu button, and paginated battle list with zero horizontal overflow. |

### 3.5 Responsive Off-Canvas Drawer, Logical CSS RTL Mirroring & Command Palette + Undo Toast (`19` – `22`)

| # | Viewport & State | Before (`docs/screenshots/ux_improvements/before/`) | After (`docs/screenshots/ux_improvements/after/`) | UX & Architectural Improvements |
| :-: | :--- | :--- | :--- | :--- |
| **19** | **Off-Canvas Navigation Drawer — Tablet (`768x1024`)** | ![Before Nav Drawer Tablet](screenshots/ux_improvements/before/19_nav_drawer_tablet.png) | ![After Nav Drawer Tablet](screenshots/ux_improvements/after/19_nav_drawer_tablet.png) | **Before**: No off-canvas navigation drawer existed for tablet viewports (`<= 1024px`). **After**: Accessible `<OffCanvasNavDrawer />` (`role="dialog"`, `aria-modal="true"`) opens via the hamburger button with backdrop overlay, `Escape` dismissal, workspace tab links, arena switcher, `Command Palette Ctrl+K`, and auto-close on route selection. |
| **20** | **Off-Canvas Navigation Drawer — Mobile (`390x844`)** | ![Before Nav Drawer Mobile](screenshots/ux_improvements/before/20_nav_drawer_mobile.png) | ![After Nav Drawer Mobile](screenshots/ux_improvements/after/20_nav_drawer_mobile.png) | **Before**: Mobile users had no slide-over navigation drawer and header tabs collided with the arena title. **After**: Full-height slide-over navigation drawer on `390x844` mobile viewports providing one-tap access to all views, arenas, command palette, and LTR/RTL toggle. |
| **21** | **RTL (`dir="rtl"`) Logical CSS Layout — Desktop (`1440x900`)** | ![Before RTL Layout Desktop](screenshots/ux_improvements/before/21_rtl_layout_desktop.png) | ![After RTL Layout Desktop](screenshots/ux_improvements/after/21_rtl_layout_desktop.png) | **Before**: Physical CSS properties (`margin-left`, `padding-right`, `text-align: left`) prevented clean bidirectional layout toggling and required manual DOM inspection. **After**: Built-in header/drawer RTL toggle sets `document.documentElement.dir = 'rtl'` and CSS logical properties (`margin-inline`, `padding-inline`, `inset-inline`, `text-align: start`) automatically mirror the header, Outcome Profile, Leaderboard columns, and Pagination Bar. |
| **22** | **Non-Blocking Toast with Undo & `Cmd/Ctrl+K` Command Palette — Desktop (`1440x900`)** | ![Before Toast and Command Palette Desktop](screenshots/ux_improvements/before/22_toast_and_command_palette_desktop.png) | ![After Toast and Command Palette Desktop](screenshots/ux_improvements/after/22_toast_and_command_palette_desktop.png) | **Before**: Neither a keyboard Command Palette (`Cmd/Ctrl + K`) nor a non-blocking Toast Notification stack with Undo existed. **After**: Global `<CommandPalette />` (`Cmd/Ctrl + K`) enables instant keyboard jumping across views and arenas with `<kbd className="kbd-hint">` shortcut badges, while `<ToastProvider />` (`role="status"`, `aria-live="polite"`) displays a non-blocking warning toast with an interactive **`Undo Reset`** button that restores cleared tournament stats in one click. |

---

## 4. Verification Summary

- **Frontend Unit & Architectural Gate Tests (`Vitest`)**: **6 test suites, 28 tests passing (100%)** covering `<ToastProvider />`, `<ConfirmModal />`, `<PaginationBar />`, `<OffCanvasNavDrawer />`, `<CommandPalette />`, Zod form schemas (`codingameTokenSchema`, `codingameDeploySchema`, `simulationFormSchema`), inline validation and real-time error clearing in `<CodinGamePanel />`, URL search-param synchronization (`?q=`, `?pageSize=`, `?sort=&dir=`) in `<Leaderboard />`, XSS sanitization (`sanitizeText`, `sanitizeIdentifier`), static zero-`alert`/`confirm`/`prompt` gate, zero hardcoded hex colors in `.tsx`, all `var(--...)` custom properties defined in `tokens.css`, and `< 500` lines per file across all `ui/src/` modules.
- **Backend Unit & Integration Tests (`pytest`)**: **100% passing**.
- **BDD End-to-End Browser Tests (`Behave` + Headless Chromium)**: **4 features, 10 scenarios, 64 steps passing (100%)** across `1440x900`, `768x1024`, and `390x844` viewports with zero `SEVERE` browser console errors and zero horizontal page overflow.
