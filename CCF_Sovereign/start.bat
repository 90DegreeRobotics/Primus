@echo off
REM CCF Sovereign Mind + Sleep Architecture v0.1
echo ========================================
echo   CCF SOVEREIGN MIND
echo   Sleep Architecture v0.1
echo   WAKE / NREM / REM / VALIDATE / SEAL
echo ========================================
echo.

cd /d "%~dp0\src"
python -m main
if errorlevel 1 (
  echo.
  echo [FAIL] Runtime exited with error.
  exit /b 1
)
