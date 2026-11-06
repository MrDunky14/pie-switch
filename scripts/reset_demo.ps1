# ==============================================================================
# pie-Switch Demo Reset Script (PowerShell)
# Cleanly restores target_service/app.py to its original buggy state in 2 seconds.
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Split-Path -Parent $ScriptDir

Write-Host "Resetting pie-Switch to baseline demo state..." -ForegroundColor Cyan

# 1. Restore unpatched target_service/app.py from pristine backup
$OrigFile = Join-Path $RootDir "target_service\app.py.orig"
$TargetFile = Join-Path $RootDir "target_service\app.py"

if (Test-Path $OrigFile) {
    Copy-Item -Path $OrigFile -Destination $TargetFile -Force
    (Get-Item $TargetFile).LastWriteTime = Get-Date
    Write-Host "  [OK] Restored target_service\app.py to original latent-bug state" -ForegroundColor Green
} else {
    Write-Host "  [WARN] target_service\app.py.orig not found" -ForegroundColor Yellow
}

# 2. Reset workspace logs
$WorkspaceDir = Join-Path $RootDir "workspace"
if (-not (Test-Path $WorkspaceDir)) {
    New-Item -ItemType Directory -Path $WorkspaceDir | Out-Null
}
$LogFile = Join-Path $WorkspaceDir "service.log"
Set-Content -Path $LogFile -Value "" -Encoding utf8
Write-Host "  [OK] Cleared .\workspace\service.log" -ForegroundColor Green

# 3. Ensure volumes exist
$ReproDir = Join-Path $WorkspaceDir "repro"
$PatchesDir = Join-Path $WorkspaceDir "patches"
if (-not (Test-Path $ReproDir)) { New-Item -ItemType Directory -Path $ReproDir | Out-Null }
if (-not (Test-Path $PatchesDir)) { New-Item -ItemType Directory -Path $PatchesDir | Out-Null }
Write-Host "  [OK] Verified .\workspace\repro\ and .\workspace\patches\ directories" -ForegroundColor Green

Write-Host "Demo environment reset complete. Ready for chaos trigger or live run." -ForegroundColor Magenta
