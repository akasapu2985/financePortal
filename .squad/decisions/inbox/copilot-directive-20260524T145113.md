### 2026-05-24T14:51:13-07:00: Ralph Dispatch Rule
**By:** Giakas (via Copilot)
**What:** Ralph commands (status, go, start) MUST always spawn Ralph as a general-purpose agent who follows his charter's Startup Routine. The coordinator MUST NOT handle Ralph's work inline. Ralph owns his own auth and reporting logic.
**Why:** User request — three consecutive sessions failed because the coordinator tried to do Ralph's job inline. Ralph's charter has the correct GitHub auth procedure (gh CLI with PATH fix).
**Updated 2026-05-24T15:36:36-07:00:** Auth method is now `gh` CLI (was `git credential fill` + `Invoke-RestMethod` — that was a workaround for a PATH issue, now resolved).
