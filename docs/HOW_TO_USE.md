# How to Use HardenSys

A comprehensive guide on how to use the HardenSys security compliance tool for both Windows and Linux systems.

## 📋 Table of Contents

- [Prerequisites](-#prerequisites)
- [Installation](-#installation)
- [Quick Start](-#quick-start)
- [GUI Interface](-#gui-interface)
- [CLI Interface](-#cli-interface)
- [Understanding Reports](-#understanding-reports)
- [Advanced Usage](-#advanced-usage)
- [Troubleshooting](-#troubleshooting)
- [Best Practices](-#best-practices)

## 🔧 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 or Linux (Ubuntu/Debian/other distributions)
- **Python**: 3.6 or higher
- **Privileges**: Administrator/root privileges (recommended for full functionality)
- **Disk Space**: ~50MB for installation
- **Internet**: Required for downloading dependencies

### Required Privileges
- **Windows**: Run as Administrator for full functionality
- **Linux**: Use `sudo` or run as root for system-level checks

## 🚀 Installation

### Step 1: Download the Tool
```bash
# Clone the repository
git clone https://github.com/ajeyverma/HardenSys.git
cd HardenSys
```

### Step 2: Install Dependencies
```bash
# Windows
pip install -r requirements.txt

# Linux
pip3 install -r requirements.txt
```

### Step 3: Verify Installation
```bash
# Windows
python HardenSys.py --help

# Linux
python3 HardenSys.py --help
```

## ⚡ Quick Start

### GUI Interface (Recommended for Beginners)
```bash
# Windows
python HardenSys_gui.py

# Linux
python3 HardenSys_gui.py
```

### CLI Interface (For Automation)
```bash
# Windows - Generate HTML report
python HardenSys.py --output report.html

# Linux - Generate HTML report
python3 HardenSys.py --output report.html
```

## 🖥️ GUI Interface

### Main Interface Overview
The GUI provides an intuitive interface for running security compliance checks:

1. **Start Screen**: Choose between Windows or Linux compliance checks
2. **Category Selection**: Select specific security categories to check
3. **Run Checks**: Execute compliance checks with progress tracking
4. **View Results**: Review compliance status and recommendations
5. **Generate Reports**: Export results to HTML or PDF format

### Step-by-Step GUI Usage

#### 1. Launch the GUI
```bash
# Windows
python HardenSys_gui.py

# Linux
python3 HardenSys_gui.py
```

#### 2. Select Platform
- Choose **Windows** for Windows security parameters
- Choose **Linux** for Linux security parameters

#### 3. Configure Checks
- **Full System Check**: Run all compliance checks
- **Category Selection**: Choose specific categories (Account Policies, Firewall, etc.)
- **Individual Parameters**: Select specific parameters to check

#### 4. Run Compliance Check
- Click **"Run Compliance Check"**
- Monitor progress in the progress bar
- View real-time status updates

#### 5. Review Results
- **Passed Checks**: Green indicators for compliant settings
- **Failed Checks**: Red indicators with recommendations
- **Details**: Click on parameters for detailed information

#### 6. Generate Reports
- **HTML Report**: Interactive report with detailed findings
- **PDF Report**: Professional report for documentation
- **Save Location**: Choose where to save the report

### GUI Features
- **Real-time Progress**: Live updates during checks
- **Interactive Results**: Click for detailed parameter information
- **Report Generation**: Multiple output formats
- **Backup & Restore**: Security policy backup functionality
- **Settings**: Customize tool behavior

## 💻 CLI Interface

### Basic Usage

#### Run All Compliance Checks
```bash
# Windows
python HardenSys.py --output full_report.html

# Linux
python3 HardenSys.py --output full_report.html
```

#### Generate Different Report Formats
```bash
# HTML Report (Default)
python HardenSys.py --output report.html

# JSON Report
python HardenSys.py --format json --output report.json

# Text Report
python HardenSys.py --format text --output report.txt
```

### Advanced Filtering

#### Filter by Category
```bash
# Windows - Account Policies only
python HardenSys.py --heading "Account Policies" --output account_policies.html

# Linux - Filesystem Configuration only
python3 HardenSys.py --heading "Filesystem Configuration" --output filesystem.html
```

#### Filter by Subcategory
```bash
# Windows - Password Policy only
python HardenSys.py --subheading "Password Policy" --output password_policy.html

# Linux - SSH Configuration only
python3 HardenSys.py --subheading "SSH Configuration" --output ssh_config.html
```

#### Filter by Specific Parameter
```bash
# Windows - Check specific password parameter
python HardenSys.py --parameter "Enforce password history" --output password_history.html

# Linux - Check specific SSH parameter
python3 HardenSys.py --parameter "Ensure SSH private host key files permissions are configured" --output ssh_permissions.html
```

### CLI Options Reference

| Option | Description | Example |
|--------|-------------|---------|
| `--output FILE` | Output file for report | `--output report.html` |
| `--format FORMAT` | Report format (html, json, text) | `--format json` |
| `--heading NAME` | Filter by heading/category | `--heading "Account Policies"` |
| `--subheading NAME` | Filter by subheading | `--subheading "Password Policy"` |
| `--parameter NAME` | Filter by specific parameter | `--parameter "Enforce password history"` |
| `--info NAME` | Show detailed parameter information | `--info "password"` |
| `--list` | List all available categories | `--list` |
| `--verbose` | Verbose output with details | `--verbose` |
| `--help` | Show help message | `--help` |

### Useful CLI Examples

#### Quick Security Check
```bash
# Windows - Quick account policies check
python HardenSys.py --heading "Account Policies" --output quick_check.html

# Linux - Quick filesystem check
python3 HardenSys.py --heading "Filesystem Configuration" --output quick_check.html
```

#### Comprehensive Audit
```bash
# Windows - Full audit with JSON export
python HardenSys.py --format json --output full_audit.json

# Linux - Full audit with verbose output
python3 HardenSys.py --verbose --output full_audit.html
```

#### Specific Parameter Check
```bash
# Windows - Check firewall settings
python HardenSys.py --heading "Windows Defender Firewall with Advanced Security" --output firewall_check.html

# Linux - Check SSH configuration
python3 HardenSys.py --heading "Access Control" --subheading "SSH Configuration" --output ssh_check.html
```

## 📊 Understanding Reports

### Report Types

#### HTML Reports
- **Interactive Elements**: Click for detailed information
- **Visual Indicators**: Color-coded compliance status
- **Navigation**: Easy browsing through results
- **Export Options**: Save as PDF or print

#### JSON Reports
- **Machine Readable**: Perfect for automation
- **Structured Data**: Easy to parse programmatically
- **Integration**: Use with other security tools
- **API Friendly**: Ideal for custom dashboards

#### Text Reports
- **Simple Format**: Easy to read in terminal
- **Log Friendly**: Perfect for system logs
- **Email Friendly**: Can be sent via email
- **Script Integration**: Easy to process with scripts

### Understanding Report Content

#### Summary Section
- **Total Checks**: Number of parameters checked
- **Passed**: Number of compliant parameters
- **Failed**: Number of non-compliant parameters
- **Success Rate**: Percentage of compliance
- **Duration**: Time taken for the scan

#### Detailed Results
- **Parameter Name**: Specific security setting
- **Status**: Pass/Fail/Error
- **Current Value**: Current system setting
- **Recommended Value**: Recommended setting
- **Description**: Detailed explanation
- **Remediation**: Steps to fix non-compliant settings

### Report Categories

#### Windows Categories
1. **Account Policies** (9 parameters)
2. **User Rights Assignment** (7 parameters)
3. **Security Options** (24 parameters)
4. **System Settings** (32 parameters)
5. **Windows Firewall** (18 parameters)
6. **Advanced Audit Policy** (20 parameters)
7. **Application Guard** (11 parameters)

#### Linux Categories
1. **Filesystem Configuration** (16 parameters)
2. **Package Management** (7 parameters)
3. **Services Configuration** (21 parameters)
4. **Network Configuration** (12 parameters)
5. **Access Control** (21 parameters)
6. **System Hardening** (12 parameters)

## 🔧 Advanced Usage

### Automation and Scripting

#### Windows Batch Script
```batch
@echo off
echo Running HardenSys compliance check...
python HardenSys.py --output "C:\Reports\compliance_%date%.html"
echo Compliance check completed. Report saved to C:\Reports\
```

#### Linux Bash Script
```bash
#!/bin/bash
echo "Running HardenSys compliance check..."
python3 HardenSys.py --output "/var/reports/compliance_$(date +%Y%m%d).html"
echo "Compliance check completed. Report saved to /var/reports/"
```

#### PowerShell Script
```powershell
# Run compliance check and email results
$reportPath = "C:\Reports\compliance_$(Get-Date -Format 'yyyyMMdd').html"
python HardenSys.py --output $reportPath

# Email the report
Send-MailMessage -To "admin@company.com" -Subject "Security Compliance Report" -Body "Please find attached the security compliance report." -Attachments $reportPath
```

### Scheduled Tasks

#### Windows Task Scheduler
```bash
# Create daily compliance check
schtasks /create /tn "Daily Security Compliance" /tr "python C:\HardenSys\HardenSys.py --output C:\Reports\daily_%date%.html" /sc daily /st 09:00
```

#### Linux Cron Job
```bash
# Add to crontab for daily checks
0 9 * * * /usr/bin/python3 /opt/HardenSys/HardenSys.py --output /var/reports/daily_$(date +\%Y\%m\%d).html
```

### Integration with CI/CD

#### GitHub Actions Example
```yaml
name: Security Compliance Check
on: [schedule]
jobs:
  compliance-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run HardenSys
        run: |
          python3 HardenSys.py --format json --output compliance.json
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: compliance-report
          path: compliance.json
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Permission Errors
**Problem**: "Access denied" or "Permission denied" errors
**Solution**: 
- **Windows**: Run Command Prompt or PowerShell as Administrator
- **Linux**: Use `sudo` or run as root user

#### 2. Python Not Found
**Problem**: "python: command not found" or "python3: command not found"
**Solution**:
```bash
# Check Python installation
python --version
python3 --version

# Install Python if needed
# Windows: Download from python.org
# Linux: sudo apt install python3
```

#### 3. Module Import Errors
**Problem**: "ModuleNotFoundError" when running the tool
**Solution**:
```bash
# Install required dependencies
pip install -r requirements.txt
# or
pip3 install -r requirements.txt
```

#### 4. JSON File Not Found
**Problem**: "File not found" errors for JSON parameter files
**Solution**:
- Ensure `windows_tasks.json` and `linux_tasks.json` are in the same directory
- Check file permissions
- Verify the tool is run from the correct directory

#### 5. Report Generation Issues
**Problem**: Reports not generating or empty reports
**Solution**:
- Check write permissions in the output directory
- Ensure sufficient disk space
- Verify the output file path is valid

### Debug Mode

#### Enable Verbose Output
```bash
# Windows
python HardenSys.py --verbose --output debug_report.html

# Linux
python3 HardenSys.py --verbose --output debug_report.html
```

#### Check Tool Information
```bash
# List all available parameters
python HardenSys.py --list

# Get help information
python HardenSys.py --help
```

## 📋 Best Practices

### Security Considerations
1. **Always Backup**: Create system backups before applying security changes
2. **Test First**: Test in a non-production environment
3. **Gradual Implementation**: Apply changes gradually to avoid system instability
4. **Review Reports**: Thoroughly review compliance reports before implementation
5. **Document Changes**: Keep records of all security modifications

### Usage Recommendations
1. **Regular Scans**: Run compliance checks regularly (daily/weekly)
2. **Automated Reports**: Set up automated reporting for continuous monitoring
3. **Version Control**: Keep track of security policy changes
4. **Team Collaboration**: Share reports with security teams
5. **Compliance Tracking**: Maintain compliance history for audits

### Performance Optimization
1. **Selective Scanning**: Use category filters for faster scans
2. **Scheduled Runs**: Run scans during off-peak hours
3. **Resource Monitoring**: Monitor system resources during scans
4. **Report Management**: Archive old reports to save disk space
5. **Network Considerations**: Consider network impact for remote systems

### Maintenance
1. **Regular Updates**: Keep the tool updated with latest versions
2. **Dependency Updates**: Update Python dependencies regularly
3. **Parameter Updates**: Update parameter files as security standards evolve
4. **Documentation**: Keep documentation current with tool updates
5. **Training**: Train team members on tool usage and best practices

## 📚 Additional Resources

### Documentation
- **Complete Documentation**: [https://ajeyverma.github.io/HardenSys/docs](https://ajeyverma.github.io/HardenSys/docs)
- **Parameter Reference**: [https://ajeyverma.github.io/HardenSys/docs/parameters.html](https://ajeyverma.github.io/HardenSys/docs/parameters.html)
- **Manual Setup Guide**: [https://ajeyverma.github.io/HardenSys/docs/manual-setup.html](https://ajeyverma.github.io/HardenSys/docs/manual-setup.html)

### Support
- **GitHub Issues**: [https://github.com/ajeyverma/HardenSys/issues](https://github.com/ajeyverma/HardenSys/issues)
- **GitHub Discussions**: [https://github.com/ajeyverma/HardenSys/discussions](https://github.com/ajeyverma/HardenSys/discussions)
- **Repository**: [https://github.com/ajeyverma/HardenSys](https://github.com/ajeyverma/HardenSys)

### Examples and Tutorials
- **CLI Examples**: See the CLI documentation for detailed examples
- **GUI Screenshots**: Check the GUI documentation for interface screenshots
- **Integration Examples**: Advanced topics documentation for automation examples

---

**Need Help?** If you encounter any issues or need assistance, please check the troubleshooting section above or open an issue on GitHub.

**Contributing**: Found a bug or want to suggest an improvement? We welcome contributions! Please see the contributing guidelines in the main repository.
