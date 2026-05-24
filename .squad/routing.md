# Work Routing

How to decide who handles what.

## Routing Table

| Work Type | Route To | Examples |
|-----------|----------|----------|
| Architecture & system design | Dalinar | Component boundaries, data flow, API contracts, tech decisions |
| Backend services & data collection | Kaladin | Python services, scrapers, API integrations, processing pipelines |
| Dashboard UI & visualization | Shallan | React components, charts, watchlists, alerts UI, responsive design |
| Database & data pipelines | Navani | PostgreSQL schema, migrations, caching strategy, data normalization |
| Testing & quality | Jasnah | Unit tests, integration tests, edge cases, load testing |
| Code review | Dalinar | Review PRs, check quality, suggest improvements |
| MCP server & agent integration | Kaladin + Navani | MCP protocol, Hermes agent, Telegram notifications |
| Requirements & PRDs | Adolin | PRD writing, user stories, acceptance criteria, feature specs |
| Ideation & research | Adolin | Feature ideas, competitive analysis, data source research, suggestions |
| API & data source research | Wit | API discovery, rate limits, auth flows, data format analysis, competitive tool research |
| Dashboard design & UX | Renarin | Layout, charts, data visualization, information hierarchy, design specs |
| Scope & priorities | Adolin + Dalinar | What to build next, trade-offs, phasing decisions |
| Session logging | Scribe | Automatic — never needs routing |

## Issue Routing

| Label | Action | Who |
|-------|--------|-----|
| `squad` | Triage: analyze issue, assign `squad:{member}` label | Dalinar |
| `squad:dalinar` | Architecture, design, review tasks | Dalinar |
| `squad:kaladin` | Backend services, APIs, data collection | Kaladin |
| `squad:shallan` | UI, dashboard, frontend components | Shallan |
| `squad:navani` | Database, data pipelines, caching | Navani |
| `squad:jasnah` | Testing, quality, verification | Jasnah |
| `squad:adolin` | Requirements, PRDs, research, ideation | Adolin |
| `squad:wit` | API research, data sources, competitive analysis | Wit |
| `squad:renarin` | Design, visualization, UX, dashboard layout | Renarin |

### How Issue Assignment Works

1. When a GitHub issue gets the `squad` label, **Dalinar** triages it — analyzing content, assigning the right `squad:{member}` label, and commenting with triage notes.
2. When a `squad:{member}` label is applied, that member picks up the issue in their next session.
3. Members can reassign by removing their label and adding another member's label.
4. The `squad` label is the "inbox" — untriaged issues waiting for Dalinar's review.

## Rules

1. **Eager by default** — spawn all agents who could usefully start work, including anticipatory downstream work.
2. **Scribe always runs** after substantial work, always as `mode: "background"`. Never blocks.
3. **Quick facts → coordinator answers directly.** Don't spawn an agent for "what port does the server run on?"
4. **When two agents could handle it**, pick the one whose domain is the primary concern.
5. **"Team, ..." → fan-out.** Spawn all relevant agents in parallel as `mode: "background"`.
6. **Anticipate downstream work.** If a feature is being built, spawn the tester to write test cases from requirements simultaneously.
7. **Issue-labeled work** — when a `squad:{member}` label is applied to an issue, route to that member. Dalinar handles all `squad` (base label) triage.
8. **Changelog rule** — every agent MUST update CHANGELOG.md when making changes. This is a global rule for all work.
