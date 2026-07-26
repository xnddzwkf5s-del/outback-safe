# Outback-Safe USB AI Assistant — PowerShell Launcher
# Right-click → "Run with PowerShell" or run from PowerShell: .\start.ps1
# If execution policy blocks: powershell -ExecutionPolicy Bypass -File start.ps1

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$USB_DIR = Split-Path -Parent $scriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Outback-Safe USB AI Assistant" -ForegroundColor White
Write-Host "  Offline Survival & Medical Reference" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing servers
Write-Host "[1/4] Checking for existing server processes..." -ForegroundColor Gray
Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort 8766 -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1

# Find Python 3.10+
Write-Host "[2/4] Looking for Python 3.10+..." -ForegroundColor Gray
$python = $null
$pythonCandidates = @("python3", "python")
foreach ($candidate in $pythonCandidates) {
    try {
        $verOutput = & $candidate --version 2>&1
        if ($verOutput -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $python = $candidate
                Write-Host "   Found Python $($Matches[0]) ($candidate)" -ForegroundColor Green
                break
            }
        }
    } catch {}
}

# Also try py launcher
if (-not $python) {
    try {
        $verOutput = & py -3 --version 2>&1
        if ($verOutput -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 10) {
                $python = "py"
                $pythonArgs = @("-3")
                Write-Host "   Found Python $($Matches[0]) (py launcher)" -ForegroundColor Green
            }
        }
    } catch {}
}

if (-not $python) {
    Write-Host ""
    Write-Host "X Python 3.10+ not found." -ForegroundColor Red
    Write-Host "Install from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Opening survival reference instead..." -ForegroundColor Yellow
    Start-Process "$USB_DIR\outback-safe\index.html"
    Read-Host "Press Enter to close"
    exit 1
}

# Verify files
Write-Host "[3/4] Verifying required files..." -ForegroundColor Gray
if (-not (Test-Path "$USB_DIR\ai\bin\llama-server-win64.exe")) {
    Write-Host "X Missing: ai\bin\llama-server-win64.exe" -ForegroundColor Red
    Start-Process "$USB_DIR\outback-safe\index.html"
    Read-Host "Press Enter to close"
    exit 1
}
Write-Host "   All files present" -ForegroundColor Green

# Launch server
Write-Host "[4/4] Starting AI server..." -ForegroundColor Gray
Write-Host ""
Write-Host "Model: Qwen 2.5 3B (CPU-only on Windows)" -ForegroundColor White
Write-Host "Expected first response: 15-45 seconds" -ForegroundColor DarkYellow
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

$env:PYTHONDONTWRITEBYTECODE = "1"
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONPATH = "$USB_DIR\ai\deps-win64"

Set-Location "$USB_DIR\ai\app"

try {
    if ($pythonArgs) {
        & $python @pythonArgs server.py --usb-dir $USB_DIR --llama-bin "$USB_DIR\ai\bin\llama-server-win64.exe"
    } else {
        & $python server.py --usb-dir $USB_DIR --llama-bin "$USB_DIR\ai\bin\llama-server-win64.exe"
    }
} finally {
    Write-Host ""
    Write-Host "Shutting down Outback-Safe AI..." -ForegroundColor Yellow
    Get-Process -Name "llama-server-win64" -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Done." -ForegroundColor Green
}
