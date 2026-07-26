@echo off
setlocal enabledelayedexpansion
title Outback-Safe USB AI Assistant

REM ===================================================
REM  Outback-Safe USB Windows Launcher
REM  Pauses on every exit — window never closes silently.
REM  Full diagnostic log: shtf-diag.txt on USB root.
REM ===================================================

REM ── Determine USB root ──
cd /d "%~dp0"
pushd "%~dp0.."
set "USB_DIR=%CD%"
popd
REM Ensure trailing backslash for drive root (E:\ not E: — Path.resolve needs it)

REM ── Start logging immediately ──
set "LOG=%USB_DIR%\shtf-diag.txt"
echo ===== SHTF USB Diagnostic Log =====> "%LOG%"
echo Time: %date% %time%>> "%LOG%"
echo USB dir: %USB_DIR%>> "%LOG%"
echo.>> "%LOG%"
echo [LOG] Startup OK>> "%LOG%"

REM ── Verify USB is writable ──
set "TEST_FILE=%USB_DIR%\ai\.write_test"
(echo test > "%TEST_FILE%") 2>nul
if not exist "%TEST_FILE%" (
    echo WARNING: USB is read-only or corrupted.
    echo Opening survival reference instead...
    start "" "%USB_DIR%\outback-safe\index.html"
    pause
    exit /b 1
)
del "%TEST_FILE%" 2>nul

echo ============================================
echo   Outback-Safe USB AI Assistant
echo   Offline Survival ^& Medical Reference
echo ============================================
echo.

REM ── Kill existing servers ──
echo [1/5] Checking for existing server processes...
echo [LOG] Step 1: process check>> "%LOG%"
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8765 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>nul
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8766 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" 2>nul
taskkill /F /IM llama-server-win64.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Outback*" 2>nul
ping -n 2 127.0.0.1 >nul 2>&1
echo [LOG] Step 1 done>> "%LOG%"

REM ── Find Python 3.10+ ──
echo [2/5] Looking for Python 3.10+...
echo [LOG] Step 2: Python detection started>> "%LOG%"
set "PYTHON="
set "PY_VER="

for %%p in (python3 python) do (
    if not defined PYTHON (
        for /f "tokens=2" %%v in ('%%p --version 2^>nul') do (
            for /f "tokens=1,2 delims=." %%a in ("%%v") do (
                if %%a geq 3 if %%b geq 10 (
                    set "PYTHON=%%p"
                    set "PY_VER=%%a.%%b"
                    echo    Found Python %%v ^(%%p^)
                )
            )
        )
    )
)

if not defined PYTHON (
    for /f "tokens=2" %%v in ('py -3 --version 2^>nul') do (
        for /f "tokens=1,2 delims=." %%a in ("%%v") do (
            if %%a geq 3 if %%b geq 10 (
                set "PYTHON=py -3"
                set "PY_VER=%%a.%%b"
                echo    Found Python %%v ^(py launcher^)
            )
        )
    )
)

if defined PYTHON goto :have_python

REM =======================================================
REM  PATH: No Python found
REM =======================================================
:no_python
echo [LOG] Step 2 FAILED: Python not found>> "%LOG%"
echo.
echo X Python 3.10+ not found on this computer.
echo.
echo QUICK FIX (choose one):
echo   [A] winget install Python.Python.3.12
echo   [B] https://www.python.org/downloads/
echo   [C] Microsoft Store: search "Python 3.12"
echo.
choice /C YN /M "Try auto-install with winget"
if errorlevel 2 goto :no_python_fallback
echo Running: winget install Python.Python.3.12...
winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements 2>&1
echo.
echo If install succeeded, close this window and re-run start.bat
pause
goto :no_python_fallback

:no_python_fallback
echo Opening survival reference (always works)...
start "" "%USB_DIR%\outback-safe\index.html"
pause
exit /b 1

REM =======================================================
REM  PATH: Python found
REM =======================================================
:have_python
echo [LOG] Step 2 OK: PYTHON=!PYTHON! PY_VER=!PY_VER!>> "%LOG%"

