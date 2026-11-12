import os
import re
import json
import shutil
import subprocess
import urllib.parse
import webbrowser
import ctypes
from pathlib import Path

from computer_control import (
    browser_back,
    browser_forward,
    close_window,
    maximize_window,
    minimize_window,
    mute,
    page_down,
    page_up,
    play_video,
    scroll_down,
    scroll_up,
    switch_window,
    type_text,
    volume_down,
    volume_up,
)

from phone_link import open_phone, answer_call, reject_call


# =========================================================
# BASIC HELPERS
# =========================================================

def open_url(url):
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        print("Browser error:", e)
        return False


def contains_any(text, phrases):
    return any(p in text for p in phrases)


# =========================================================
# WINDOWS APP LAUNCHER
# =========================================================

def _get_start_menu_apps():
    """Return installed Start-menu app names and AppIDs without shell interpolation."""
    try:
        script = "Get-StartApps | Select-Object Name,AppID | ConvertTo-Json -Compress"
        result = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True, text=True, timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        data = json.loads(result.stdout)
        if isinstance(data, dict):
            data = [data]
        return [item for item in data if isinstance(item, dict) and item.get("Name") and item.get("AppID")]
    except Exception as e:
        print("Start-menu app scan error:", e)
        return []


def open_windows_app(app_name):
    """Open an installed Windows app by Start-menu name, allowing exact or partial matches."""
    wanted = re.sub(r"[^a-z0-9]+", "", app_name.lower())
    if not wanted:
        return False
    try:
        candidates = []
        wanted_tokens = set(re.findall(r"[a-z0-9]+", app_name.lower()))
        for item in _get_start_menu_apps():
            name = str(item.get("Name", ""))
            normalized = re.sub(r"[^a-z0-9]+", "", name.lower())
            if normalized == wanted:
                score = 0
            elif wanted in normalized or normalized in wanted:
                score = 1
            else:
                name_tokens = set(re.findall(r"[a-z0-9]+", name.lower()))
                if wanted_tokens and wanted_tokens.issubset(name_tokens):
                    score = 2
                else:
                    continue
            candidates.append((score, len(name), name, str(item["AppID"])))
        if candidates:
            candidates.sort()
            app_id = candidates[0][3]
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"], shell=False)
            return True
        executable = shutil.which(app_name)
        if executable:
            subprocess.Popen([executable], shell=False)
            return True
    except Exception as e:
        print(f"{app_name} app launch error:", e)
    return False


def _launch_requested_installed_app(command_text):
    """Interpret common English/Hinglish launch phrases and open a matching installed app."""
    raw = command_text.lower().strip().strip(" .,!?")
    prefixes = ("please open ", "please launch ", "please start ", "open ", "launch ", "start ", "run ", "open the ", "launch the ", "start the ")
    target = None
    for prefix in prefixes:
        if raw.startswith(prefix):
            target = raw[len(prefix):].strip()
            break
    if target is None:
        patterns = (
            r"^(.+?)\s+(?:ko\s+)?(?:khol do|kholo|khol|open karo|launch karo|start karo|chalao|chala do)$",
            r"^(?:lucki\s+)?(.+?)\s+(?:open|launch|start)(?:\s+(?:please|now))?$",
        )
        for pattern in patterns:
            match = re.match(pattern, raw)
            if match:
                target = match.group(1).strip()
                break
    if not target:
        return None
    target = re.sub(r"^(the|app|application)\s+", "", target).strip()
    target = re.sub(r"\s+(app|application|software)$", "", target).strip()
    if not target or len(target) > 80:
        return None
    if target in {"google", "youtube", "gmail", "facebook", "instagram", "whatsapp web"}:
        return None
    if open_windows_app(target):
        return f"{target.title()} open kar raha hoon."
    return None

# =========================================================
# WHATSAPP
# APP FIRST → WEB FALLBACK
# =========================================================

def open_whatsapp():
    """
    Priority:
    1. Installed WhatsApp Desktop
    2. WhatsApp Web in default browser
    """

    # First try installed Windows app
    if open_windows_app("WhatsApp"):
        return True

    # If desktop app is unavailable, open WhatsApp Web
    return open_url("https://web.whatsapp.com")


# =========================================================
# MAIN COMMAND EXECUTOR
# =========================================================

