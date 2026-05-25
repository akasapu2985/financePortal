# Decisions Log — financePortal

Archived decision records documenting technical choices, policy decisions, and pivots affecting the project.

---

## 2026-05-25 — Kaladin: pipeline scheduler path with backend compatibility

- **By:** Kaladin
- **Time:** 2026-05-25T15:28:43-07:00

Treat `pipeline/src/scheduler.py` plus `pipeline/schedule.yaml` as the canonical scheduler entrypoint for the intelligence-pipeline architecture, while keeping `backend/src/collectors/scheduler.py` as a compatibility export for current imports, tests, and bootstrap scripts.

**Rationale:** Issue #81 targets a pipeline scheduler, but the existing codebase still references the backend collector path. Moving the orchestration logic to `pipeline/` aligns the runtime with the Hermes/MCP pivot without forcing a risky all-at-once import migration across the backend today.

---

## 2026-05-25 — Jasnah: Keep scheduler acceptance gaps visible in skipped tests

- **By:** Jasnah
- **Time:** 2026-05-25T15:28:43-07:00

Cover the implemented issue #81 scheduler behaviors directly in `backend/tests/test_scheduler.py`, and use explicit `pytest.mark.skip` cases only for the two acceptance gaps that are still missing: env-only fallback when `pipeline/schedule.yaml` is absent and validation that rejects zero-minute intervals.

**Rationale:** The current scheduler implementation in `pipeline/src/scheduler.py` already supports YAML-backed schedules, env overrides, scheduler state logging, graceful shutdown, and startup crash tolerance, so those behaviors should be enforced with active tests instead of placeholders. Leaving only the truly missing acceptance criteria as skipped tests keeps the suite honest while still making the remaining delivery scope obvious in test output and review.

**Consequences:** The active scheduler suite now verifies the implemented acceptance criteria instead of deferring them. The two remaining scheduler gaps remain visible to backend contributors and reviewers until implementation lands.

---

## 2026-05-24 — Kaladin: Persist setup PATH fixups for uv and GitHub CLI

- **By:** Kaladin
- **Time:** 2026-05-24T16:14:12-07:00

Have `setup.ps1` add `C:\Users\{user}\.local\bin` and `C:\Program Files\GitHub CLI` to the current session PATH and the user PATH when those directories exist.

**Rationale:** Fresh Windows shells often do not see `uv` or `gh` immediately after installation, which breaks the self-contained setup flow. Persisting the fixups makes the bootstrap idempotent and keeps follow-up commands like `npm install`, `npx playwright install chromium`, and `start.ps1` working without manual PATH edits.

**Consequences:** New shells can resolve `uv` and `gh` after setup without extra user action. Re-running `setup.ps1` remains safe because duplicate PATH entries are skipped.

---

## 2026-05-24 — Kaladin: Persist watchlists with dedicated relational tables

- **By:** Kaladin
- **Time:** 2026-05-24T12:51:37-07:00

Implement watchlist persistence with a dedicated `watchlists` table plus a `watchlist_items` join table keyed by `watchlist_id` and `instrument_id`, and expose CRUD + membership mutation endpoints from a FastAPI router at `/watchlists`.

**Rationale:** The backend already treats `instruments` as the canonical symbol catalog, so referencing `instrument_id` preserves referential integrity and lets watchlists survive app restarts without duplicating instrument metadata. Returning watchlists with embedded instrument rows gives the frontend a single API shape for read, create, update, and membership edits.

**Consequences:** Watchlist membership now validates against the seeded `instruments` table before inserts or deletes. Deleting a watchlist cascades to membership rows automatically through foreign keys.

---

## 2026-05-24 — Kaladin: Default watchlist seed name

- **By:** Kaladin
- **Time:** 2026-05-24T16:43:37-07:00

Treat `My Watchlist` as the canonical seeded default watchlist name in backend seeding.

**Rationale:** The active backend watchlist schema does not carry an `is_default` flag, so the seed needs a stable, idempotent way to find-or-create the starter watchlist before attaching dashboard symbols.

---

## 2026-05-24 — Ralph: GitHub Issue Tracker Reconciliation

- **By:** Ralph (Work Monitor)
- **Time:** 2026-05-24 (via 2025-07-17 entry)

Performed a full reconciliation of the GitHub issue tracker against actual completed work in the codebase.

**Findings:**

| Range | Status | Action |
|-------|--------|--------|
| #1–#31 | Already closed | None required |
| #32–#34 | Open, `go:needs-research` | Phase 2 remaining — left open |
| #35–#75 | Open | Phases 3–6 backlog — left open |

