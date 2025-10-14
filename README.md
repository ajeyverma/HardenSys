# HardenSys - Unified System Hardening Tool

A comprehensive security policy management and compliance checking tool for Windows and Linux systems. This tool helps organizations and system administrators enforce, manage, and audit security policies through both CLI and GUI interfaces.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Linux](https://img.shields.io/badge/platform-Linux-ff0000)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://ajeyverma.github.io/HardenSys/)

## 🛡️ Features

- **Comprehensive Coverage**: 121 Windows + 89 Linux security parameters
  - **Windows**: Account Policies, User Rights, Security Options, System Settings, Firewall, Audit Policy, Application Guard
  - **Linux**: Filesystem Configuration, Package Management, Services, Network, Access Control, System Hardening

- **Dual Interface**
  - Command-line interface for automation and scripting
  - User-friendly GUI for interactive management

- **Advanced Capabilities**
  - Automatic backup and restore of security policies
  - Detailed HTML and PDF compliance reports
  - Real-time policy status monitoring
  - Batch processing support
  - Cross-platform support (Windows & Linux)

- **Professional Documentation**
  - Complete GitHub Pages documentation
  - Interactive parameter reference
  - Step-by-step setup guides
  - API documentation and examples

## 🚀 Quick Start

### Prerequisites
- Windows 10/11 or Linux (Ubuntu/Debian)
- Python 3.6 or higher
- Administrator/root privileges (recommended)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/AjeyVerma/HardenSys.git
cd HardenSys
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Usage

#### GUI Interface
Run the graphical interface:
```bash
python HardenSys_gui.py
```

#### CLI Interface
Run compliance checks and generate a report:
```bash
# Windows
python HardenSys.py --output report.html

# Linux
python3 HardenSys.py --output report.html
```

## 📚 Documentation

Visit our comprehensive documentation at: **[https://ajeyverma.github.io/HardenSys/docs](https://ajeyverma.github.io/HardenSys/docs)**

### Documentation Features
- **Interactive Parameter Reference**: Search and explore all 210+ security parameters
- **Step-by-Step Guides**: Complete setup instructions for both Windows and Linux
- **API Documentation**: Full CLI and GUI interface documentation
- **Examples & Tutorials**: Real-world usage scenarios and best practices
- **Troubleshooting**: Common issues and solutions

## 📊 Compliance Categories

### Windows (121 Parameters)
1. **Account Policies** (9 parameters)
   - Password policies, account lockout settings, Kerberos authentication

2. **User Rights Assignment** (7 parameters)
   - Administrative privileges, system access controls, security permissions

3. **Security Options** (24 parameters)
   - Network security, User Account Control, system cryptography

4. **System Settings** (32 parameters)
   - Critical service configurations, security-related services

5. **Windows Firewall** (18 parameters)
   - Firewall profiles, connection security, rule management

6. **Advanced Audit Policy** (20 parameters)
   - Account logon, object access, system events

7. **Application Guard** (11 parameters)
   - Microsoft Defender Application Guard settings

### Linux (89 Parameters)
1. **Filesystem Configuration** (16 parameters)
   - Kernel modules, partitions, file system security

2. **Package Management** (7 parameters)
   - Bootloader settings, process hardening

3. **Services Configuration** (21 parameters)
   - Server and client services, time synchronization

4. **Network Configuration** (12 parameters)
   - Network parameters, firewall configuration

5. **Access Control** (21 parameters)
   - SSH, PAM, user account controls

6. **System Hardening** (12 parameters)
   - Additional kernel and system security measures

## 📝 Reports

The tool generates comprehensive compliance reports in multiple formats:
- HTML reports with interactive elements
- PDF reports for formal documentation
- Detailed compliance status for each parameter
- Recommendations for non-compliant settings

## 🔒 Security Considerations

- Always run the tool with administrator privileges
- Create a backup before applying changes
- Review compliance reports thoroughly
- Test in a non-production environment first

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)  
© 2025 [Ajay Kumar](https://github.com/ajeyverma)  
(also known as Ajay Verma / Aarush Chaudhary)

## ⚠️ Disclaimer

This tool is provided **"as is"** without warranty of any kind.  
Use it **at your own risk**. The author is **not responsible** for any damage, data loss, or misconfiguration caused by the use of this tool.

Always test security or system tools in a **safe or virtual environment** before using them on production machines.

<!-- ## 👨‍💻 Author

Developed and maintained by **Ajay Kumar**  
*(also known as **Ajay Verma** / **Aarush Chaudhary** in different communities)*  

- GitHub: [@ajeyverma](https://github.com/ajeyverma)  
- LinkedIn: [Ajay Verma](https://www.linkedin.com/in/ajeyverma/)  
- Instagram: [@ajayverma](https://instagram.com/ajayverma097)  -->
