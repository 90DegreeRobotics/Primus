@echo off
cd /d "%~dp0"
title Primus Sleep Architecture Operator
set PYTHONPATH=%~dp0src;%PYTHONPATH%
python -m operator_ui
if errorlevel 1 (
  echo.
  echo Primus operator UI exited with an error.
  pause
)