REM ── Select deps directory ──
set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py312"
echo [3/5] Selecting deps for Python !PY_VER!...
echo [LOG] Step 3: Matching deps for PY_VER=!PY_VER!>> "%LOG%"
echo !PY_VER! | findstr /c:"3.14" >nul && set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py314"
echo !PY_VER! | findstr /c:"3.13" >nul && set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py313"
echo !PY_VER! | findstr /c:"3.12" >nul && set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py312"
echo [LOG] DEPS_DIR=!DEPS_DIR!>> "%LOG%"

REM ── Check if deps exist ──
echo [LOG] Checking if !DEPS_DIR!\numpy exists...>> "%LOG%"
if exist "!DEPS_DIR!\numpy" goto :deps_ok

REM ── Deps missing ──
echo [LOG] Deps NOT found>> "%LOG%"
echo.
echo WARNING: No pre-built deps for Python !PY_VER!
echo    Bundled: Python 3.12 and 3.14
echo    Your Python: !PY_VER!
echo.
choice /C YN /M "Install deps now (needs internet, ~30s)"
if errorlevel 2 goto :deps_fallback
echo Installing deps for Python !PY_VER!...
mkdir "!DEPS_DIR!" 2>nul
!PYTHON! -m pip install --target "!DEPS_DIR!" flask rank_bm25 numpy colorama 2>&1
if errorlevel 1 (
    echo [LOG] Deps install FAILED>> "%LOG%"
    echo X Install failed.
    pause
    goto :deps_fallback
)
echo [LOG] Deps installed successfully>> "%LOG%"
goto :deps_ok

:deps_fallback
echo.
echo Opening survival reference (works without deps)...
start "" "%USB_DIR%\outback-safe\index.html"
pause
exit /b 1

REM ── Deps OK, continue ──
:deps_ok
echo [LOG] Deps OK>> "%LOG%"
echo    Deps: deps-win64-py!PY_VER!

REM =======================================================
REM  PATH: Verify files and launch
REM =======================================================
echo [4/5] Verifying files...
echo [LOG] Step 4: Verifying files>> "%LOG%"

if not exist "%USB_DIR%\ai\bin\llama-server-win64.exe" (
    echo [LOG] FAIL: llama-server-win64.exe missing>> "%LOG%"
    echo X ERROR: Missing ai\bin\llama-server-win64.exe
    echo   The USB may be incomplete.
    pause
    start "" "%USB_DIR%\outback-safe\index.html"
    pause
    exit /b 1
)

if not exist "%USB_DIR%\ai\app\search_index.json" (
    echo [LOG] FAIL: search_index.json missing>> "%LOG%"
    echo X ERROR: Missing ai\app\search_index.json
    pause
    start "" "%USB_DIR%\outback-safe\index.html"
    pause
    exit /b 1
)

echo [LOG] Step 4 OK: All files present>> "%LOG%"
echo    All files present

REM ── Launch server ──
echo [5/5] Starting AI server...
echo [LOG] Step 5: Launching server.py>> "%LOG%"
echo [LOG] Command: !PYTHON! server.py --usb-dir %USB_DIR% --llama-bin "%USB_DIR%\ai\bin\llama-server-win64.exe">> "%LOG%"
echo.
echo Model: Qwen 2.5 3B (CPU-only on Windows)
echo Python: !PY_VER!  ^|  Deps: deps-win64-py!PY_VER!
echo Logs: %USB_DIR%\launcher.log
echo Browser opens when ready. Press Ctrl+C to stop.
echo.

set "PYTHONDONTWRITEBYTECODE=1"
set "PYTHONUNBUFFERED=1"
set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH=!DEPS_DIR!"

cd /d "%USB_DIR%\ai\app"
%PYTHON% server.py --usb-dir %USB_DIR% --llama-bin "%USB_DIR%\ai\bin\llama-server-win64.exe" >> "%USB_DIR%\launcher.log" 2>&1

REM ── Server exited ──
echo [LOG] server.py exited with code !ERRORLEVEL!>> "%LOG%"
echo.
echo ==============================================
echo   Server stopped.
echo   Check launcher.log on USB for details.
echo ==============================================
echo.
taskkill /F /IM llama-server-win64.exe 2>nul
echo [LOG] Cleanup complete>> "%LOG%"
pause
endlocal