**Auth Blocker:** The only GitHub credential available in Windows Credential Manager is `giakas_microsoft` — an **Enterprise Managed User (EMU)** token. EMU tokens can read from personal repos but cannot write (POST/PATCH/DELETE). All write operations return HTTP 403.

- Commenting on issues is blocked
- Closing issues via API is blocked
- Removing labels is blocked

**Resolution required:** Giakas must create a Personal Access Token (PAT) from the `akasapu2985` GitHub account with `repo` scope and store it as `GITHUB_TOKEN` in `.env.local` (which is `.gitignore`d) so agents can perform write operations.

**Phase 2 Remaining:**
1. **#32** — Responsive panel collapse behavior (assigned: Shallan)
2. **#33** — Dashboard performance optimization to <1s (assigned: Shallan)
3. **#34** — Dashboard MVP smoke + E2E test coverage (assigned: Shallan + Jasnah)

---

## 2026-05-24 — Giakas: Commit and push rule

- **By:** Giakas (via Copilot)
- **Time:** 2026-05-24T12:51:37-07:00

Every completed issue/step MUST be committed AND pushed to remote. No local-only work. Include CHANGELOG.md updates in every commit. The repo must always reflect current state on GitHub.

**Rationale:** User directive — repo will be cloned to another machine. Remote must be up to date at all times.

---

## 2026-05-24 — Giakas: Ralph dispatch rule

- **By:** Giakas (via Copilot)
- **Time:** 2026-05-24T15:36:36-07:00

Ralph commands (status, go, start) MUST always spawn Ralph as a general-purpose agent who follows his charter's Startup Routine. The coordinator MUST NOT handle Ralph's work inline. Ralph owns his own auth and reporting logic.

**Rationale:** User request — three consecutive sessions failed because the coordinator tried to do Ralph's job inline. Ralph's charter has the correct GitHub auth procedure (gh CLI with PATH fix).

**Update:** Auth method is now `gh` CLI (was `git credential fill` + `Invoke-RestMethod` — that was a workaround for a PATH issue, now resolved).

---

## 2026-05-24 — Giakas: Pivot away from custom dashboard

- **By:** Giakas (via Copilot)
- **Time:** 2026-05-24T19:38:49-07:00

Pivot away from building a custom dashboard. Use Fidelity Tracker+ as the UI instead. The project's value is in data gathering and making it easy/fast/cheap for the AI agent (Hermes) to access that data. No custom React frontend needed.

**Rationale:** User request — building a dashboard is overkill when Fidelity Tracker+ already exists. Focus engineering on the intelligence/data layer.

---

## 2026-05-24 — Dalinar: Architecture pivot — intelligence pipeline for Hermes

- **By:** Dalinar
- **Time:** 2026-05-24T20:37:13-07:00
- **Status:** Active

financePortal has pivoted from a full financial dashboard to a **financial intelligence pipeline** that feeds Hermes.

**New Architecture:**

```
[Gather]          [Filter]           [Analyze]          [Serve]
Finnhub/yfinance → Regex + FinBERT → DeepSeek extracts → Hermes reads via MCP
(free APIs)        (zero cost)        (~$0.01/day)        (~2,500 tokens/session)
```

**Key Decisions:**

1. **No dashboard** — Fidelity Tracker+ handles visualization. We build no frontend.
2. **No FastAPI** — No HTTP REST API for humans. MCP is the only interface.
3. **SQLite-first** — No Docker, no TimescaleDB. Plain SQLite with WAL mode.
4. **FinBERT pre-filter** — Local CPU model eliminates ~80-90% of articles before DeepSeek.
5. **DeepSeek via OpenRouter** — $0.27/1M tokens, batched every 6h, not real-time.
6. **MCP is Phase 3, not Phase 6** — It's the primary deliverable, not an afterthought.
7. **Telegram for push** — morning brief (7am), evening brief (6pm), immediate critical alerts.
8. **Daily cost target: ~$0.05** — well-defined budget constraint.

**Phase Breakdown (4 phases replacing 6):**

- **Phase 1:** Foundation — collectors + SQLite schema + APScheduler
- **Phase 2:** Intelligence — FinBERT + DeepSeek + briefs
- **Phase 3:** Hermes — MCP server + Telegram delivery
- **Phase 4:** Advanced signals — Reddit, insider trades, pattern detection

**What Is Abandoned:**

- React/Vite frontend
- FastAPI REST server
- Docker Compose / TimescaleDB
- Dashboard-facing alert UI
- Multi-phase alert tier system (dashboard panels)

