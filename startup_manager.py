"""Windows sign-in startup registration for Lucki AI.

Registers only the current Windows user. It never requests administrator rights.
"""
import os
import sys
from pathlib import Path

APP_NAME = "LuckiAI"
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def startup_command():
    """Return a quoted command that survives spaces in the installation path."""
    if getattr(sys, "frozen", False):
        exe = Path(sys.executable).resolve()
        return f'"{exe}" --background'

    project_dir = Path(__file__).resolve().parent
    python_exe = Path(sys.executable).resolve()
    pythonw = python_exe.with_name("pythonw.exe")
    runner = pythonw if pythonw.exists() else python_exe
    script = project_dir / "main.py"
    return f'"{runner}" "{script}" --background'


def enable_startup():
    """Enable auto-start for the current Windows account."""
    if os.name != "nt":
        return False
    try:
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, startup_command())
        return True
    except Exception as exc:
        print("Startup registration error:", exc)
        return False


def disable_startup():
    """Disable Lucki auto-start for the current Windows account."""
    if os.name != "nt":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
        return True
    except FileNotFoundError:
        return True
    except Exception as exc:
        print("Startup removal error:", exc)
        return False


def startup_enabled():
    if os.name != "nt":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
        return True
    except Exception:
        return False
