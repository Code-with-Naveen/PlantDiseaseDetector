@echo off
setlocal EnableExtensions
title Plant Disease Detector
cd /d "%~dp0"

echo ============================================================
echo   Plant Disease Detector
echo ============================================================
echo.

set "VENV=%~dp0.venv"
set "PYEXE=%VENV%\Scripts\python.exe"
set "MARK=%VENV%\deps_installed.flag"

if exist "%PYEXE%" goto have_venv

rem ---------- 1. find a suitable Python (3.9 - 3.13) ----------
set "PYCMD="
for %%V in (3.12 3.11 3.10 3.13 3.9) do (
    if not defined PYCMD (
        py -%%V -c "import sys" >nul 2>&1 && set "PYCMD=py -%%V"
    )
)
if not defined PYCMD (
    python -c "import sys; sys.exit(0 if (3,9) <= sys.version_info[:2] <= (3,13) else 1)" >nul 2>&1 && set "PYCMD=python"
)
if not defined PYCMD goto no_python

echo [1/3] Creating virtual environment (first run only) ...
%PYCMD% -m venv "%VENV%"
if errorlevel 1 goto venv_fail

:have_venv
rem ---------- 2. install dependencies ----------
if exist "%MARK%" goto start_app
echo [2/3] Installing required packages (first run only).
echo       This needs an internet connection and can take a few minutes ...
"%PYEXE%" -m pip install --upgrade pip >nul 2>&1
"%PYEXE%" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto pip_fail
echo installed> "%MARK%"

:start_app
rem ---------- 3. start the app (opens your browser automatically) ----------
echo [3/3] Starting the application ...
echo.
"%PYEXE%" "%~dp0main.py"
if errorlevel 1 goto app_fail
goto end

:no_python
echo ERROR: Python 3.9 - 3.13 was not found on this computer.
echo.
echo   1. Download Python 3.12 from https://www.python.org/downloads/windows/
echo   2. During installation tick "Add python.exe to PATH".
echo   3. Double-click run.bat again.
echo.
start "" "https://www.python.org/downloads/windows/"
goto end

:venv_fail
echo ERROR: Could not create the virtual environment.
if exist "%VENV%" rmdir /s /q "%VENV%"
goto end

:pip_fail
echo.
echo ERROR: Package installation failed. Please check your internet connection
echo        and double-click run.bat again (it will resume the installation).
goto end

:app_fail
echo.
echo ERROR: The application stopped unexpectedly. See the messages above.
echo        If the problem persists, delete the ".venv" folder and run run.bat again.

:end
echo.
pause
endlocal
