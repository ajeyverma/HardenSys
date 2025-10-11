@echo off
echo Windows Security Compliance CLI Tool
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if running as administrator
net session >nul 2>&1
if errorlevel 1 (
    echo Warning: Not running as Administrator
    echo Some compliance checks may fail without admin privileges
    echo.
    echo To run as Administrator:
    echo 1. Right-click this batch file
    echo 2. Select "Run as administrator"
    echo.
    pause
)

REM Run the compliance CLI
python compliance_cli.py %*

pause

