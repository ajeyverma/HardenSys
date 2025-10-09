import subprocess
import winreg
import ctypes
import os
import tempfile
from pathlib import Path

def enforce_password_history():
    """
    Ensures 'Enforce password history' is set to 24 or more passwords.
    Uses 'net accounts /uniquepw:24' for Windows systems.
    Returns a dictionary with compliance data for proper logging.
    """
    try:
        # Require Admin
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return {
                "status": "error",
                "message": "⚠️ Please run the tool as Administrator.",
                "previous": "Unknown",
                "current": "Unknown"
            }

        # First, check current value using net accounts
        previous_value = "Unknown"
        try:
            result = subprocess.run(
                ["net", "accounts"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0:
                # Parse the output to find password history length
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Length of password history maintained:" in line:
                        # Extract the number from the line
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} passwords"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/uniquepw:24"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied using net accounts again
            current_value = "24 passwords"
            try:
                verify_result = subprocess.run(
                    ["net", "accounts"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if verify_result.returncode == 0:
                    lines = verify_result.stdout.split('\n')
                    for line in lines:
                        if "Length of password history maintained:" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} passwords"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Password history set to 24 successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set password history: {result.stderr.strip()}",
                "previous": previous_value,
                "current": "Failed to apply"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error: {str(e)}",
            "previous": "Unknown",
            "current": "Unknown"
        }


def check_password_history():
    """
    Checks current 'Enforce password history' setting using net accounts.
    Returns a dictionary with compliance data for proper logging.
    """
    try:
        result = subprocess.run(
            ["net", "accounts"],
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode == 0:
            # Parse the output to find password history length
            lines = result.stdout.split('\n')
            for line in lines:
                if "Length of password history maintained:" in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        value = parts[1].strip()
                        current_value = f"{value} passwords"
                        return {
                            "status": "success",
                            "message": f"🔍 Current 'Enforce password history': {current_value}",
                            "previous": "Not applicable (check only)",
                            "current": current_value
                        }
            
            # If we get here, the line wasn't found
            return {
                "status": "error",
                "message": "⚠️ Could not find password history setting in net accounts output",
                "previous": "Unknown",
                "current": "Unknown"
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to run net accounts: {result.stderr.strip()}",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error reading password history: {e}",
            "previous": "Unknown",
            "current": "Unknown"
        }


def backup_password_policy():
    """
    Export current Local Security Policy to an INF using secedit.
    Returns (path, msg). On success: (inf_path, ""). On failure: ("", error_msg).
    """
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return "", "Please run as Administrator."

        # Use repo-local backup directory: <repo>/backup
        repo_root = Path(__file__).resolve().parent
        backup_dir = repo_root / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        import time as _time
        timestamp = _time.strftime("%Y%m%d_%H%M%S")
        inf_path = backup_dir / f"secpol_backup_{timestamp}.inf"

        # Export without specifying /db to avoid "No more data is available" errors
        # Limit to common areas to keep file concise
        cmd = [
            "secedit", "/export",
            "/cfg", str(inf_path),
            "/areas", "SECURITYPOLICY", "USER_RIGHTS",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            return "", f"secedit export failed: {detail}"
        if not inf_path.exists() or inf_path.stat().st_size == 0:
            return "", "Export produced no data (INF is empty)."
        return str(inf_path), ""
    except FileNotFoundError:
        return "", "secedit not found on system PATH."
    except Exception as e:
        return "", f"Error exporting policy: {e}"


def restore_password_policy(inf_path: str):
    """
    Applies a security policy INF using secedit. Returns status message.
    """
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return "⚠️ Please run the tool as Administrator."
        
        if not os.path.exists(inf_path):
            return "❌ Backup INF file not found."
        
        # Check if INF file is valid (not empty)
        if os.path.getsize(inf_path) == 0:
            return "❌ Backup INF file is empty or corrupted."

        tmp_db = Path(tempfile.gettempdir()) / "secpol_apply.sdb"
        log_path = Path(tempfile.gettempdir()) / "secedit_configure.log"
        
        # Clean up any existing temp database
        if tmp_db.exists():
            tmp_db.unlink()
        
        # Run secedit configure command
        cmd = [
            "secedit", "/configure", 
            "/db", str(tmp_db), 
            "/cfg", inf_path, 
            "/overwrite", 
            "/log", str(log_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True,
            timeout=60  # 60 second timeout
        )
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip()
            if "Access is denied" in error_msg:
                return "❌ Access denied. Please run as Administrator and ensure the INF file is not read-only."
            elif "The system cannot find the file specified" in error_msg:
                return "❌ secedit command failed. Please ensure Windows Security Policy tools are available."
            else:
                return f"❌ Failed to apply policy: {error_msg}"
        
        # Check if log file was created and has content
        if log_path.exists() and log_path.stat().st_size > 0:
            return f"✅ Policy applied successfully. Check log: {log_path}\nNote: A reboot or 'gpupdate /force' may be required for changes to take effect."
        else:
            return "✅ Policy applied successfully. A reboot or 'gpupdate /force' may be required for changes to take effect."
            
    except subprocess.TimeoutExpired:
        return "❌ Policy restore timed out. The operation may still be in progress."
    except FileNotFoundError:
        return "❌ secedit not found on system PATH. Please ensure Windows Security Policy tools are installed."
    except Exception as e:
        return f"❌ Error applying policy: {e}"
