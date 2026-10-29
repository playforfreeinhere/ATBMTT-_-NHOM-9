@echo off
cd /d "%~dp0"
py run_gui.py
if errorlevel 1 pause
