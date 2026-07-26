@echo off
setlocal enabledelayedexpansion
title SHTF USB — Reindex Knowledge Base

cd /d "%~dp0"
pushd "%~dp0.."
set "USB_DIR=%CD%"
popd

echo ============================================
echo   SHTF USB — Reindex Knowledge Base
echo ============================================
echo.
echo This rebuilds the search index after adding
echo new .md files to the content/ folder.
echo.

REM Find Python
set "PYTHON="
for %%p in (python3 python) do (
    if not defined PYTHON (
        for /f "tokens=2" %%v in ('%%p --version 2^>nul') do (
            for /f "tokens=1,2 delims=." %%a in ("%%v") do (
                if %%a geq 3 if %%b geq 10 set "PYTHON=%%p"
            )
        )
    )
)
if not defined PYTHON (
    for /f "tokens=2" %%v in ('py -3 --version 2^>nul') do (
        for /f "tokens=1,2 delims=." %%a in ("%%v") do (
            if %%a geq 3 if %%b geq 10 set "PYTHON=py -3"
        )
    )
)
if not defined PYTHON (
    echo X Python 3.10+ not found
    pause
    exit /b 1
)

echo Using: %PYTHON%
echo Content: %USB_DIR%\content\
echo.

REM Kill server if running
taskkill /F /IM llama-server-win64.exe 2>nul
ping -n 2 127.0.0.1 >nul

REM Detect deps dir
set "PY_VER="
for /f "tokens=2" %%v in ('%PYTHON% --version 2^>^&1') do (
    for /f "tokens=1,2 delims=." %%a in ("%%v") do set "PY_VER=%%a.%%b"
)
set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py312"
echo !PY_VER! | findstr /c:"3.14" >nul && set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py314"
echo !PY_VER! | findstr /c:"3.13" >nul && set "DEPS_DIR=%USB_DIR%\ai\deps-win64-py313"

set PYTHONDONTWRITEBYTECODE=1
set PYTHONUNBUFFERED=1
set PYTHONPATH=%DEPS_DIR%

REM Rebuild
echo 🔨 Rebuilding...
cd /d "%USB_DIR%\ai\app"
%PYTHON% rag.py --rebuild --content "%USB_DIR%\outback-safe" --user-content "%USB_DIR%\content" --index "%USB_DIR%\ai\app\search_index.json"

if errorlevel 1 (
    echo.
    echo X Reindex failed
    pause
    exit /b 1
)

echo.
echo ✅ Reindex complete!
echo    Index: ai\app\search_index.json
echo.
echo To restart: double-click ai\start.bat
echo.
pause
