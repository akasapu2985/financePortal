# Project Context

- **Project:** financePortal
- **Created:** 2026-05-24

## Core Context

Ralph monitors work progress, reconciles GitHub Issues with actual codebase state, and identifies what's next.

## Recent Updates

### 2026-05-24T13:58Z — Issue Tracker Reconciliation
- Verified issues #2–#31 already closed (Phase 1 complete, Phase 2 largely complete)
- Removed `go:needs-research` label from #32, #33, #34
- Created `go:ready` label and applied to #32, #33, #34
- **Next up:** Phase 2 close-out (#32 responsive collapse, #33 perf, #34 E2E tests)

📌 Team initialized on 2026-05-24

### 2026-05-24T14:57Z — Board Status Check
- ✅ Authentication verified (akasapu2985 token via credential manager)
- 🟢 **3 ready issues** (#32, #33, #34) — Phase 2 close-out work
- 🔴 **30 untriaged** — Future phases not yet triaged
- 🟡 **0 in progress** — Dispatch available
- **Next:** Squad ready to execute Phase 2 remaining work

### 2026-05-25T17:38:20-07:00 — Post-pivot board audit
- ✅ `gh` auth verified for `akasapu2985` (repo-scoped token active)
- 📊 Open board now has **57 open issues**, all still labeled `go:needs-research`; **0** issues are assigned and **0** have `go:ready`
- ✅ **43 issues closed in the last 7 days**; dashboard-era cleanup is already done, so there are **0 stale open dashboard issues** remaining
- 🔁 Open issues #81, #83, #85, and #86 map to code already present on branch `squad/86-extraction-prompts` (`pipeline/src/scheduler.py`, `pipeline/src/intelligence/finbert.py`, `pipeline/src/intelligence/openrouter.py`, `pipeline/src/intelligence/extractor.py` + prompts)
- ⚠️ The board still needs reconciliation because completed Phase 2 work remains open, while later-phase pipeline/MCP issues are still parked in `go:needs-research`
- **Next:** close or retag the completed Phase 2 items first (#81, #83, #85, #86), then pick the next dependency-ordered pipeline item and mark it `go:ready`

## Learnings

- GitHub auth: `gh` CLI is installed at `C:\Program Files\GitHub CLI` and authenticated as `akasapu2985`. Use `gh` for all GitHub operations. If not on PATH, add it: `$env:Path += ";C:\Program Files\GitHub CLI"`
- All 75 issues exist on GitHub. Phase 1 + most of Phase 2 already shipped.
- Write access works via `gh` (akasapu2985 account active).

### 2026-05-24T15:36:36-07:00 — Auth Resolution
- ✅ `gh` CLI was installed the whole time at `C:\Program Files\GitHub CLI` — just missing from PATH
- ✅ Authenticated as `akasapu2985` (active), `giakas_microsoft` (secondary, read-only)
- Charter updated to use `gh` directly with PATH fix at startup
- `start.ps1` updated with `gh` PATH fallback block
- Previous `Invoke-RestMethod` + `git credential fill` approach was a workaround — no longer needed

### 2026-05-24T15:08Z — Status Check: Phase 2 Close-Out Active
- ✅ Authentication verified (akasapu2985 token via credential manager working)
- 🟢 **3 ready issues** (#32, #33, #34) — Phase 2 close-out: responsive collapse, perf <1s, MVP tests
- 🔴 **41 untriaged** — Future phases not yet started
- 🟡 **0 in progress** — No active assignments
- ✅ **31 closed in 7d** — Phase 1 + Phase 2 bulk complete
- **Next:** Squad ready to dispatch on Phase 2 remaining work

---

## 2025-07-17 — Issue Tracker Reconciliation

**What I did:**
Reconciled the GitHub issue tracker against actual completed work in the codebase. Verified the state of all 75 issues and confirmed #2–#31 are already closed.

**What I found:**
- Issues #2–#31 (Phase 1 + Phase 2 complete work): **Already closed** — no action needed.
- Issues #32, #33, #34 (Phase 2 remaining): Open and correctly tagged with `go:needs-research` and `squad:shallan`/`squad:jasnah`.
- Issues #35–#75 (Phases 3–6): Open and untouched — correctly represents future work.

**Auth situation:**
- Only credential available is `giakas_microsoft` (Enterprise Managed User / EMU token) stored in Windows Credential Manager.
- EMU tokens can **read** from personal repos but **cannot write** (POST/PATCH/DELETE) — all write operations return 403.
- Label removal for `go:needs-research` on #32–#34 was blocked by this restriction.
- To perform future write operations, Giakas needs to store a PAT from the `akasapu2985` personal account.

**What's next (Phase 2 remaining):**
- **#32** — Responsive panel collapse (squad:shallan)
- **#33** — Performance optimization: <1s load (squad:shallan)
- **#34** — Dashboard MVP smoke/E2E tests (squad:shallan + squad:jasnah)

**Recommendation:**
Store a `akasapu2985` PAT (with `repo` scope) as `GITHUB_TOKEN` in a local `.env` file (git-ignored) so future agents can perform write operations on the issue tracker.
