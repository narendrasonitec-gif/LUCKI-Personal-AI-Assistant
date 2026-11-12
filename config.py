from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# In a PyInstaller build, load .env from the folder containing Lucki.exe.
# In source mode, load .env from the project folder.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
OWNER_NAME = "Narendra Soni"