def execute_command(command):

    if not command:
        return None

    original = command.strip()
    c = original.lower().strip()

    # =====================================================
    # BASIC HINGLISH NORMALIZATION
    # =====================================================

    replacements = {
        "khol do": "open ",
        "kholo": "open ",
        "khol": "open ",
    }

    for old, new in replacements.items():
        c = c.replace(old, new)

    # =====================================================
    # WINDOW / DESKTOP CONTROL
    # =====================================================

    if contains_any(
        c,
        [
            "switch window",
            "switch app",
            "change window",
            "next window"
        ]
    ):
        return (
            "Switching window."
            if switch_window()
            else "Window switching is unavailable."
        )

    if contains_any(
        c,
        [
            "minimize window",
            "minimise window",
            "minimize this",
            "minimise this"
        ]
    ):
        return (
            "Minimizing the current window."
            if minimize_window()
            else "I couldn't minimize the window."
        )

    if contains_any(
        c,
        [
            "maximize window",
            "maximise window",
            "maximize this",
            "maximise this"
        ]
    ):
        return (
            "Maximizing the current window."
            if maximize_window()
            else "I couldn't maximize the window."
        )

    if contains_any(
        c,
        [
            "close window",
            "close this window",
            "close current window"
        ]
    ):
        return (
            "Closing the current window."
            if close_window()
            else "I couldn't close the window."
        )

    if contains_any(
        c,
        [
            "go back",
            "browser back",
            "back page",
            "back karo"
        ]
    ):
        return (
            "Going back."
            if browser_back()
            else "I couldn't go back."
        )

    if contains_any(
        c,
        [
            "go forward",
            "browser forward",
            "forward page",
            "forward karo"
        ]
    ):
        return (
            "Going forward."
            if browser_forward()
            else "I couldn't go forward."
        )

    # =====================================================
    # SCROLL / PAGE
    # =====================================================

    if contains_any(
        c,
        [
            "scroll down",
            "neeche scroll",
            "scroll neeche"
        ]
    ):
        return (
            "Scrolling down."
            if scroll_down()
            else "Scroll control is unavailable."
        )

    if contains_any(
        c,
        [
            "scroll up",
            "upar scroll",
            "scroll upar"
        ]
    ):
        return (
            "Scrolling up."
            if scroll_up()
            else "Scroll control is unavailable."
        )

    if contains_any(
        c,
        [
            "page down",
            "next page"
        ]
    ):
        return (
            "Moving down a page."
            if page_down()
            else "Page control is unavailable."
        )

    if contains_any(
        c,
        [
            "page up",
            "previous page"
        ]
    ):
        return (
            "Moving up a page."
            if page_up()
            else "Page control is unavailable."
        )

    # =====================================================
    # MEDIA
    # =====================================================

    if contains_any(
        c,
        [
            "pause video",
            "video pause",
            "pause it",
            "pause karo"
        ]
    ):
        return (
            "Pausing the video."
            if play_video()
            else "Media control is unavailable."
        )

    if contains_any(
        c,
        [
            "play video",
            "video play",
            "play it",
            "play karo"
        ]
    ):
        return (
            "Playing the video."
            if play_video()
            else "Media control is unavailable."
        )

    if contains_any(
        c,
        [
            "next video",
            "next track",
            "skip video"
        ]
    ):
        from computer_control import media_next

        return (
            "Moving to the next item."
            if media_next()
            else "Media control is unavailable."
        )

    if contains_any(
        c,
        [
            "previous video",
            "previous track",
            "previous song"
        ]
    ):
        from computer_control import media_previous

        return (
            "Going to the previous item."
            if media_previous()
            else "Media control is unavailable."
        )

    # =====================================================
    # VOLUME
    # =====================================================

    if contains_any(
        c,
        [
            "volume up",
            "increase volume",
            "volume badhao",
            "volume badao",
            "awaz badhao"
        ]
    ):
        return (
            "Increasing the volume."
            if volume_up()
            else "Volume control is unavailable."
        )

    if contains_any(
        c,
        [
            "volume down",
            "decrease volume",
            "volume kam",
            "awaz kam karo"
        ]
    ):
        return (
            "Decreasing the volume."
            if volume_down()
            else "Volume control is unavailable."
        )

    if contains_any(
        c,
        [
            "mute",
            "mute volume",
            "volume mute",
            "awaz band"
        ]
    ):
        return (
            "Muting the volume."
            if mute()
            else "Volume control is unavailable."
        )

    # =====================================================
    # PERSONAL CONTACT CALLING (Windows tel: handler / Phone Link)
    # =====================================================

    if contains_any(c, ["call papa", "papa ko call", "papa ko phone", "phone papa", "papa ko phone karo", "call dad", "dad ko call"]):
        number = os.getenv("LUCKI_PAPA_PHONE", "").strip()
        if not number:
            return ("Papa ko call karne ke liye .env file mein LUCKI_PAPA_PHONE=+91XXXXXXXXXX set karo. "
                    "Phone Link ya Windows ka tel: calling app bhi configured hona chahiye.")
        number = re.sub(r"[^0-9+]", "", number)
        if not number or number in {"+", "91", "+91"}:
            return "Papa ka phone number .env mein sahi format mein set nahi hai."
        try:
            if os.name == "nt":
                os.startfile("tel:" + number)
            else:
                webbrowser.open("tel:" + number)
            return "Papa ka calling screen khol diya hai. Phone Link/Windows prompt par call confirm kar do agar poochhe."
        except Exception as e:
            print("Contact call error:", e)
            return "Calling screen open nahi hua. Phone Link pairing aur Windows tel: app check karo."

    # =====================================================
    # PHONE LINK
    # =====================================================

    if contains_any(
        c,
        [
            "open phone link",
            "phone link kholo",
            "phone link open",
            "phone kholo"
        ]
    ):
        return (
            "Opening Phone Link."
            if open_phone()
            else "I couldn't open Phone Link."
        )

    if contains_any(
        c,
        [
            "answer call",
            "pick up call",
            "call utha",
            "call uthao",
            "utha lo",
            "receive call"
        ]
    ):
        return (
            "Answering the call."
            if answer_call()
            else "I couldn't control the call."
        )

    if contains_any(
        c,
        [
            "reject call",
            "decline call",
            "cut the call",
            "call kaat",
            "call kato",
            "call kaat do",
            "ignore call",
            "ignore karo"
        ]
    ):
        return (
            "Rejecting the call."
            if reject_call()
            else "I couldn't control the call."
        )

    # =====================================================
    # WHATSAPP
    # APP FIRST → WEB FALLBACK
    # =====================================================

    whatsapp_commands = [
        "whatsapp",
        "open whatsapp",
        "launch whatsapp",
        "start whatsapp",
        "whatsapp kholo",
        "whatsapp open",
        "whatsapp khol",
        "whatsapp chalao",
    ]

    if c in whatsapp_commands:
        if open_whatsapp():
            return "WhatsApp khol raha hoon."
        return "WhatsApp open nahi ho paya."

    # =====================================================
    # WEBSITES
    # =====================================================

    sites = {
        "chrome": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "chatgpt": "https://chatgpt.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "linkedin": "https://www.linkedin.com",
        "instagram": "https://www.instagram.com",
    }

    for name, url in sites.items():

        if c in (
            name,
            f"open {name}",
            f"launch {name}",
            f"start {name}"
        ):
            return (
                f"Opening {name.title()}."
                if open_url(url)
                else f"I couldn't open {name.title()}."
            )

    # =====================================================
    # GOOGLE SEARCH
    # =====================================================

    patterns = [
        r"^search (.+)$",
        r"^google (.+)$",
        r"^search for (.+)$",
        r"^google search (.+)$",
    ]

    for pattern in patterns:

        m = re.match(pattern, c)

        if m:
            query = m.group(1).strip()

            url = (
                "https://www.google.com/search?q="
                + urllib.parse.quote(query)
            )

            return (
                f"Searching Google for {query}."
                if open_url(url)
                else "I couldn't open Google."
            )

    # =====================================================
    # YOUTUBE SEARCH / PLAY
    # =====================================================

    youtube_patterns = [
        r"^play (.+?) on youtube$",
        r"^play (.+?) youtube$",
        r"^search (.+?) on youtube$",
        r"^youtube (.+)$",
        r"^youtube par (.+)$",
    ]

    for pattern in youtube_patterns:

        m = re.match(pattern, c)

        if m:

            query = m.group(1).strip()

            url = (
                "https://www.youtube.com/results?search_query="
                + urllib.parse.quote(query)
            )

            return (
                f"YouTube par {query} search kar raha hoon."
                if open_url(url)
                else "I couldn't open YouTube."
            )

    # =====================================================
    # APPLICATIONS
    # =====================================================

    apps = {
        "notepad": "notepad",
        "calculator": "calc",
        "calc": "calc",
        "paint": "mspaint",
        "cmd": "cmd",
        "powershell": "powershell",
        "task manager": "taskmgr",
        "control panel": "control",
        "device manager": "devmgmt.msc",
        "word": "winword",
        "excel": "excel",
        "powerpoint": "powerpnt",
    }

    for name, exe in apps.items():

        if c in (
            name,
            f"open {name}",
            f"launch {name}",
            f"start {name}"
        ):

            try:

                subprocess.Popen(
                    exe,
                    shell=True
                )

                return f"Opening {name.title()}."

            except Exception:

                return f"{name.title()} was not found."

    # =====================================================
    # VS CODE
    # =====================================================

    if (
        "vs code" in c
        or "visual studio code" in c
        or c in ("code", "open code")
    ):

        try:

            subprocess.Popen(
                "code",
                shell=True
            )

            return "Opening VS Code."

        except Exception:

            return "VS Code was not found."

    # =====================================================
    # ANY INSTALLED START-MENU APP (natural English/Hinglish)
    # =====================================================

    app_result = _launch_requested_installed_app(original)
    if app_result:
        return app_result

    # =====================================================
    # FOLDERS
    # =====================================================

    folders = {
        "desktop": "Desktop",
        "downloads": "Downloads",
        "documents": "Documents",
        "pictures": "Pictures",
        "videos": "Videos",
    }

    for name, folder in folders.items():

        if c in (
            name,
            f"open {name}",
            f"launch {name}"
        ):

            path = Path.home() / folder

            try:

                subprocess.Popen(
                    f'explorer "{path}"',
                    shell=True
                )

                return f"Opening {name.title()}."

            except Exception:

                return f"Couldn't open {name.title()}."

    # =====================================================
    # THIS PC
    # =====================================================

    if c in (
        "this pc",
        "open this pc",
        "my computer",
        "open my computer"
    ):

        subprocess.Popen(
            "explorer shell:MyComputerFolder",
            shell=True
        )

        return "Opening This PC."

    # =====================================================
    # RECYCLE BIN
    # =====================================================

    if "recycle bin" in c:

        subprocess.Popen(
            "explorer.exe shell:RecycleBinFolder",
            shell=True
        )

        return "Opening Recycle Bin."

    # =====================================================
    # WINDOWS SETTINGS
    # =====================================================

    if c in (
        "settings",
        "open settings",
        "windows settings"
    ):

        subprocess.Popen(
            "start ms-settings:",
            shell=True
        )

        return "Opening Windows Settings."

    # =====================================================
    # CAMERA
    # =====================================================

    if (
        c == "camera"
        or c == "open camera"
        or "camera kholo" in c
    ):

        subprocess.Popen(
            "start microsoft.windows.camera:",
            shell=True
        )

        return "Opening Camera."

    # =====================================================
    # POWER
    # =====================================================

    if c in (
        "lock",
        "lock pc",
        "lock computer",
        "computer lock",
        "pc lock"
    ):

        subprocess.Popen(
            "rundll32.exe user32.dll,LockWorkStation",
            shell=True
        )

        return "Locking the computer."

    # =====================================================
    # CANCEL SHUTDOWN / RESTART
    # =====================================================

    if contains_any(
        c,
        [
            "cancel shutdown",
            "shutdown cancel",
            "cancel restart"
        ]
    ):

        os.system("shutdown /a")

        return "Shutdown or restart cancelled."

    # =====================================================
    # SHUTDOWN
    # =====================================================

    if contains_any(
        c,
        [
            "shut down my pc",
            "shutdown my pc",
            "shut down my computer",
            "shutdown my computer",
            "pc ko shutdown",
            "computer ko shutdown",
            "pc band karo",
            "computer band karo",
            "laptop band karo",
            "shutdown pc",
            "shutdown computer",
            "shut down pc",
            "shut down computer",
            "shutdown",
            "shut down",
        ]
    ):

        os.system("shutdown /s /t 10")

        return (
            "PC shutdown 10 seconds mein scheduled hai. "
            "Agar cancel karna ho to bolo, cancel shutdown."
        )

    # =====================================================
    # RESTART
    # =====================================================

    if contains_any(
        c,
        [
            "restart my pc",
            "restart my computer",
            "restart pc",
            "restart computer",
            "pc restart",
            "computer restart",
            "pc ko restart",
            "computer ko restart",
        ]
    ):

        os.system("shutdown /r /t 10")

        return (
            "PC restart 10 seconds mein scheduled hai. "
            "Agar cancel karna ho to bolo, cancel restart."
        )

    # =====================================================
    # SLEEP
    # =====================================================

    sleep_commands = [
        "sleep",
        "sleep pc",
        "sleep my pc",
        "sleep computer",
        "put pc to sleep",
        "put my pc to sleep",
        "computer sleep",
        "pc sleep",
        "laptop sleep",
        "laptop ko sleep",
        "pc ko sleep",
        "computer ko sleep",
        "system sleep",
        "sleep my computer",
    ]

    if (
        c in sleep_commands
        or contains_any(
            c,
            [
                "put my pc to sleep",
                "put pc to sleep"
            ]
        )
    ):

        try:

            ctypes.windll.powrprof.SetSuspendState(
                0,
                1,
                0
            )

            return "Putting the PC to sleep."

        except Exception as e:

            print("Sleep error:", e)

            return "I couldn't put the PC to sleep."

    # =====================================================
    # NOTHING MATCHED
    # =====================================================

    return None