**Rationale:** The user already has Fidelity Tracker+ for portfolio visualization. Building a second dashboard duplicates effort and adds maintenance burden with no incremental value. The intelligence pipeline delivers the same market awareness through Hermes + Telegram with ~$0.05/day operating cost and zero frontend maintenance.

---

## 2026-05-24 — Jasnah: Phase 1 smoke test uses mocked backend dependencies

- **By:** Jasnah
- **Time:** 2026-05-24T12:47:40-07:00

Implement the Phase 1 smoke test as a pytest integration suite that exercises the FastAPI app with `TestClient`, a mocked asyncpg pool, and mocked collector dependencies instead of requiring Docker-backed Postgres or live market/news APIs.

**Rationale:** This keeps the verification command runnable in a clean developer environment and in CI without external infrastructure. It still validates the API contracts, seeded-data responses, and collector orchestration paths needed for Phase 1 production-track confidence.

**Consequences:** The smoke test is fast and deterministic. Live container wiring remains covered by the documented startup flow rather than this automated smoke suite.

---

## 2026-05-24 — Shallan: Dashboard proxy + starter watchlist bootstrap

- **By:** Shallan
- **Time:** 2026-05-24T16:42:34-07:00

The frontend dashboard will treat `/api/*` as a client-only namespace and rely on the Vite dev proxy to rewrite requests onto the backend's root-mounted routes. When the watchlist service returns no watchlists, the UI will auto-create a starter watchlist from the seeded instruments so the desktop dashboard opens with a usable left rail instead of an empty state.

**Rationale:** The backend currently serves `watchlists`, `instruments`, `news`, and `prices` without an `/api` prefix, which caused the frontend to load permanent 404 states in development. Auto-bootstrapping the first watchlist keeps the dashboard aligned with the three-column Bloomberg-style design by ensuring the chart/news rails have an active symbol immediately.

**Trade-offs:** This keeps local development self-healing and removes first-run confusion, but it means the frontend owns a small amount of bootstrap behavior until the backend guarantees a default watchlist and seeded prices.

---

## 2026-05-24 — Shallan: shadcn/ui + token-driven dashboard overhaul

- **By:** Shallan
- **Time:** 2026-05-24T17:10:08-07:00

The frontend dashboard will standardize on `shadcn/ui` primitives layered on top of the existing Tailwind CSS v4 token system. New UI work should compose `frontend/src/components/ui/` building blocks first, then apply the finance dashboard palette and density rules through the shared CSS tokens instead of continuing with raw one-off HTML styling.

**Rationale:** `npx shadcn@latest init` completed successfully in the Vite frontend even with Tailwind v4, which removes the compatibility risk called out at handoff. Using shared primitives gives the dashboard consistent spacing, hover states, badges, buttons, and cards while still preserving the dark financial design system Renarin defined.

**Trade-offs:** This adds a small dependency footprint and requires maintaining the custom token mapping in `frontend/src/index.css`, but it prevents the UI from drifting back into wireframe-level bespoke markup and keeps future dashboard polish work faster and more consistent.

---

## 2026-05-24 — Shallan: Tailwind theme tokens as CSS variables

- **By:** Shallan
- **Time:** 2026-05-24T12:51:37-07:00

Keep the approved dashboard dark-theme values in `frontend/src/styles/tokens.css` as CSS custom properties, then mirror those values into `frontend/tailwind.config.ts` and `frontend/src/styles/index.css` so Tailwind utilities and shared semantic classes both point at the same token set.

**Rationale:** The design spec is already token-driven, and CSS variables keep those values reusable for Tailwind utilities, chart libraries, and any non-Tailwind styling without duplicating ad hoc hex values through components. This also keeps semantic gain/loss/warning/info styling centralized for dense dashboard surfaces.

**Consequences:** Shared theme and status styling can be reused without inline color literals. Future chart, watchlist, and alerts work can consume the same dark-theme tokens from CSS or Tailwind.

---

## 2026-05-25 — Kaladin: OpenRouter Client Standardization

- **By:** Kaladin
- **Time:** 2026-05-25T15:28:43-07:00
- **Issue:** #85

Standardize DeepSeek OpenRouter access in `pipeline/src/intelligence/openrouter.py` on a shared async `httpx.AsyncClient` wrapper with injectable transport and sleep dependencies for deterministic mocked tests.

**Rationale:** Phase 2 intelligence work needs one MCP-facing client pattern for LLM calls that is easy to reuse, retries transient 408/429/5xx failures with exponential backoff, and logs token usage on every successful request for cost visibility.

**Follow-up:** Future intelligence modules should build on this client instead of making raw OpenRouter calls directly.

---

EOF
