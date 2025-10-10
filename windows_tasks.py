import subprocess
import winreg
import ctypes
import os
import tempfile
import re
from pathlib import Path

def is_admin():
    """Check if the current process is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def disable_service(service_name):
    """Helper function to disable a Windows service."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    try:
        # Get current service status
        previous_value = "Unknown"
        try:
            result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                if "STOPPED" in result.stdout:
                    previous_value = "Disabled"
                elif "RUNNING" in result.stdout:
                    previous_value = "Enabled"
                else:
                    previous_value = "Unknown"
            else:
                previous_value = "Not installed"
        except:
            previous_value = "Unknown"
        
        # Disable the service
        subprocess.run(['sc', 'config', service_name, 'start=', 'disabled'], capture_output=True, text=True, shell=True)
        subprocess.run(['sc', 'stop', service_name], capture_output=True, text=True, shell=True)
        
        # Verify the change
        result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            if "STOPPED" in result.stdout:
                current_value = "Disabled"
            else:
                current_value = "Enabled"
        else:
            current_value = "Not installed"
        
        return {
            "status": "success",
            "message": f"Successfully disabled {service_name}",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error disabling {service_name}: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }

def block_microsoft_accounts():
    """
    Configure 'Accounts: Block Microsoft accounts' to prevent users from adding or logging on with Microsoft accounts.
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "NoConnectedUser"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 3 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (3 = Block Microsoft accounts)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 3)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 3:
                return {
                    "status": "success",
                    "message": "✅ Microsoft accounts blocked successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to block Microsoft accounts",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def disable_guest_account():
    """
    Configure 'Accounts: Guest account status' to disable the Guest account.
    """
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current status
        previous_value = "Unknown"
        try:
            result = subprocess.run(['net', 'user', 'Guest'], capture_output=True, text=True)
            previous_value = "Enabled" if "Account active               Yes" in result.stdout else "Disabled"
        except:
            previous_value = "Unknown"
            
        # Disable Guest account
        try:
            subprocess.run(['net', 'user', 'Guest', '/active:no'], check=True, capture_output=True)
            
            # Verify the change
            result = subprocess.run(['net', 'user', 'Guest'], capture_output=True, text=True)
            current_value = "Enabled" if "Account active               Yes" in result.stdout else "Disabled"
            
            if current_value == "Disabled":
                return {
                    "status": "success",
                    "message": "✅ Guest account disabled successfully",
                    "previous": previous_value,
                    "current": current_value
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable Guest account",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error disabling Guest account: {str(e)}",
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

def allow_admin_account_lockout():
    """
    Configure 'Allow administrator account lockout'
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\RemoteAccess\Parameters\AccountLockout"
    value_name = "AdminLockout"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enable admin account lockout)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Administrator account lockout enabled successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to enable administrator account lockout",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def account_lockout_threshold():
    """
    Configure 'Account lockout threshold'
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\RemoteAccess\Parameters\AccountLockout"
    value_name = "MaxDenials"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"{value} invalid logon attempts"
        except:
            previous_value = "Not configured"
            
        # Set new value (5 attempts)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 5)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 5:
                return {
                    "status": "success",
                    "message": "✅ Account lockout threshold set to 5 attempts successfully",
                    "previous": previous_value,
                    "current": "5 invalid logon attempts"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set account lockout threshold",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def account_lockout_duration():
    """
    Configure 'Account lockout duration'
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\RemoteAccess\Parameters\AccountLockout"
    value_name = "ResetTime"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"{value} minutes"
        except:
            previous_value = "Not configured"
            
        # Set new value (30 minutes)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 30)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 30:
                return {
                    "status": "success",
                    "message": "✅ Account lockout duration set to 30 minutes successfully",
                    "previous": previous_value,
                    "current": "30 minutes"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set account lockout duration",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def store_passwords_using_reversible_encryption():
    """
    Configure 'Store passwords using reversible encryption'
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "ClearTextPassword"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (0 = Disabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 0:
                return {
                    "status": "success",
                    "message": "✅ Reversible password encryption disabled successfully",
                    "previous": previous_value,
                    "current": "Disabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable reversible password encryption",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def limit_blank_passwords():
    """
    Configure 'Accounts: Limit local account use of blank passwords to console logon only'
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "LimitBlankPasswordUse"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Blank password restriction enabled successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to enable blank password restriction",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def anonymous_enumeration_sam():
    """
    Configure 'Network access: Do not allow anonymous enumeration of SAM accounts'
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "RestrictAnonymousSAM"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Anonymous SAM enumeration disabled successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable anonymous SAM enumeration",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def rename_administrator_account():
    """
    Configure 'Accounts: Rename administrator account' to a custom name.
    """
    key_path = r"System\CurrentControlSet\Control\SAM"
    value_name = "NewAdministratorName"
    new_name = "SystemAdmin"  # Example name, can be customized
    
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = value
        except:
            previous_value = "Administrator"
            
        # Set new value
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, new_name)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == new_name:
                return {
                    "status": "success",
                    "message": f"✅ Administrator account renamed to '{new_name}' successfully",
                    "previous": previous_value,
                    "current": new_name
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to rename Administrator account",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def message_text_for_logon():
    """Configure 'Interactive logon: Message text for users attempting to log on'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "LegalNoticeText"
    value_data = "This system is for authorized users only. By logging on, you agree to comply with all security policies."
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = value
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Logon message text configured successfully",
                "previous": previous_value,
                "current": value
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to configure logon message text",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def message_title_for_logon():
    """Configure 'Interactive logon: Message title for users attempting to log on'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "LegalNoticeCaption"
    value_data = "Security Notice"
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = value
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Logon message title configured successfully",
                "previous": previous_value,
                "current": value
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to configure logon message title",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def prompt_password_change():
    """Configure 'Interactive logon: Prompt user to change password before expiration'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    value_name = "PasswordExpiryWarning"
    value_data = 14  # Number of days before password expiration to start warning
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = str(value) + " days"
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Password change prompt configured successfully",
                "previous": previous_value,
                "current": str(value) + " days"
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to configure password change prompt",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def anonymous_enumeration_shares():
    """Configure 'Network access: Do not allow anonymous enumeration of SAM accounts and shares'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "RestrictAnonymous"
    value_data = 1  # 1 = Do not allow anonymous enumeration
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = "Enabled" if value == 1 else "Disabled"
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Anonymous enumeration restriction enabled successfully",
                "previous": previous_value,
                "current": "Enabled"
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to enable anonymous enumeration restriction",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def storage_of_passwords():
    """Configure 'Network security: Configure storage of passwords and credentials'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "DisableDomainCreds"
    value_data = 1  # 1 = Do not store passwords and credentials for network authentication
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = "Enabled" if value == 1 else "Disabled"
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Password storage restriction enabled successfully",
                "previous": previous_value,
                "current": "Enabled"
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to enable password storage restriction",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def everyone_permissions_anonymous():
    """Configure 'Network access: Let Everyone permissions apply to anonymous users'."""
    if not ctypes.windll.shell32.IsUserAnAdmin():
        return {
            "status": "error",
            "message": "⚠️ Please run as Administrator",
            "previous": "Unknown",
            "current": "Unknown"
        }
    
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "EveryoneIncludesAnonymous"
    value_data = 0  # 0 = Do not allow Everyone permissions to apply to anonymous users
    
    # Get current value
    previous_value = "Unknown"
    try:
        root = winreg.HKEY_LOCAL_MACHINE
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        previous_value = "Enabled" if value == 1 else "Disabled"
    except:
        previous_value = "Not configured"
    
    # Set new value
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        if value == value_data:
            return {
                "status": "success",
                "message": "✅ Everyone permissions for anonymous users disabled successfully",
                "previous": previous_value,
                "current": "Disabled"
            }
        else:
            return {
                "status": "error",
                "message": "❌ Failed to disable Everyone permissions for anonymous users",
                "previous": previous_value,
                "current": "Failed to apply"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error setting registry value: {str(e)}",
            "previous": previous_value,
            "current": "Failed to apply"
        }

def rename_guest_account():
    """
    Configure 'Accounts: Rename guest account' to rename the built-in Guest account
    """
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current guest account name
        previous_value = "Unknown"
        try:
            result = subprocess.run(['wmic', 'useraccount', 'where', 'sid="S-1-5-21-.*-501"', 'get', 'name'], capture_output=True, text=True)
            previous_value = result.stdout.strip().split('\n')[1].strip()
        except:
            previous_value = "Guest"
            
        # New guest account name
        new_name = "VisitorAccess"
            
        # Rename guest account
        try:
            subprocess.run(['wmic', 'useraccount', 'where', f'name="{previous_value}"', 'call', 'rename', f'name="{new_name}"'], check=True, capture_output=True)
            
            # Verify the change
            result = subprocess.run(['wmic', 'useraccount', 'where', 'sid="S-1-5-21-.*-501"', 'get', 'name'], capture_output=True, text=True)
            current_value = result.stdout.strip().split('\n')[1].strip()
            
            if current_value == new_name:
                        return {
                    "status": "success",
                    "message": "✅ Guest account renamed successfully",
                    "previous": previous_value,
                    "current": current_value
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to rename Guest account",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error renaming Guest account: {str(e)}",
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

def disable_ctrl_alt_del_requirement():
    """
    Configure 'Interactive logon: Do not require CTRL+ALT+DEL' to be disabled
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "DisableCAD"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (0 = Disabled, requiring CTRL+ALT+DEL)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 0:
                return {
                    "status": "success",
                    "message": "✅ CTRL+ALT+DEL requirement enabled successfully",
                    "previous": previous_value,
                    "current": "Disabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to enable CTRL+ALT+DEL requirement",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def hide_last_signed_in():
    """
    Configure 'Interactive logon: Don't display last signed in' to be enabled
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "DontDisplayLastUserName"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled, hiding last signed-in user)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Last signed-in user display disabled successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable last signed-in user display",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def machine_account_lockout_threshold():
    """
    Configure 'Interactive logon: Machine account lockout threshold' to 10 invalid attempts
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "MaxDevicePasswordFailedAttempts"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = str(value)
        except:
            previous_value = "Not configured"
            
        # Set new value (10 attempts)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 10)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 10:
                        return {
                    "status": "success",
                    "message": "✅ Machine account lockout threshold set successfully",
                    "previous": previous_value,
                    "current": "10 attempts"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set machine account lockout threshold",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def machine_inactivity_limit():
    """
    Configure 'Interactive logon: Machine inactivity limit' to 900 seconds (15 minutes)
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "InactivityTimeoutSecs"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"{value} seconds"
        except:
            previous_value = "Not configured"
            
        # Set new value (900 seconds = 15 minutes)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 900)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 900:
                        return {
                    "status": "success",
                    "message": "✅ Machine inactivity limit set successfully",
                    "previous": previous_value,
                    "current": "900 seconds"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set machine inactivity limit",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def idle_time_suspension():
    """
    Configure 'Microsoft network server: Amount of idle time required before suspending session' to 15 minutes
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
    value_name = "AutoDisconnect"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"{value} minutes"
        except:
            previous_value = "Not configured"
            
        # Set new value (15 minutes)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 15)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 15:
                        return {
                    "status": "success",
                    "message": "✅ Server idle time suspension set successfully",
                    "previous": previous_value,
                    "current": "15 minutes"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set server idle time suspension",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def disconnect_expired_clients():
    """
    Configure 'Microsoft network server: Disconnect clients when logon hours expire' to Enabled
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters"
    value_name = "EnableForcedLogoff"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Client disconnection policy set successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to set client disconnection policy",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def anonymous_sid_translation():
    """
    Configure 'Network access: Allow anonymous SID/Name translation' to Disabled
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "TurnOffAnonymousNameLookup"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Disabled" if value == 1 else "Enabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Disabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Anonymous SID/Name translation disabled successfully",
                    "previous": previous_value,
                    "current": "Disabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable anonymous SID/Name translation",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def anonymous_sam_enumeration():
    """
    Configure 'Network access: Do not allow anonymous enumeration of SAM accounts' to Enabled
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "RestrictAnonymousSAM"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ Anonymous SAM enumeration restricted successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to restrict anonymous SAM enumeration",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def configure_kerberos_encryption():
    """
    Configure 'Network security: Configure encryption types allowed for Kerberos' to use only AES encryption types
    """
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Kerberos\Parameters"
    value_name = "SupportedEncryptionTypes"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            # Convert numeric value to encryption types
            encryption_types = []
            if value & 0x1: encryption_types.append("DES_CBC_CRC")
            if value & 0x2: encryption_types.append("DES_CBC_MD5")
            if value & 0x4: encryption_types.append("RC4_HMAC_MD5")
            if value & 0x8: encryption_types.append("AES128_HMAC_SHA1")
            if value & 0x10: encryption_types.append("AES256_HMAC_SHA1")
            previous_value = ", ".join(encryption_types) if encryption_types else "Not configured"
            
        except:
            previous_value = "Not configured"
            
        # Set new value (0x18 = AES128 + AES256 only)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0x18)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 0x18:
                        return {
                    "status": "success",
                    "message": "✅ Kerberos encryption types configured successfully",
                    "previous": previous_value,
                    "current": "AES128_HMAC_SHA1, AES256_HMAC_SHA1"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to configure Kerberos encryption types",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def disable_lan_manager_hash():
    """
    Configure 'Network security: Do not store LAN Manager hash value on next password change' to Enabled
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "NoLMHash"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Enabled)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ LAN Manager hash storage disabled successfully",
                    "previous": previous_value,
                    "current": "Enabled"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to disable LAN Manager hash storage",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

def ldap_client_signing():
    """
    Configure 'Network security: LDAP client signing requirements' to Negotiate signing
    """
    key_path = r"SYSTEM\CurrentControlSet\Services\LDAP"
    value_name = "LDAPClientIntegrity"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            # Convert numeric value to setting name
            if value == 0:
                previous_value = "None"
            elif value == 1:
                previous_value = "Negotiate signing"
            elif value == 2:
                previous_value = "Require signing"
            else:
                previous_value = f"Unknown ({value})"
                
        except:
            previous_value = "Not configured"
            
        # Set new value (1 = Negotiate signing)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 1:
                return {
                    "status": "success",
                    "message": "✅ LDAP client signing requirements configured successfully",
                    "previous": previous_value,
                    "current": "Negotiate signing"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to configure LDAP client signing requirements",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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

    """
    Configure 'Network security: Minimum session security for NTLM SSP based servers'
    to require NTLMv2 and 128-bit encryption
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa\MSV1_0"
    value_name = "NtlmMinServerSec"
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
                    return {
                "status": "error",
                "message": "⚠️ Please run as Administrator",
                "previous": "Unknown",
                "current": "Unknown"
            }
            
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            # Convert numeric value to security requirements
            requirements = []
            if value & 0x20: requirements.append("Require NTLMv2 session security")
            if value & 0x80000000: requirements.append("Require 128-bit encryption")
            previous_value = ", ".join(requirements) if requirements else "None"
            
        except:
            previous_value = "Not configured"
            
        # Set new value (0x80000020 = Require NTLMv2 + 128-bit encryption)
        try:
            key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, 0x80000020)
            winreg.CloseKey(key)
            
            # Verify the change
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            
            if value == 0x80000020:
                        return {
                    "status": "success",
                    "message": "✅ Minimum session security configured successfully",
                    "previous": previous_value,
                    "current": "Require NTLMv2 session security, Require 128-bit encryption"
                }
            else:
                return {
                    "status": "error",
                    "message": "❌ Failed to configure minimum session security",
                    "previous": previous_value,
                    "current": "Failed to apply"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"❌ Error setting registry value: {str(e)}",
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


def maximum_password_age():
    """
    Ensures 'Maximum password age' is set to 90 days.
    Uses 'net accounts /maxpwage:90' for Windows systems.
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
                # Parse the output to find maximum password age
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Maximum password age" in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} days"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/maxpwage:90"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied using net accounts again
            current_value = "90 days"
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
                        if "Maximum password age" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} days"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Maximum password age set to 90 days successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set maximum password age: {result.stderr.strip()}",
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


def minimum_password_age():
    """
    Ensures 'Minimum password age' is set to 1 day.
    Uses 'net accounts /minpwage:1' for Windows systems.
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
                # Parse the output to find minimum password age
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Minimum password age" in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} days"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/minpwage:1"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied using net accounts again
            current_value = "1 day"
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
                        if "Minimum password age" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} days"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Minimum password age set to 1 day successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set minimum password age: {result.stderr.strip()}",
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


def minimum_password_length():
    """
    Ensures 'Minimum password length' is set to 12 characters.
    Uses 'net accounts /minpwlen:12' for Windows systems.
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
                # Parse the output to find minimum password length
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Minimum password length" in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} characters"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/minpwlen:12"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied using net accounts again
            current_value = "12 characters"
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
                        if "Minimum password length" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} characters"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Minimum password length set to 12 characters successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set minimum password length: {result.stderr.strip()}",
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


def password_complexity_requirements():
    """
    Ensures 'Password must meet complexity requirements' is set to 'Enabled'.
    Uses secedit to enable password complexity requirements.
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

        # Create temporary files for secedit operations
        temp_dir = Path(tempfile.gettempdir())
        export_path = temp_dir / "secpol_export.inf"
        db_path = temp_dir / "secpol.sdb"
        log_path = temp_dir / "secedit.log"

        # Clean up any existing temp files
        for path in [export_path, db_path, log_path]:
            if path.exists():
                path.unlink()

        # First, export current policy to check the value
        previous_value = "Unknown"
        try:
            result = subprocess.run(
                ["secedit", "/export", "/cfg", str(export_path), "/areas", "SECURITYPOLICY"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0 and export_path.exists():
                with open(export_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if "PasswordComplexity" in line:
                            value = line.split('=')[1].strip()
                            previous_value = "Enabled" if value == "1" else "Disabled"
                            break
        except:
            previous_value = "Unable to read current value"

        # Create a temporary INF file with the new setting
        policy_inf = """[Unicode]
Unicode=yes
[System Access]
PasswordComplexity = 1
[Version]
signature="$CHICAGO$"
Revision=1
"""
        with open(export_path, 'w') as f:
            f.write(policy_inf)

        # Apply the new policy
        result = subprocess.run(
            [
                "secedit", "/configure",
                "/db", str(db_path),
                "/cfg", str(export_path),
                "/areas", "SECURITYPOLICY",
                "/log", str(log_path)
            ],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied
            current_value = "Enabled"
            try:
                verify_result = subprocess.run(
                    ["secedit", "/export", "/cfg", str(export_path), "/areas", "SECURITYPOLICY"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if verify_result.returncode == 0 and export_path.exists():
                    with open(export_path, 'r') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if "PasswordComplexity" in line:
                                value = line.split('=')[1].strip()
                                current_value = "Enabled" if value == "1" else "Disabled"
                                break
            except:
                current_value = "Applied (unable to verify)"

            # Clean up temp files
            for path in [export_path, db_path, log_path]:
                if path.exists():
                    path.unlink()

            return {
                "status": "success",
                "message": f"✅ Password complexity requirements set to Enabled successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return {
                "status": "error",
                "message": f"❌ Failed to set password complexity requirements: {error_msg}",
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


def store_passwords_using_reversible_encryption():
    """
    Ensures 'Store passwords using reversible encryption' is set to 'Disabled'.
    Uses secedit to disable storing passwords using reversible encryption.
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

        # Create temporary files for secedit operations
        temp_dir = Path(tempfile.gettempdir())
        export_path = temp_dir / "secpol_export.inf"
        db_path = temp_dir / "secpol.sdb"
        log_path = temp_dir / "secedit.log"

        # Clean up any existing temp files
        for path in [export_path, db_path, log_path]:
            if path.exists():
                path.unlink()

        # First, export current policy to check the value
        previous_value = "Unknown"
        try:
            result = subprocess.run(
                ["secedit", "/export", "/cfg", str(export_path), "/areas", "SECURITYPOLICY"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode == 0 and export_path.exists():
                with open(export_path, 'r') as f:
                    content = f.read()
                    for line in content.split('\n'):
                        if "ClearTextPassword" in line:
                            value = line.split('=')[1].strip()
                            previous_value = "Enabled" if value == "1" else "Disabled"
                            break
        except:
            previous_value = "Unable to read current value"

        # Create a temporary INF file with the new setting
        policy_inf = """[Unicode]
Unicode=yes
[System Access]
ClearTextPassword = 0
[Version]
signature="$CHICAGO$"
Revision=1
"""
        with open(export_path, 'w') as f:
            f.write(policy_inf)

        # Apply the new policy
        result = subprocess.run(
            [
                "secedit", "/configure",
                "/db", str(db_path),
                "/cfg", str(export_path),
                "/areas", "SECURITYPOLICY",
                "/log", str(log_path)
            ],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change was applied
            current_value = "Disabled"
            try:
                verify_result = subprocess.run(
                    ["secedit", "/export", "/cfg", str(export_path), "/areas", "SECURITYPOLICY"],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if verify_result.returncode == 0 and export_path.exists():
                    with open(export_path, 'r') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if "ClearTextPassword" in line:
                                value = line.split('=')[1].strip()
                                current_value = "Enabled" if value == "1" else "Disabled"
                                break
            except:
                current_value = "Applied (unable to verify)"

            # Clean up temp files
            for path in [export_path, db_path, log_path]:
                if path.exists():
                    path.unlink()

            return {
                "status": "success",
                "message": f"✅ Store passwords using reversible encryption set to Disabled successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            error_msg = result.stderr.strip() or result.stdout.strip()
            return {
                "status": "error",
                "message": f"❌ Failed to set store passwords using reversible encryption: {error_msg}",
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


def account_lockout_duration():
    """
    Ensures 'Account lockout duration' is set to 15 minutes.
    Uses 'net accounts /lockoutduration:15' for Windows systems.
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
                    if "Lockout duration" in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} minutes"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/lockoutduration:15"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change
            current_value = "15 minutes"
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
                        if "Lockout duration" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} minutes"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Account lockout duration set to 15 minutes successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set account lockout duration: {result.stderr.strip()}",
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


def account_lockout_threshold():
    """
    Ensures 'Account lockout threshold' is set to 5 invalid attempts.
    Uses 'net accounts /lockoutthreshold:5' for Windows systems.
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
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Lockout threshold" in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            value = parts[1].strip()
                            previous_value = f"{value} attempts"
                        break
        except:
            previous_value = "Unable to read current value"

        # Apply policy
        result = subprocess.run(
            ["net", "accounts", "/lockoutthreshold:5"],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change
            current_value = "5 attempts"
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
                        if "Lockout threshold" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                value = parts[1].strip()
                                current_value = f"{value} attempts"
                            break
            except:
                current_value = "Applied (unable to verify)"

            return {
                "status": "success",
                "message": f"✅ Account lockout threshold set to 5 attempts successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to set account lockout threshold: {result.stderr.strip()}",
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


def allow_admin_account_lockout():
    """
    Ensures 'Allow Administrator account lockout' is set to Enabled.
    Uses secedit to modify the security policy.
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

        # First, export current policy to check the value
        previous_value = "Unknown"
        try:
            # Create a temporary file for the current policy
            temp_dir = tempfile.gettempdir()
            current_policy = os.path.join(temp_dir, "current_policy.inf")
            
            # Export current policy
            result = subprocess.run(
                ["secedit", "/export", "/cfg", current_policy],
                capture_output=True,
                text=True,
                shell=True
            )
            
            if result.returncode == 0 and os.path.exists(current_policy):
                with open(current_policy, 'r') as f:
                    policy_content = f.read()
                    # Look for the setting in the policy file
                    if "EnableAdminAccount" in policy_content:
                        previous_value = "Enabled" if "1" in policy_content else "Disabled"
        except:
            previous_value = "Unable to read current value"

        # Create a temporary security policy file
        policy_file = os.path.join(temp_dir, "admin_lockout.inf")
        with open(policy_file, 'w') as f:
            f.write("""[System Access]
EnableAdminAccount = 1
""")

        # Apply the policy
        db_file = os.path.join(temp_dir, "temp.sdb")
        result = subprocess.run(
            ["secedit", "/configure", "/db", db_file, "/cfg", policy_file],
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode == 0:
            # Verify the change
            current_value = "Enabled"
            try:
                verify_result = subprocess.run(
                    ["secedit", "/export", "/cfg", current_policy],
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if verify_result.returncode == 0:
                    with open(current_policy, 'r') as f:
                        policy_content = f.read()
                        if "EnableAdminAccount" in policy_content:
                            current_value = "Enabled" if "1" in policy_content else "Disabled"
            except:
                current_value = "Applied (unable to verify)"

            # Clean up temporary files
            try:
                os.remove(policy_file)
                os.remove(db_file)
                os.remove(current_policy)
            except:
                pass

            return {
                "status": "success",
                "message": f"✅ Administrator account lockout enabled successfully. Previous: {previous_value}, Current: {current_value}",
                "previous": previous_value,
                "current": current_value
            }
        else:
            return {
                "status": "error",
                "message": f"❌ Failed to enable Administrator account lockout: {result.stderr.strip()}",
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


def get_user_rights_assignment(right_name):
    """Helper function to get current user rights assignment."""
    try:
        result = subprocess.run(['secedit', '/export', '/cfg', 'temp.inf'], capture_output=True, text=True)
        if result.returncode != 0:
            return None, f"Failed to export security policy: {result.stderr}"
        
        with open('temp.inf', 'r') as f:
            content = f.read()
        
        os.remove('temp.inf')
        
        pattern = f"{right_name} = (.*)"
        match = re.search(pattern, content)
        if match:
            return match.group(1), None
        return None, "Right not found in security policy"
    except Exception as e:
        return None, str(e)

def set_user_rights_assignment(right_name, users):
    """Helper function to set user rights assignment."""
    try:
        # Export current policy
        result = subprocess.run(['secedit', '/export', '/cfg', 'temp.inf'], capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"Failed to export security policy: {result.stderr}"
        
        # Read and modify the policy
        with open('temp.inf', 'r') as f:
            content = f.readlines()
        
        new_content = []
        found = False
        for line in content:
            if line.startswith(right_name):
                new_content.append(f"{right_name} = {users}\n")
                found = True
            else:
                new_content.append(line)
        
        if not found:
            new_content.append(f"{right_name} = {users}\n")
        
        # Write modified policy
        with open('temp.inf', 'w') as f:
            f.writelines(new_content)
        
        # Import modified policy
        result = subprocess.run(['secedit', '/configure', '/db', 'temp.sdb', '/cfg', 'temp.inf'], capture_output=True, text=True)
        
        # Clean up temporary files
        os.remove('temp.inf')
        if os.path.exists('temp.sdb'):
            os.remove('temp.sdb')
        
        if result.returncode != 0:
            return False, f"Failed to import security policy: {result.stderr}"
        
        return True, None
    except Exception as e:
        return False, str(e)

def access_credential_manager():
    """Set 'Access Credential Manager as a trusted caller' to 'No One'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeTrustedCredManAccessPrivilege"
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, "")
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Change the system time' to 'Administrators, LOCAL SERVICE'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def access_computer_from_network():
    """Set 'Access this computer from the network' to 'Administrators, Remote Desktop Users'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeNetworkLogonRight"
    users = "*S-1-5-32-544,*S-1-5-32-555"  # Administrators, Remote Desktop Users
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Access this computer from the network' to 'Administrators, Remote Desktop Users'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def adjust_memory_quotas():
    """Set 'Adjust memory quotas for a process' to 'Administrators, LOCAL SERVICE, NETWORK SERVICE'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeIncreaseQuotaPrivilege"
    users = "*S-1-5-32-544,*S-1-5-19,*S-1-5-20"  # Administrators, LOCAL SERVICE, NETWORK SERVICE
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Adjust memory quotas for a process' to 'Administrators, LOCAL SERVICE, NETWORK SERVICE'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def allow_logon_locally():
    """Set 'Allow log on locally' to 'Administrators, Users'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeInteractiveLogonRight"
    users = "*S-1-5-32-544,*S-1-5-32-545"  # Administrators, Users
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Allow log on locally' to 'Administrators, Users'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def change_time_zone():
    """Set 'Change the time zone' to 'Administrators, LOCAL SERVICE, Users'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeTimeZonePrivilege"
    users = "*S-1-5-32-544,*S-1-5-19,*S-1-5-32-545"  # Administrators, LOCAL SERVICE, Users
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Change the time zone' to 'Administrators, LOCAL SERVICE, Users'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def change_time_zone():
    """Set 'Change the time zone' to 'Administrators, LOCAL SERVICE, Users'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeTimeZonePrivilege"
    users = "*S-1-5-32-544,*S-1-5-19,*S-1-5-32-545"  # Administrators, LOCAL SERVICE, Users
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Change the time zone' to 'Administrators, LOCAL SERVICE, Users'",
        "previous": previous_value or "Not set",
        "current": current_value
    }


def backup_files_and_directories():
    """Set 'Back up files and directories' to 'Administrators'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeBackupPrivilege"
    users = "*S-1-5-32-544"  # Administrators
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Back up files and directories' to 'Administrators'",
        "previous": previous_value or "Not set",
        "current": current_value
    }

def change_system_time():
    """Set 'Change the system time' to 'Administrators, LOCAL SERVICE'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    right_name = "SeSystemTimePrivilege"
    users = "*S-1-5-32-544,*S-1-5-19"  # Administrators, LOCAL SERVICE
    
    previous_value, error = get_user_rights_assignment(right_name)
    if error:
                return {"status": "error", "message": error, "previous": None, "current": None}
    
    success, error = set_user_rights_assignment(right_name, users)
    if not success:
                return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    current_value, error = get_user_rights_assignment(right_name)
    if error:
        return {"status": "error", "message": error, "previous": previous_value, "current": None}
    
    return {
        "status": "success",
        "message": "Successfully set 'Change the system time' to 'Administrators, LOCAL SERVICE'",
        "previous": previous_value or "Not set",
        "current": current_value
    }



def minimum_session_security_clients():
    """Set 'Network security: Minimum session security for NTLM SSP based clients' to 'Require NTLMv2 session security, Require 128-bit encryption'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "NTLMMinClientSec"
    target_value = 0x20080000  # Require NTLMv2 session security, Require 128-bit encryption
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"0x{value:08X}"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = f"0x{value:08X}"
    
        return {
            "status": "success",
            "message": "Successfully configured minimum session security for NTLM SSP clients",
            "previous": previous_value,
            "current": current_value
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring minimum session security for clients: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def minimum_session_security_servers():
    """Set 'Network security: Minimum session security for NTLM SSP based servers' to 'Require NTLMv2 session security, Require 128-bit encryption'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SYSTEM\CurrentControlSet\Control\Lsa"
    value_name = "NTLMMinServerSec"
    target_value = 0x20080000  # Require NTLMv2 session security, Require 128-bit encryption
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"0x{value:08X}"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = f"0x{value:08X}"
    
        return {
            "status": "success",
            "message": "Successfully configured minimum session security for NTLM SSP servers",
            "previous": previous_value,
            "current": current_value
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring minimum session security for servers: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


# System Settings - User Account Control Functions

def admin_approval_mode_builtin():
    """Set 'User Account Control: Admin Approval Mode for the Built-in Administrator account' to 'Enabled'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "FilterAdministratorToken"
    target_value = 1  # Enabled
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = "Enabled" if value == 1 else "Disabled"
    
        return {
            "status": "success",
            "message": "Successfully enabled Admin Approval Mode for Built-in Administrator",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring Admin Approval Mode: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def elevation_prompt_administrators():
    """Set 'User Account Control: Behaviour of the elevation prompt for administrators in Admin Approval Mode' to 'Prompt for consent on the secure desktop'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "ConsentPromptBehaviorAdmin"
    target_value = 2  # Prompt for consent on the secure desktop
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"Value: {value}"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = f"Value: {value}"
        
        return {
            "status": "success",
            "message": "Successfully configured elevation prompt for administrators",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring elevation prompt for administrators: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def elevation_prompt_standard_users():
    """Set 'User Account Control: Behaviour of the elevation prompt for standard users' to 'Automatically deny elevation requests'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "ConsentPromptBehaviorUser"
    target_value = 0  # Automatically deny elevation requests
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = f"Value: {value}"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = f"Value: {value}"
        
        return {
            "status": "success",
            "message": "Successfully configured elevation prompt for standard users",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring elevation prompt for standard users: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def detect_application_installations():
    """Set 'User Account Control: Detect application installations and prompt for elevation' to 'Enabled'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "EnableInstallerDetection"
    target_value = 1  # Enabled
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = "Enabled" if value == 1 else "Disabled"
        
        return {
            "status": "success",
            "message": "Successfully enabled application installation detection",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring application installation detection: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def run_all_administrators_admin_approval():
    """Set 'User Account Control: Run all administrators in Admin Approval Mode' to 'Enabled'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "EnableLUA"
    target_value = 1  # Enabled
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = "Enabled" if value == 1 else "Disabled"
        
        return {
            "status": "success",
            "message": "Successfully enabled Admin Approval Mode for all administrators",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring Admin Approval Mode: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


def switch_to_secure_desktop():
    """Set 'User Account Control: Switch to the secure desktop when prompting for elevation' to 'Enabled'."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    value_name = "PromptOnSecureDesktop"
    target_value = 1  # Enabled
    
    try:
        # Get current value
        previous_value = "Unknown"
        try:
            root = winreg.HKEY_LOCAL_MACHINE
            key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, value_name)
            winreg.CloseKey(key)
            previous_value = "Enabled" if value == 1 else "Disabled"
        except:
            previous_value = "Not configured"
        
        # Set new value
        key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, target_value)
        winreg.CloseKey(key)
        
        # Verify the change
        key = winreg.OpenKey(root, key_path, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        
        current_value = "Enabled" if value == 1 else "Disabled"
        
        return {
            "status": "success",
            "message": "Successfully enabled secure desktop for elevation prompts",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring secure desktop: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


# System Settings - System Services Functions

def disable_bluetooth_audio_gateway():
    """Disable 'Bluetooth Audio Gateway Service (BTAGService)'."""
    return disable_service("BTAGService")


def disable_bluetooth_support():
    """Disable 'Bluetooth Support Service (bthserv)'."""
    return disable_service("bthserv")


def disable_computer_browser():
    """Disable 'Computer Browser (Browser)'."""
    return disable_service("Browser")


def disable_geolocation_service():
    """Disable 'Geolocation Service (lfsvc)'."""
    return disable_service("lfsvc")


def disable_internet_connection_sharing():
    """Disable 'Internet Connection Sharing (ICS) (SharedAccess)'."""
    return disable_service("SharedAccess")


def disable_remote_desktop_configuration():
    """Disable 'Remote Desktop Configuration (SessionEnv)'."""
    return disable_service("SessionEnv")


def disable_remote_desktop_services():
    """Disable 'Remote Desktop Services (TermService)'."""
    return disable_service("TermService")


def disable_remote_desktop_usermode():
    """Disable 'Remote Desktop Services UserMode Port Redirector (UmRdpService)'."""
    return disable_service("UmRdpService")


def disable_rpc_locator():
    """Disable 'Remote Procedure Call (RPC) Locator (RpcLocator)'."""
    return disable_service("RpcLocator")


def disable_remote_registry():
    """Disable 'Remote Registry (RemoteRegistry)'."""
    return disable_service("RemoteRegistry")


def disable_routing_remote_access():
    """Disable 'Routing and Remote Access (RemoteAccess)'."""
    return disable_service("RemoteAccess")


def disable_simple_tcpip_services():
    """Disable 'Simple TCP/IP Services (simptcp)'."""
    return disable_service("simptcp")


def disable_snmp_service():
    """Disable 'SNMP Service (SNMP)'."""
    return disable_service("SNMP")


def disable_upnp_device_host():
    """Disable 'UPnP Device Host (upnphost)'."""
    return disable_service("upnphost")


def disable_web_management_service():
    """Disable 'Web Management Service (WMSvc)'."""
    return disable_service("WMSvc")


def disable_windows_error_reporting():
    """Disable 'Windows Error Reporting Service (WerSvc)'."""
    return disable_service("WerSvc")


def disable_windows_event_collector():
    """Disable 'Windows Event Collector (Wecsvc)'."""
    return disable_service("Wecsvc")


def disable_wmp_network_sharing():
    """Disable 'Windows Media Player Network Sharing Service (WMPNetworkSvc)'."""
    return disable_service("WMPNetworkSvc")


def disable_windows_mobile_hotspot():
    """Disable 'Windows Mobile Hotspot Service (icssvc)'."""
    return disable_service("icssvc")


def disable_windows_pushtoinstall():
    """Disable 'Windows PushToInstall Service (PushToInstall)'."""
    return disable_service("PushToInstall")


def disable_windows_remote_management():
    """Disable 'Windows Remote Management (WS Management) (WinRM)'."""
    return disable_service("WinRM")


def disable_world_wide_web_publishing():
    """Disable 'World Wide Web Publishing Service (W3SVC)'."""
    return disable_service("W3SVC")


def disable_xbox_accessory_management():
    """Disable 'Xbox Accessory Management Service (XboxGipSvc)'."""
    return disable_service("XboxGipSvc")


def disable_xbox_live_auth_manager():
    """Disable 'Xbox Live Auth Manager (XblAuthManager)'."""
    return disable_service("XblAuthManager")


def disable_xbox_live_game_save():
    """Disable 'Xbox Live Game Save (XblGameSave)'."""
    return disable_service("XblGameSave")


def disable_xbox_live_networking():
    """Disable 'Xbox Live Networking Service (XboxNetApiSvc)'."""
    return disable_service("XboxNetApiSvc")


# Windows Defender Firewall with Advanced Security Functions

def configure_firewall_setting(profile, setting_name, value_type, target_value):
    """Helper function to configure Windows Firewall settings."""
    if not is_admin():
                return {"status": "error", "message": "Administrator privileges required", "previous": None, "current": None}
    
    try:
        # Get current value using netsh
        previous_value = "Unknown"
        try:
            cmd = f'netsh advfirewall {profile} show {setting_name}'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                output = result.stdout
                if value_type == "state":
                    if "ON" in output.upper():
                        previous_value = "On"
                    elif "OFF" in output.upper():
                        previous_value = "Off"
                elif value_type == "action":
                    if "BLOCK" in output.upper():
                        previous_value = "Block"
                    elif "ALLOW" in output.upper():
                        previous_value = "Allow"
                elif value_type == "notification":
                    if "ENABLE" in output.upper():
                        previous_value = "Yes"
                    elif "DISABLE" in output.upper():
                        previous_value = "No"
                elif value_type == "logging":
                    if "ENABLE" in output.upper():
                        previous_value = "Yes"
                    elif "DISABLE" in output.upper():
                        previous_value = "No"
                elif value_type == "size":
                    # Extract size value
                    import re
                    size_match = re.search(r'(\d+)', output)
                    if size_match:
                        previous_value = f"{size_match.group(1)} KB"
                elif value_type == "filename":
                    # Extract filename
                    filename_match = re.search(r'([A-Za-z]:\\[^\\s]+)', output)
                    if filename_match:
                        previous_value = filename_match.group(1)
        except:
            previous_value = "Unknown"
        
        # Set new value using netsh
        if value_type == "state":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        elif value_type == "action":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        elif value_type == "notification":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        elif value_type == "logging":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        elif value_type == "size":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        elif value_type == "filename":
            cmd = f'netsh advfirewall {profile} set {setting_name} {target_value}'
        
        subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        # Verify the change
        try:
            cmd = f'netsh advfirewall {profile} show {setting_name}'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                output = result.stdout
                if value_type == "state":
                    if "ON" in output.upper():
                        current_value = "On"
                    elif "OFF" in output.upper():
                        current_value = "Off"
                elif value_type == "action":
                    if "BLOCK" in output.upper():
                        current_value = "Block"
                    elif "ALLOW" in output.upper():
                        current_value = "Allow"
                elif value_type == "notification":
                    if "ENABLE" in output.upper():
                        current_value = "Yes"
                    elif "DISABLE" in output.upper():
                        current_value = "No"
                elif value_type == "logging":
                    if "ENABLE" in output.upper():
                        current_value = "Yes"
                    elif "DISABLE" in output.upper():
                        current_value = "No"
                elif value_type == "size":
                    import re
                    size_match = re.search(r'(\d+)', output)
                    if size_match:
                        current_value = f"{size_match.group(1)} KB"
                elif value_type == "filename":
                    import re
                    filename_match = re.search(r'([A-Za-z]:\\[^\\s]+)', output)
                    if filename_match:
                        current_value = filename_match.group(1)
            else:
                current_value = "Unknown"
        except:
            current_value = "Unknown"
        
        return {
            "status": "success",
            "message": f"Successfully configured {profile} {setting_name}",
            "previous": previous_value,
            "current": current_value
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error configuring firewall setting: {str(e)}",
            "previous": previous_value if 'previous_value' in locals() else "Unknown",
            "current": "Unknown"
        }


# Private Profile Functions

def firewall_private_state():
    """Set 'Windows Firewall: Private: Firewall state' to 'On (recommended)'."""
    return configure_firewall_setting("private", "state", "state", "on")


def firewall_private_inbound():
    """Set 'Windows Firewall: Private: Inbound connections' to 'Block (default)'."""
    return configure_firewall_setting("private", "firewallpolicy", "action", "blockinbound")


def firewall_private_outbound():
    """Set 'Windows Firewall: Private: Outbound connections' to 'Allow (default)'."""
    return configure_firewall_setting("private", "firewallpolicy", "action", "allowoutbound")


def firewall_private_notification():
    """Set 'Windows Firewall: Private: Settings: Display a notification' to 'No'."""
    return configure_firewall_setting("private", "settings", "notification", "disable")


def firewall_private_logging_name():
    """Set 'Windows Firewall: Private: Logging: Name' to '%SystemRoot%\\System32\\logfiles\\firewall\\privatefw.log'."""
    return configure_firewall_setting("private", "logging", "filename", "%SystemRoot%\\System32\\logfiles\\firewall\\privatefw.log")


def firewall_private_logging_size():
    """Set 'Windows Firewall: Private: Logging: Size limit (KB)' to '16,384 KB or greater'."""
    return configure_firewall_setting("private", "logging", "size", "16384")


def firewall_private_log_dropped():
    """Set 'Windows Firewall: Private: Logging: Log dropped packets' to 'Yes'."""
    return configure_firewall_setting("private", "logging", "logging", "enable")


def firewall_private_log_successful():
    """Set 'Windows Firewall: Private: Logging: Log successful connections' to 'Yes'."""
    return configure_firewall_setting("private", "logging", "logging", "enable")


# Public Profile Functions

def firewall_public_state():
    """Set 'Windows Firewall: Public: Firewall state' to 'On (recommended)'."""
    return configure_firewall_setting("public", "state", "state", "on")


def firewall_public_inbound():
    """Set 'Windows Firewall: Public: Inbound connections' to 'Block (default)'."""
    return configure_firewall_setting("public", "firewallpolicy", "action", "blockinbound")


def firewall_public_outbound():
    """Set 'Windows Firewall: Public: Outbound connections' to 'Allow (default)'."""
    return configure_firewall_setting("public", "firewallpolicy", "action", "allowoutbound")


def firewall_public_notification():
    """Set 'Windows Firewall: Public: Settings: Display a notification' to 'No'."""
    return configure_firewall_setting("public", "settings", "notification", "disable")


def firewall_public_local_rules():
    """Set 'Windows Firewall: Public: Settings: Apply local firewall rules' to 'No'."""
    return configure_firewall_setting("public", "settings", "notification", "disable")


def firewall_public_local_connection_rules():
    """Set 'Windows Firewall: Public: Settings: Apply local connection security rules' to 'No'."""
    return configure_firewall_setting("public", "settings", "notification", "disable")


def firewall_public_logging_name():
    """Set 'Windows Firewall: Public: Logging: Name' to '%SystemRoot%\\System32\\logfiles\\firewall\\publicfw.log'."""
    return configure_firewall_setting("public", "logging", "filename", "%SystemRoot%\\System32\\logfiles\\firewall\\publicfw.log")


def firewall_public_logging_size():
    """Set 'Windows Firewall: Public: Logging: Size limit (KB)' to '16,384 KB or greater'."""
    return configure_firewall_setting("public", "logging", "size", "16384")


def firewall_public_log_dropped():
    """Set 'Windows Firewall: Public: Logging: Log dropped packets' to 'Yes'."""
    return configure_firewall_setting("public", "logging", "logging", "enable")


def firewall_public_log_successful():
    """Set 'Windows Firewall: Public: Logging: Log successful connections' to 'Yes'."""
    return configure_firewall_setting("public", "logging", "logging", "enable")


# Advanced Audit Policy Configuration Functions

def audit_credential_validation():
    """Set 'Audit Credential Validation' to 'Success and Failure'."""
    try:
        # Use auditpol to configure credential validation auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Logon", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Credential Validation set to Success and Failure"
        else:
            return f"✗ Failed to set Audit Credential Validation: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Credential Validation: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_application_group_management():
    """Set 'Audit Application Group Management' to 'Success and Failure'."""
    try:
        # Use auditpol to configure application group management auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Application Group Management", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Application Group Management set to Success and Failure"
        else:
            return f"✗ Failed to set Audit Application Group Management: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Application Group Management: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_security_group_management():
    """Set 'Audit Security Group Management' to include 'Success'."""
    try:
        # Use auditpol to configure security group management auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Security Group Management", "/success:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Security Group Management set to Success"
        else:
            return f"✗ Failed to set Audit Security Group Management: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Security Group Management: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_user_account_management():
    """Set 'Audit User Account Management' to 'Success and Failure'."""
    try:
        # Use auditpol to configure user account management auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:User Account Management", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit User Account Management set to Success and Failure"
        else:
            return f"✗ Failed to set Audit User Account Management: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit User Account Management: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_pnp_activity():
    """Set 'Audit PNP Activity' to include 'Success'."""
    try:
        # Use auditpol to configure PNP activity auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Plug and Play Events", "/success:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit PNP Activity set to Success"
        else:
            return f"✗ Failed to set Audit PNP Activity: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit PNP Activity: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_process_creation():
    """Set 'Audit Process Creation' to include 'Success'."""
    try:
        # Use auditpol to configure process creation auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Process Creation", "/success:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Process Creation set to Success"
        else:
            return f"✗ Failed to set Audit Process Creation: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Process Creation: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_account_lockout():
    """Set 'Audit Account Lockout' to include 'Failure'."""
    try:
        # Use auditpol to configure account lockout auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Account Lockout", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Account Lockout set to Failure"
        else:
            return f"✗ Failed to set Audit Account Lockout: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Account Lockout: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_other_logon_logoff_events():
    """Set 'Audit Other Logon/Logoff Events' to 'Success and Failure'."""
    try:
        # Use auditpol to configure other logon/logoff events auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Other Logon/Logoff Events", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Other Logon/Logoff Events set to Success and Failure"
        else:
            return f"✗ Failed to set Audit Other Logon/Logoff Events: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Other Logon/Logoff Events: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_file_share():
    """Set 'Audit File Share' to 'Success and Failure'."""
    try:
        # Use auditpol to configure file share auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:File Share", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit File Share set to Success and Failure"
        else:
            return f"✗ Failed to set Audit File Share: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit File Share: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_removable_storage():
    """Set 'Audit Removable Storage' to 'Success and Failure'."""
    try:
        # Use auditpol to configure removable storage auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Removable Storage", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Removable Storage set to Success and Failure"
        else:
            return f"✗ Failed to set Audit Removable Storage: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Removable Storage: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_audit_policy_change():
    """Set 'Audit Audit Policy Change' to include 'Success'."""
    try:
        # Use auditpol to configure audit policy change auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Audit Policy Change", "/success:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Audit Policy Change set to Success"
        else:
            return f"✗ Failed to set Audit Audit Policy Change: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Audit Policy Change: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_other_policy_change_events():
    """Set 'Audit Other Policy Change Events' to include 'Failure'."""
    try:
        # Use auditpol to configure other policy change events auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Other Policy Change Events", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Other Policy Change Events set to Failure"
        else:
            return f"✗ Failed to set Audit Other Policy Change Events: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Other Policy Change Events: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_sensitive_privilege_use():
    """Set 'Audit Sensitive Privilege Use' to 'Success and Failure'."""
    try:
        # Use auditpol to configure sensitive privilege use auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:Sensitive Privilege Use", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit Sensitive Privilege Use set to Success and Failure"
        else:
            return f"✗ Failed to set Audit Sensitive Privilege Use: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit Sensitive Privilege Use: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def audit_system_integrity():
    """Set 'Audit System Integrity' to 'Success and Failure'."""
    try:
        # Use auditpol to configure system integrity auditing
        result = subprocess.run([
            "auditpol", "/set", "/subcategory:System Integrity", "/success:enable", "/failure:enable"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Audit System Integrity set to Success and Failure"
        else:
            return f"✗ Failed to set Audit System Integrity: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Audit System Integrity: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def prevent_enabling_lock_screen_camera():
    """Set 'Prevent enabling lock screen camera' to 'Enabled'."""
    try:
        # Use reg add to set the registry value
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\Personalization",
            "/v", "NoLockScreenCamera", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Prevent enabling lock screen camera set to Enabled"
        else:
            return f"✗ Failed to set Prevent enabling lock screen camera: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Prevent enabling lock screen camera: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def configure_smb_v1_client_driver():
    """Set 'Configure SMB v1 client driver' to 'Enabled: Disable driver (recommended)'."""
    try:
        # Use reg add to disable SMB v1 client driver
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\mrxsmb10",
            "/v", "Start", "/t", "REG_DWORD", "/d", "4", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Configure SMB v1 client driver set to Disabled"
        else:
            return f"✗ Failed to set Configure SMB v1 client driver: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Configure SMB v1 client driver: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def configure_smb_v1_server():
    """Set 'Configure SMB v1 server' to 'Disabled'."""
    try:
        # Use reg add to disable SMB v1 server
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Services\\LanmanServer\\Parameters",
            "/v", "SMB1", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Configure SMB v1 server set to Disabled"
        else:
            return f"✗ Failed to set Configure SMB v1 server: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Configure SMB v1 server: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def disallow_autoplay_non_volume_devices():
    """Set 'Disallow Autoplay for non-volume devices' to 'Enabled'."""
    try:
        # Use reg add to disable autoplay for non-volume devices
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\Explorer",
            "/v", "NoAutoplayfornonVolume", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Disallow Autoplay for non-volume devices set to Enabled"
        else:
            return f"✗ Failed to set Disallow Autoplay for non-volume devices: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Disallow Autoplay for non-volume devices: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def set_default_behavior_autorun():
    """Set 'Set the default behaviour for AutoRun' to 'Enabled: Do not execute any autorun commands'."""
    try:
        # Use reg add to disable autorun commands
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
            "/v", "NoAutorun", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Set default behaviour for AutoRun set to Do not execute any autorun commands"
        else:
            return f"✗ Failed to set Set default behaviour for AutoRun: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Set default behaviour for AutoRun: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def turn_off_autoplay():
    """Set 'Turn off Autoplay' to 'Enabled: All drives'."""
    try:
        # Use reg add to turn off autoplay for all drives
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer",
            "/v", "NoDriveTypeAutoRun", "/t", "REG_DWORD", "/d", "255", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Turn off Autoplay set to All drives"
        else:
            return f"✗ Failed to set Turn off Autoplay: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Turn off Autoplay: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def allow_auditing_events_appguard():
    """Set 'Allow auditing events in Microsoft Defender Application Guard' to 'Enabled'."""
    try:
        # Use reg add to enable auditing events in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowAuditingEvents", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Allow auditing events in Microsoft Defender Application Guard set to Enabled"
        else:
            return f"✗ Failed to set Allow auditing events in Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Allow auditing events in Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def allow_camera_microphone_access_appguard():
    """Set 'Allow camera and microphone access in Microsoft Defender Application Guard' to 'Disabled'."""
    try:
        # Use reg add to disable camera and microphone access in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowCameraMicrophoneRedirection", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Allow camera and microphone access in Microsoft Defender Application Guard set to Disabled"
        else:
            return f"✗ Failed to set Allow camera and microphone access in Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Allow camera and microphone access in Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def allow_data_persistence_appguard():
    """Set 'Allow data persistence for Microsoft Defender Application Guard' to 'Disabled'."""
    try:
        # Use reg add to disable data persistence in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowPersistence", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Allow data persistence for Microsoft Defender Application Guard set to Disabled"
        else:
            return f"✗ Failed to set Allow data persistence for Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Allow data persistence for Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def allow_file_download_host_os_appguard():
    """Set 'Allow files to download and save to the host operating system from Microsoft Defender Application Guard' to 'Disabled'."""
    try:
        # Use reg add to disable file download to host OS in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowFileDownload", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Allow files to download and save to the host operating system from Microsoft Defender Application Guard set to Disabled"
        else:
            return f"✗ Failed to set Allow files to download and save to the host operating system from Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Allow files to download and save to the host operating system from Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def configure_clipboard_settings_appguard():
    """Set 'Configure Microsoft Defender Application Guard clipboard settings: Clipboard behaviour setting' to 'Enabled: Enable clipboard operation from an isolated session to the host'."""
    try:
        # Use reg add to configure clipboard settings in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "ClipboardFileRedirectionAllowed", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Configure Microsoft Defender Application Guard clipboard settings set to Enable clipboard operation from an isolated session to the host"
        else:
            return f"✗ Failed to set Configure Microsoft Defender Application Guard clipboard settings: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Configure Microsoft Defender Application Guard clipboard settings: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def allow_virtual_gpu_appguard():
    """Set 'Allow virtual GPU in Microsoft Defender Application Guard' to 'Disabled'."""
    try:
        # Use reg add to disable virtual GPU in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowVirtualGPU", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Allow virtual GPU in Microsoft Defender Application Guard set to Disabled"
        else:
            return f"✗ Failed to set Allow virtual GPU in Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Allow virtual GPU in Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def block_non_enterprise_content_appguard():
    """Set 'Block non-enterprise content in Microsoft Defender Application Guard' to 'Enabled'."""
    try:
        # Use reg add to enable blocking non-enterprise content in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "BlockNonEnterpriseContent", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Block non-enterprise content in Microsoft Defender Application Guard set to Enabled"
        else:
            return f"✗ Failed to set Block non-enterprise content in Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Block non-enterprise content in Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def configure_clipboard_file_types_appguard():
    """Set 'Configure Microsoft Defender Application Guard clipboard file types' to 'Enabled: Allow only text'."""
    try:
        # Use reg add to configure clipboard file types in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "ClipboardFileType", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Configure Microsoft Defender Application Guard clipboard file types set to Allow only text"
        else:
            return f"✗ Failed to set Configure Microsoft Defender Application Guard clipboard file types: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Configure Microsoft Defender Application Guard clipboard file types: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def configure_printing_settings_appguard():
    """Set 'Configure Microsoft Defender Application Guard printing settings' to 'Disabled'."""
    try:
        # Use reg add to disable printing in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "PrintingSettings", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Configure Microsoft Defender Application Guard printing settings set to Disabled"
        else:
            return f"✗ Failed to set Configure Microsoft Defender Application Guard printing settings: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Configure Microsoft Defender Application Guard printing settings: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def save_files_to_host_appguard():
    """Set 'Save files to host from Microsoft Defender Application Guard' to 'Disabled'."""
    try:
        # Use reg add to disable saving files to host in Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "SaveFilesToHost", "/t", "REG_DWORD", "/d", "0", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Save files to host from Microsoft Defender Application Guard set to Disabled"
        else:
            return f"✗ Failed to set Save files to host from Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Save files to host from Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"


def enable_windows_defender_application_guard():
    """Set 'Microsoft Defender Application Guard' to 'Enabled'."""
    try:
        # Use reg add to enable Microsoft Defender Application Guard
        result = subprocess.run([
            "reg", "add", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Policies\\Microsoft\\Windows\\AppHVSI",
            "/v", "AllowWindowsDefenderApplicationGuard", "/t", "REG_DWORD", "/d", "1", "/f"
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            return "✓ Microsoft Defender Application Guard set to Enabled"
        else:
            return f"✗ Failed to set Microsoft Defender Application Guard: {result.stderr}"
    except subprocess.CalledProcessError as e:
        return f"✗ Error setting Microsoft Defender Application Guard: {e.stderr}"
    except Exception as e:
        return f"✗ Unexpected error: {str(e)}"
