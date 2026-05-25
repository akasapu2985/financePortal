$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Summary = [ordered]@{
    Installed = New-Object System.Collections.Generic.List[string]
    AlreadyPresent = New-Object System.Collections.Generic.List[string]
    Failed = New-Object System.Collections.Generic.List[string]
    Skipped = New-Object System.Collections.Generic.List[string]
}
$DockerNeedsRestart = $false
$WingetAvailable = $null -ne (Get-Command winget -ErrorAction SilentlyContinue)

function Write-Step {
    param([string]$Message)
    Write-Host "`n==> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Write-WarningMessage {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Failure {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Add-PathEntry {
    param([string]$PathEntry)

    if (-not (Test-Path $PathEntry)) {
        return
    }

    $pathParts = @($env:PATH -split ';' | Where-Object { $_ })
    if ($pathParts -notcontains $PathEntry) {
        $env:PATH = "$PathEntry;$env:PATH"
    }

    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $userPathParts = @($userPath -split ';' | Where-Object { $_ })
    if ($userPathParts -notcontains $PathEntry) {
        $newUserPath = if ([string]::IsNullOrWhiteSpace($userPath)) {
            $PathEntry
        } else {
            "$userPath;$PathEntry"
        }

        [Environment]::SetEnvironmentVariable('Path', $newUserPath, 'User')
        Write-Success "Added $PathEntry to the user PATH."
    }
}

function Add-SummaryItem {
    param(
        [ValidateSet('Installed', 'AlreadyPresent', 'Failed', 'Skipped')]
        [string]$Bucket,
        [string]$Item
    )

    $Summary[$Bucket].Add($Item)
}

function Refresh-ProcessPath {
    $machinePath = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:PATH = (@($machinePath, $userPath) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join ';'
}

function Test-WingetPackageInstalled {
    param([string]$PackageId)

    if (-not $WingetAvailable) {
        return $false
    }

    $output = & winget list --exact --id $PackageId --accept-source-agreements 2>$null | Out-String
    return $LASTEXITCODE -eq 0 -and $output -match [regex]::Escape($PackageId)
}

function Test-DockerDesktopInstalled {
    return (Test-WingetPackageInstalled -PackageId 'Docker.DockerDesktop') -or
        (Test-Path 'C:\Program Files\Docker\Docker\Docker Desktop.exe')
}

function Test-NodeInstalled {
    return ($null -ne (Get-Command node -ErrorAction SilentlyContinue)) -or
        (Test-Path 'C:\Program Files\nodejs\node.exe') -or
        (Test-WingetPackageInstalled -PackageId 'OpenJS.NodeJS.LTS')
}

function Test-GitHubCliInstalled {
    return ($null -ne (Get-Command gh -ErrorAction SilentlyContinue)) -or
        (Test-Path 'C:\Program Files\GitHub CLI\gh.exe') -or
        (Test-WingetPackageInstalled -PackageId 'GitHub.cli')
}

function Invoke-WingetInstall {
    param(
        [string]$PackageId,
        [string]$DisplayName
    )

    Write-Step "Installing $DisplayName"
    & winget install --exact --id $PackageId --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) {
        throw "winget install failed for $DisplayName."
    }
}

function Invoke-Step {
    param(
        [string]$Name,
        [scriptblock]$Action
    )

    try {
        & $Action
    } catch {
        Write-Failure "$Name failed: $($_.Exception.Message)"
        Add-SummaryItem -Bucket 'Failed' -Item $Name
        return $false
    }

    return $true
}

function Test-Python312Installed {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.12 --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
    }

    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        return $false
    }

    $versionOutput = & $pythonCommand.Source --version 2>&1
    return $versionOutput -match '^Python 3\.12(\.|$)'
}

function Test-PlaywrightChromiumInstalled {
    $cacheRoot = Join-Path $env:LOCALAPPDATA 'ms-playwright'
    if (-not (Test-Path $cacheRoot)) {
        return $false
    }

    return $null -ne (Get-ChildItem -Path $cacheRoot -Directory -Filter 'chromium-*' -ErrorAction SilentlyContinue | Select-Object -First 1)
}

if ($WingetAvailable) {
    Write-Success 'winget is available.'
} else {
    Write-WarningMessage 'winget is not available. Installed tools will be reused, but missing prerequisites cannot be installed automatically.'
}

Invoke-Step -Name 'Docker Desktop' -Action {
    if (Test-DockerDesktopInstalled) {
        Write-Success 'Docker Desktop is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'Docker Desktop'
        return
    }

    if (-not $WingetAvailable) {
        throw 'winget is required to install Docker Desktop. Install Microsoft App Installer or Docker Desktop manually.'
    }

    Invoke-WingetInstall -PackageId 'Docker.DockerDesktop' -DisplayName 'Docker Desktop'
    Refresh-ProcessPath
    $script:DockerNeedsRestart = $true
    Write-Success 'Docker Desktop installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'Docker Desktop'
} | Out-Null

