@echo off
setlocal
set "NOVA_ROOT=%~dp0.."
set "NOVA_PYTHON=%NOVA_ROOT%\.venv\Scripts\pythonw.exe"
if not exist "%NOVA_PYTHON%" exit /b 1

cd /d "%NOVA_ROOT%"
start "" /b "%NOVA_PYTHON%" "%NOVA_ROOT%\main.py" --gui
