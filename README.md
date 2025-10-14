# HardenSys - Unified System Hardening Tool

A comprehensive security policy management and compliance checking tool for Windows and Linux systems. This tool helps organizations and system administrators enforce, manage, and audit security policies through both CLI and GUI interfaces.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Linux](https://img.shields.io/badge/platform-Linux-ff0000)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://ajeyverma.github.io/HardenSys/docs)

## 🛡️ Features

- **🔒 Comprehensive Security Coverage**
  - **121 Windows Parameters**: Account Policies, User Rights, Security Options, System Settings, Firewall, Audit Policy, Application Guard
  - **89 Linux Parameters**: Filesystem Configuration, Package Management, Services, Network, Access Control, System Hardening
  - **CIS Benchmark Compliance**: Based on industry-standard security benchmarks

- **🖥️ Dual Interface Support**
  - **CLI Interface**: Command-line tool for automation and scripting
  - **GUI Interface**: User-friendly graphical interface for interactive management
  - **Cross-Platform**: Full support for both Windows and Linux systems

- **⚡ Advanced Capabilities**
  - **Automatic Backup & Restore**: Security policy backup with restore capability
  - **Multiple Report Formats**: HTML, PDF, JSON, and text reports
  - **Real-time Monitoring**: Live policy status monitoring and compliance checking
  - **Batch Processing**: Support for automated security audits
  - **Progress Tracking**: Detailed progress indicators and status updates

- **📚 Professional Documentation**
  - **Live Documentation**: Complete GitHub Pages documentation
  - **Interactive Reference**: Searchable parameter database with 210+ parameters
  - **Step-by-Step Guides**: Detailed setup instructions for both platforms
  - **API Documentation**: Complete CLI and GUI interface documentation
  - **Examples & Tutorials**: Real-world usage scenarios and best practices

## 🚀 Quick Start

### Prerequisites
- **Operating System**: Windows 10/11 or Linux (Ubuntu/Debian/other distributions)
- **Python**: 3.6 or higher
- **Privileges**: Administrator/root privileges (recommended for full functionality)
- **Disk Space**: ~50MB for installation

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AjeyVerma/HardenSys.git
cd HardenSys
```

2. **Install required dependencies:**
```bash
# Windows
pip install -r requirements.txt

# Linux
pip3 install -r requirements.txt
```

### Usage

#### 🖥️ GUI Interface
Run the graphical interface for interactive management:
```bash
# Windows
python HardenSys_gui.py

# Linux
python3 HardenSys_gui.py
```

#### 💻 CLI Interface
Run compliance checks and generate reports:
```bash
# Windows - Basic usage
python HardenSys.py --output report.html

# Linux - Basic usage
python3 HardenSys.py --output report.html

# Advanced usage with filtering
python HardenSys.py --heading "Account Policies" --format json --output account_policies.json

# List all available parameters
python HardenSys.py --list
```

## 📚 Documentation

Visit our comprehensive documentation at: **[https://ajeyverma.github.io/HardenSys/docs](https://ajeyverma.github.io/HardenSys/docs)**

### 📖 Documentation Features
- **🔍 Interactive Parameter Reference**: Search and explore all 210+ security parameters
- **📋 Step-by-Step Guides**: Complete setup instructions for both Windows and Linux
- **📖 API Documentation**: Full CLI and GUI interface documentation
- **💡 Examples & Tutorials**: Real-world usage scenarios and best practices
- **🔧 Troubleshooting**: Common issues and solutions
- **🎯 Quick Start Guides**: Get up and running in minutes
- **📊 Report Examples**: Sample reports and output formats

## 📊 Compliance Categories

### 🪟 Windows (121 Parameters)
| Category | Parameters | Description |
|----------|------------|-------------|
| **Account Policies** | 9 | Password policies, account lockout settings, Kerberos authentication |
| **User Rights Assignment** | 7 | Administrative privileges, system access controls, security permissions |
| **Security Options** | 24 | Network security, User Account Control, system cryptography |
| **System Settings** | 32 | Critical service configurations, security-related services |
| **Windows Firewall** | 18 | Firewall profiles, connection security, rule management |
| **Advanced Audit Policy** | 20 | Account logon, object access, system events |
| **Application Guard** | 11 | Microsoft Defender Application Guard settings |

### 🐧 Linux (89 Parameters)
| Category | Parameters | Description |
|----------|------------|-------------|
| **Filesystem Configuration** | 16 | Kernel modules, partitions, file system security |
| **Package Management** | 7 | Bootloader settings, process hardening |
| **Services Configuration** | 21 | Server and client services, time synchronization |
| **Network Configuration** | 12 | Network parameters, firewall configuration |
| **Access Control** | 21 | SSH, PAM, user account controls |
| **System Hardening** | 12 | Additional kernel and system security measures |

## 📝 Reports

The tool generates comprehensive compliance reports in multiple formats:

### 📊 Report Formats
- **HTML Reports**: Interactive elements with detailed compliance status
- **PDF Reports**: Professional documentation for formal compliance
- **JSON Reports**: Machine-readable format for automation and integration
- **Text Reports**: Simple, readable format for quick review

### 📈 Report Features
- **Detailed Compliance Status**: Pass/fail status for each parameter
- **Recommendations**: Specific guidance for non-compliant settings
- **Progress Tracking**: Real-time status updates during scans
- **Export Capabilities**: Save reports for analysis and documentation

## 🔒 Security Considerations

### ⚠️ Important Security Notes
- **Administrator Privileges**: Always run with administrator/root privileges for full functionality
- **Backup First**: Create a backup before applying any security changes
- **Review Reports**: Thoroughly review compliance reports before implementation
- **Test Environment**: Test in a non-production environment first
- **Gradual Implementation**: Implement changes gradually to avoid system instability

## 🤝 Contributing

We welcome contributions to HardenSys! Whether you're fixing bugs, adding features, or improving documentation, your contributions help make this tool better for everyone.

### 🚀 How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Make your changes** and test thoroughly
4. **Commit your changes**: `git commit -m 'Add some AmazingFeature'`
5. **Push to your branch**: `git push origin feature/AmazingFeature`
6. **Open a Pull Request** with a clear description of your changes

### 📋 Contribution Guidelines
- **Bug Reports**: Use the issue template and provide detailed information
- **Feature Requests**: Describe the use case and expected behavior
- **Code Changes**: Follow the existing code style and add tests where appropriate
- **Documentation**: Update relevant documentation for any changes

## 📄 License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)  
© 2025 [Ajay Kumar](https://github.com/ajeyverma)  
*(also known as Ajay Verma / Aarush Chaudhary)*

## ⚠️ Disclaimer

This tool is provided **"as is"** without warranty of any kind.  
Use it **at your own risk**. The author is **not responsible** for any damage, data loss, or misconfiguration caused by the use of this tool.

**Always test security or system tools in a safe or virtual environment before using them on production machines.**

## 🔗 Quick Links

- **📚 Documentation**: [https://ajeyverma.github.io/HardenSys/docs](https://ajeyverma.github.io/HardenSys/docs)
- **🐛 Report Issues**: [GitHub Issues](https://github.com/ajeyverma/HardenSys/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/ajeyverma/HardenSys/discussions)
- **⭐ Star the Project**: [GitHub Repository](https://github.com/ajeyverma/HardenSys)

<!-- ## 👨‍💻 Author

Developed and maintained by **Ajay Kumar**  
*(also known as **Ajay Verma** / **Aarush Chaudhary** in different communities)*  

- GitHub: [@ajeyverma](https://github.com/ajeyverma)  
- LinkedIn: [Ajay Verma](https://www.linkedin.com/in/ajeyverma/)  
- Instagram: [@ajayverma](https://instagram.com/ajayverma097)  -->
