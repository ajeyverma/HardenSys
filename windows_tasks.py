import subprocess
import winreg
import ctypes
import os

def enforce_password_history():
    """
    Ensures 'Enforce password history' is set to 24 or more passwords.
    Uses 'net accounts /uniquepw:24' for Windows systems.
    """
    try:
        # Require Admin
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return "⚠️ Please run the tool as Administrator."

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/uniquepw:24"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            return "✅ Password history set to 24 successfully."
        else:
            return f"❌ Failed to set password history: {result.stderr.strip()}"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def check_password_history():
    """
    Checks current 'Enforce password history' setting from registry.
    """
    try:
        key_path = r"SECURITY\Policy\Accounts"
        with winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE) as reg:
            with winreg.OpenKey(reg, key_path) as key:
                value, _ = winreg.QueryValueEx(key, "HistoryLength")
                return f"🔍 Current 'Enforce password history': {value} passwords"
    except FileNotFoundError:
        return "⚠️ Registry path not found. (May need admin access)"
    except Exception as e:
        return f"❌ Error reading registry: {e}"
