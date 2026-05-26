$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendPath = Join-Path $RepoRoot 'backend'
$BackendSrcPath = Join-Path $BackendPath 'src'
$EnvFile = Join-Path $RepoRoot '.env'
$EnvExampleFile = Join-Path $RepoRoot '.env.example'
$SchedulerJobName = 'financeportal-scheduler'

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Ensure-Command {
    param([string]$Name, [string]$InstallHint)

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "$Name was not found. $InstallHint"
    }
}

function Ensure-Uv {
    $UvBinPath = Join-Path $HOME '.local\bin'
    if ($env:PATH -notlike "*$UvBinPath*") {
        $env:PATH = "$UvBinPath;$env:PATH"
    }

    if (Get-Command uv -ErrorAction SilentlyContinue) {
        return
    }

    Write-Step 'Installing uv'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if ($LASTEXITCODE -ne 0) {
        throw 'uv installation failed.'
    }

    if ($env:PATH -notlike "*$UvBinPath*") {
        $env:PATH = "$UvBinPath;$env:PATH"
    }

    Ensure-Command -Name 'uv' -InstallHint 'Install uv from https://docs.astral.sh/uv/.'
}

function Get-ComposeCommand {
    if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
        return @('docker-compose')
    }

    docker compose version | Out-Null
    return @('docker', 'compose')
}

function Invoke-Compose {
    param([string[]]$ComposeCommand, [string[]]$Arguments)

    if ($ComposeCommand.Length -gt 1) {
        & $ComposeCommand[0] $ComposeCommand[1..($ComposeCommand.Length - 1)] @Arguments
        return
    }

    & $ComposeCommand[0] @Arguments
}

function Wait-ForPostgresHealth {
    param([string[]]$ComposeCommand)

    $containerId = (Invoke-Compose -ComposeCommand $ComposeCommand -Arguments @('ps', '-q', 'db')).Trim()
    if (-not $containerId) {
        throw 'Unable to locate the PostgreSQL container.'
    }

    for ($attempt = 1; $attempt -le 24; $attempt++) {
        $health = (& docker inspect --format '{{.State.Health.Status}}' $containerId).Trim()
        if ($health -eq 'healthy') {
            Write-Host 'PostgreSQL is healthy.' -ForegroundColor Green
            return
        }

        Start-Sleep -Seconds 5
    }

    throw 'PostgreSQL did not become healthy in time.'
}

Ensure-Command -Name 'python' -InstallHint 'Install Python 3.12 or later first.'
Ensure-Uv
# Ensure Docker is on PATH (winget install may not update current session)
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    $dockerCliPath = 'C:\Program Files\Docker\Docker\resources\bin'
    if (Test-Path (Join-Path $dockerCliPath 'docker.exe')) {
        $env:Path += ";$dockerCliPath"
    } else {
        throw 'Docker is not installed. Run .\setup.ps1 or: winget install Docker.DockerDesktop'
    }
}

# Ensure GitHub CLI is on PATH (installed via winget, sometimes not in fresh shells)
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    $ghPath = 'C:\Program Files\GitHub CLI'
    if (Test-Path (Join-Path $ghPath 'gh.exe')) {
        $env:Path += ";$ghPath"
    } else {
        Write-Host '⚠️  gh CLI not found. Install: winget install GitHub.cli' -ForegroundColor Yellow
    }
}

# Verify Docker daemon is running — offer to launch if not
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    $DockerDesktopExe = 'C:\Program Files\Docker\Docker\Docker Desktop.exe'
    if (Test-Path $DockerDesktopExe) {
        Write-Host '⚠️  Docker Desktop is installed but not running.' -ForegroundColor Yellow
        Write-Host '    Launching Docker Desktop...' -ForegroundColor Cyan
        Start-Process $DockerDesktopExe
        Write-Host '    Waiting for Docker daemon (up to 120s)...' -ForegroundColor Cyan
        $ready = $false
        for ($i = 1; $i -le 24; $i++) {
            Start-Sleep -Seconds 5
            docker info 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) { $ready = $true; break }
            Write-Host "    ... still waiting ($($i * 5)s)" -ForegroundColor DarkGray
        }
        if (-not $ready) {
            throw 'Docker daemon did not start in time. Open Docker Desktop manually and rerun start.ps1.'
        }
        Write-Host '    Docker is ready!' -ForegroundColor Green
    } else {
        throw 'Docker Desktop is not running and could not be found. Run .\setup.ps1 first.'
    }
}

if (-not (Test-Path $EnvFile)) {
    Write-Step 'Creating .env from .env.example'
    Copy-Item $EnvExampleFile $EnvFile
}

$ComposeCommand = Get-ComposeCommand
Write-Step 'Syncing backend dependencies with uv'
uv python install 3.12
uv sync --directory $BackendPath --python 3.12

Write-Step 'Starting PostgreSQL + TimescaleDB'
Invoke-Compose -ComposeCommand $ComposeCommand -Arguments @('up', '-d', 'db')
Write-Step 'Waiting for PostgreSQL health check'
Wait-ForPostgresHealth -ComposeCommand $ComposeCommand

$env:PYTHONPATH = $BackendSrcPath
Write-Step 'Applying database migrations'
uv run --directory $BackendPath python src\db\migrate.py
Write-Step 'Seeding default instruments'
uv run --directory $BackendPath python src\seed.py

Get-Job -Name $SchedulerJobName -ErrorAction SilentlyContinue |
    Stop-Job -ErrorAction SilentlyContinue -PassThru |
    Remove-Job -Force
Write-Step 'Starting collector scheduler in the background'
$null = Start-Job -Name $SchedulerJobName -ScriptBlock {
    param($RepoRoot, $BackendPath, $BackendSrcPath)
    Set-Location $RepoRoot
    $env:PYTHONPATH = $BackendSrcPath
    uv run --directory $BackendPath python ..\pipeline\src\scheduler.py
} -ArgumentList $RepoRoot, $BackendPath, $BackendSrcPath

Write-Host "Scheduler job '$SchedulerJobName' is running in the background." -ForegroundColor Green
Write-Host 'API: http://localhost:8000' -ForegroundColor Yellow
Write-Host 'Docs: http://localhost:8000/docs' -ForegroundColor Yellow
Write-Host 'Press Ctrl+C to stop the API. Use Stop-Job financeportal-scheduler to stop the scheduler job.' -ForegroundColor Yellow

try {
    Write-Step 'Starting FastAPI server'
    uv run --directory $BackendPath uvicorn api.app:app --host 0.0.0.0 --port 8000
} finally {
    Get-Job -Name $SchedulerJobName -ErrorAction SilentlyContinue | Stop-Job -PassThru | Remove-Job -Force
}
