# financePortal

financePortal is a personal financial intelligence dashboard that combines a FastAPI backend, scheduled market-data collectors, PostgreSQL/TimescaleDB storage, and a JavaScript workspace for future UI automation and frontend work. Phase 1 focuses on getting the backend foundation production-track: seeded instruments, price and news collection, and API endpoints that expose the collected data.

## Prerequisites

- Python 3.12+
- Docker Desktop / Docker Engine
- Node.js 20+

## Setup

```powershell
git clone https://github.com/akasapu2985/financePortal.git
Set-Location .\financePortal
Copy-Item .env.example .env
npm install
docker-compose up -d db
python -m uv sync --directory backend --python 3.12
python -m uv run --directory backend python src\db\migrate.py
python -m uv run --directory backend python src\seed.py
```

## Start the stack

```powershell
.\start.ps1
```

### Notes

- `docker-compose up -d db` starts the TimescaleDB/PostgreSQL container used by the backend.
- `.\start.ps1` is the end-to-end bootstrap shortcut: it syncs Python dependencies, waits for PostgreSQL, applies migrations, seeds instruments, starts the scheduler, and launches the API.

## Phase 1 verification

Run the smoke test from a clean synced backend environment:

```powershell
python -m uv run --directory backend pytest tests\integration\test_phase1_smoke.py -q
```

This verification covers API startup, `/health`, seeded instrument responses, `/prices/{symbol}`, `/news`, and one mocked collector execution path.

## Running tests

```powershell
python -m uv run --directory backend pytest -q
python -m uv run --directory backend pytest tests\integration\test_phase1_smoke.py -q
python -m uv run --directory backend ruff check .
```

## Project structure

- `backend/src/api/` — FastAPI app and route modules
- `backend/src/collectors/` — scheduled price/news collection jobs and scheduler
- `backend/src/db/` — asyncpg connection helpers and SQL migrations
- `backend/src/seed.py` — default instrument seeding workflow
- `backend/tests/` — backend pytest coverage, including integration smoke tests
- `docker-compose.yml` — local TimescaleDB/PostgreSQL service definition
- `start.ps1` — PowerShell bootstrap command for local Phase 1 startup
- `.squad/` — team knowledge, history, and decision records
