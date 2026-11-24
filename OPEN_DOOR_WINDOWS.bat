@echo off
cd /d "%~dp0"
echo Open Door Continuity - safe offline tools
python --version
if errorlevel 1 (
  echo Python 3.10 or newer is needed. Please install it before continuing.
  pause
  exit /b 1
)
python src\open_door.py --help
pause