Invoke-Step -Name 'Python 3.12' -Action {
    if (Test-Python312Installed) {
        Write-Success 'Python 3.12 is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'Python 3.12'
        return
    }

    if (-not $WingetAvailable) {
        throw 'winget is required to install Python 3.12. Install Microsoft App Installer or Python 3.12 manually.'
    }

    Invoke-WingetInstall -PackageId 'Python.Python.3.12' -DisplayName 'Python 3.12'
    Refresh-ProcessPath
    if (-not (Test-Python312Installed)) {
        throw 'Python 3.12 was not found after installation.'
    }

    Write-Success 'Python 3.12 installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'Python 3.12'
} | Out-Null

Invoke-Step -Name 'Node.js LTS' -Action {
    if (Test-NodeInstalled) {
        Write-Success 'Node.js LTS is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'Node.js LTS'
        return
    }

    if (-not $WingetAvailable) {
        throw 'winget is required to install Node.js LTS. Install Microsoft App Installer or Node.js manually.'
    }

    Invoke-WingetInstall -PackageId 'OpenJS.NodeJS.LTS' -DisplayName 'Node.js LTS'
    Refresh-ProcessPath
    if (-not (Test-NodeInstalled)) {
        throw 'Node.js LTS was not found after installation.'
    }

    Write-Success 'Node.js LTS installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'Node.js LTS'
} | Out-Null

Invoke-Step -Name 'GitHub CLI' -Action {
    if (Test-GitHubCliInstalled) {
        Write-Success 'GitHub CLI is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'GitHub CLI'
        return
    }

    if (-not $WingetAvailable) {
        throw 'winget is required to install GitHub CLI. Install Microsoft App Installer or GitHub CLI manually.'
    }

    Invoke-WingetInstall -PackageId 'GitHub.cli' -DisplayName 'GitHub CLI'
    Refresh-ProcessPath
    if (-not (Test-GitHubCliInstalled)) {
        throw 'GitHub CLI was not found after installation.'
    }

    Write-Success 'GitHub CLI installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'GitHub CLI'
} | Out-Null

Refresh-ProcessPath
Add-PathEntry -PathEntry (Join-Path $HOME '.local\bin')
Add-PathEntry -PathEntry 'C:\Program Files\GitHub CLI'

$pythonReady = Test-Python312Installed
$nodeReady = Test-NodeInstalled

Invoke-Step -Name 'uv' -Action {
    if (-not $pythonReady) {
        throw 'Python 3.12 must be installed before uv can be installed.'
    }

    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Success 'uv is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'uv'
        return
    }

    Write-Step 'Installing uv'
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if ($LASTEXITCODE -ne 0) {
        throw 'uv installer exited with a non-zero code.'
    }

    Add-PathEntry -PathEntry (Join-Path $HOME '.local\bin')
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        throw 'uv was not found after installation.'
    }

    Write-Success 'uv installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'uv'
} | Out-Null

Invoke-Step -Name 'npm install' -Action {
    if (-not $nodeReady) {
        throw 'Node.js must be installed before npm install can run.'
    }

    Write-Step 'Running npm install at the repo root'
    Push-Location $RepoRoot
    try {
        npm install
        if ($LASTEXITCODE -ne 0) {
            throw 'npm install failed.'
        }
    } finally {
        Pop-Location
    }

    Write-Success 'npm install completed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'npm dependencies'
} | Out-Null

Invoke-Step -Name 'Playwright browsers' -Action {
    if (-not $nodeReady) {
        throw 'Node.js must be installed before Playwright browsers can be installed.'
    }

    if (Test-PlaywrightChromiumInstalled) {
        Write-Success 'Playwright Chromium is already installed.'
        Add-SummaryItem -Bucket 'AlreadyPresent' -Item 'Playwright Chromium'
        return
    }

    Write-Step 'Installing Playwright Chromium browser'
    Push-Location $RepoRoot
    try {
        npx playwright install chromium
        if ($LASTEXITCODE -ne 0) {
            throw 'npx playwright install chromium failed.'
        }
    } finally {
        Pop-Location
    }

    Write-Success 'Playwright Chromium installed.'
    Add-SummaryItem -Bucket 'Installed' -Item 'Playwright Chromium'
} | Out-Null

Write-Host "`n===== Setup Summary =====" -ForegroundColor Magenta
foreach ($bucket in 'Installed', 'AlreadyPresent', 'Skipped', 'Failed') {
    $items = $Summary[$bucket]
    if ($items.Count -eq 0) {
        continue
    }

    $color = switch ($bucket) {
        'Installed' { 'Green' }
        'AlreadyPresent' { 'Yellow' }
        'Skipped' { 'DarkYellow' }
        'Failed' { 'Red' }
    }

    Write-Host "${bucket}:" -ForegroundColor $color
    foreach ($item in $items) {
        Write-Host " - $item" -ForegroundColor $color
    }
}

if ($DockerNeedsRestart) {
    Write-WarningMessage 'Docker Desktop was installed during setup. Restart Windows or sign out/in before using Docker containers.'
}

if ($Summary['Failed'].Count -gt 0) {
    Write-Failure 'Setup finished with errors. Resolve the failed items above and rerun setup.ps1.'
    exit 1
}

Write-Success 'Setup complete. You can now run .\start.ps1.'
