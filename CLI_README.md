# HardenSys CLI Tool

A command-line interface for running Windows and Linux security compliance checks based on CIS benchmarks and security best practices.

## Features

- Run all compliance checks or filter by category
- Generate text or JSON reports
- Administrator privilege detection
- Progress tracking and detailed output
- Export results to files

## Requirements

- Python 3.7+
- Windows 10/11
- Linux (Ubuntu/Debian)
- Administrator privileges (recommended for full functionality)

## Files

- `compliance_cli.py` - Main CLI script
- `windows_tasks.json` - Compliance task definitions for Windows
- `windows_tasks.py` - Compliance check functions for Windows
- `linux_tasks.json` - Compliance task definitions for Linux
- `linux_tasks.py` - Compliance check functions for Linux

## Usage

### Basic Usage

```bash
# Run all compliance checks
python compliance_cli.py

```

### Filtering by Category

```bash
# Run only Account Policies checks
python HardenSys.py --heading "Account Policies"

# Run only Password Policy checks
python HardenSys.py --subheading "Password Policy"

# Run only Advanced Audit Policy Configuration
python HardenSys.py --heading "Advanced Audit Policy Configuration"
```

### Report Generation

```bash
# Generate text report
python HardenSys.py --output report.txt

# Generate JSON report
python HardenSys.py --format json --output report.json

# Generate report for specific category
python HardenSys.py --heading "Account Policies" --output account_policies.txt
```

### List Available Categories

```bash
# List all available categories and subcategories
python HardenSys.py --list
```

### PowerShell Examples

```powershell
# Run all checks
.\HardenSys.ps1

# Run specific category
.\HardenSys.ps1 -Heading "Account Policies"

# Generate JSON report
.\HardenSys.ps1 -Format json -Output "compliance_report.json"

# List categories
.\HardenSys.ps1 -List
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `--json FILE` | Path to tasks JSON file (default: windows_tasks.json) |
| `--heading NAME` | Filter by heading (e.g., "Account Policies") |
| `--subheading NAME` | Filter by subheading (e.g., "Password Policy") |
| `--output FILE` | Output file for report |
| `--format FORMAT` | Report format: text or json (default: text) |
| `--list` | List available categories and exit |
| `--verbose` | Verbose output |
| `--help` | Show help message |

## Available Categories

- **Account Policies**
  - Password Policy
  - Account Lockout Policy

- **Local Policies**
  - User Rights Assignment

- **Security Options**
  - Accounts
  - Interactive logon
  - Microsoft network server
  - Network security

- **System Settings**
  - User Account Control
  - System Services

- **Windows Defender Firewall with Advanced Security**
  - Private Profile
  - Public Profile

- **Advanced Audit Policy Configuration**
  - Account Logon

- **Microsoft Defender Application Guard**
  - Application Guard Settings

## Report Format

### Text Report
```
HardenSys Compliance Report
========================================
Generated: 2024-01-15 14:30:25
Duration: 45.67 seconds
Total Checks: 121
Successful: 115
Failed: 6
Success Rate: 95.0%

Detailed Results:
========================================

Account Policies
----------------
✓ Enforce password history
  Status: success
  Message: ✓ Password history set to 24 successfully
  Previous: 0 passwords
  Current: 24 passwords
```

### JSON Report
```json
{
  "summary": {
    "total_checks": 121,
    "successful_checks": 115,
    "failed_checks": 6,
    "success_rate": "95.0%",
    "duration_seconds": 45.67,
    "timestamp": "2024-01-15T14:30:25"
  },
  "results": [
    {
      "status": "success",
      "message": "✓ Password history set to 24 successfully",
      "previous": "0 passwords",
      "current": "24 passwords",
      "heading": "Account Policies",
      "subheading": "Password Policy",
      "title": "Enforce password history",
      "script_key": "enforce_password_history",
      "timestamp": "2024-01-15T14:30:25"
    }
  ]
}
```

## Running as Administrator

For full functionality, run the tool as Administrator:

1. **Command Prompt**: Right-click Command Prompt → "Run as administrator"
2. **PowerShell**: Right-click PowerShell → "Run as administrator"
3. **Batch File**: Right-click `HardenSys.bat` → "Run as administrator"

## Troubleshooting

### Common Issues

1. **"Not running as Administrator"**
   - Some checks require admin privileges
   - Run the tool as Administrator for full functionality

2. **"Function not found"**
   - Ensure `windows_tasks.py` is in the same directory
   - Check that the function exists in the file

3. **"JSON file not found"**
   - Ensure `windows_tasks.json` is in the same directory
   - Use `--json` option to specify custom path

4. **Import errors**
   - Ensure all required Python modules are installed
   - Check Python version compatibility

### Error Codes

- Exit code 0: Success
- Exit code 1: Error (file not found, import error, etc.)

## Examples

### Quick Security Check
```bash
python HardenSys.py --heading "Account Policies" --output quick_check.txt
```

### Full Audit with JSON Export
```bash
python HardenSys.py --format json --output full_audit.json
```

### Password Policy Only
```bash
python HardenSys.py --subheading "Password Policy" --verbose
```

### Firewall Configuration Check
```bash
python HardenSys.py --heading "Windows Defender Firewall with Advanced Security"
```

## Integration

The CLI tool can be integrated into:
- Automated security audits
- CI/CD pipelines
- Scheduled tasks
- Monitoring systems
- Compliance reporting

Example scheduled task:
```bash
# Run daily compliance check
schtasks /create /tn "Daily Security Compliance" /tr "python C:\path\to\HardenSys.py --output C:\reports\daily_%date%.txt" /sc daily /st 09:00
```

