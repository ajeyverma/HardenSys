# Windows Security Compliance CLI Tool - PowerShell Launcher
# Run with: .\run_compliance.ps1

param(
    [string]$Heading,
    [string]$Subheading,
    [string]$Output,
    [string]$Format = "text",
    [switch]$List,
    [switch]$Verbose
)

Write-Host "Windows Security Compliance CLI Tool" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Yellow
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Warning: Not running as Administrator" -ForegroundColor Yellow
    Write-Host "Some compliance checks may fail without admin privileges" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Cyan
    Write-Host "1. Right-click PowerShell" -ForegroundColor Cyan
    Write-Host "2. Select 'Run as administrator'" -ForegroundColor Cyan
    Write-Host "3. Navigate to this directory and run: .\run_compliance.ps1" -ForegroundColor Cyan
    Write-Host ""
}

# Build command arguments
$args = @()

if ($Heading) { $args += "--heading", "`"$Heading`"" }
if ($Subheading) { $args += "--subheading", "`"$Subheading`"" }
if ($Output) { $args += "--output", "`"$Output`"" }
if ($Format) { $args += "--format", $Format }
if ($List) { $args += "--list" }
if ($Verbose) { $args += "--verbose" }

# Run the compliance CLI
Write-Host "Running compliance checks..." -ForegroundColor Cyan
Write-Host ""

try {
    if ($args.Count -gt 0) {
        & python compliance_cli.py @args
    } else {
        & python compliance_cli.py
    }
} catch {
    Write-Host "Error running compliance CLI: $_" -ForegroundColor Red
}

Write-Host ""
Read-Host "Press Enter to exit"

