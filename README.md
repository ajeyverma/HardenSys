# HardenSys - Unified System Hardening Tool

A comprehensive security policy management and compliance checking tool for Windows systems. This tool helps organizations and system administrators enforce, manage, and audit Windows security policies through both CLI and GUI interfaces.

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Python](https://img.shields.io/badge/python-3.6%2B-brightgreen.svg)

## 🛡️ Features

- **Comprehensive Coverage**: 121 security parameters across multiple categories
  - Account Policies (9 parameters)
  - User Rights (7 parameters)
  - Security Options (24 parameters)
  - System Settings (32 parameters)
  - Windows Firewall (18 parameters)
  - Audit Policy (20 parameters)
  - Application Guard (11 parameters)

- **Dual Interface**
  - Command-line interface for automation and scripting
  - User-friendly GUI for interactive management

- **Advanced Capabilities**
  - Automatic backup and restore of security policies
  - Detailed HTML and PDF compliance reports
  - Real-time policy status monitoring
  - Batch processing support

## 🚀 Quick Start

### Prerequisites
- Windows Operating System
- Python 3.6 or higher
- Administrator privileges

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
python HardenSys.py --output report.html
```

## 📊 Compliance Categories

1. **Account Policies**
   - Password policies
   - Account lockout settings
   - Kerberos authentication

2. **User Rights Assignment**
   - Administrative privileges
   - System access controls
   - Security permissions

3. **Security Options**
   - Network security
   - User Account Control
   - System cryptography

4. **System Services**
   - Critical service configurations
   - Security-related services
   - Network services

5. **Windows Firewall**
   - Firewall profiles
   - Connection security
   - Rule management

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

<!-- ## 👨‍💻 Author

Developed and maintained by **Ajay Kumar**  
*(also known as **Ajay Verma** / **Aarush Chaudhary** in different communities)*  

- GitHub: [@ajeyverma](https://github.com/ajeyverma)  
- LinkedIn: [Ajay Verma](https://www.linkedin.com/in/ajeyverma/)  
- Instagram: [@ajayverma](https://instagram.com/ajayverma097)  -->
