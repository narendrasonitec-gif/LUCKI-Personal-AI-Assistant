import os
import subprocess
import time
import webbrowser
from pathlib import Path

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    import pyperclip
except Exception:
    pyperclip = None



def _ready():
    return pyautogui is not None


def _press(key, presses=1, interval=0.05):
    if not _ready():
        return False
    pyautogui.press(key, presses=presses, interval=interval)
    return True


def scroll(amount):
    if not _ready():
        return False
    pyautogui.scroll(amount)
    return True


def hotkey(*keys):
    if not _ready():
        return False
    pyautogui.hotkey(*keys)
    return True


def type_text(text):
    if not _ready():
        return False
    if pyperclip:
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
    else:
        pyautogui.write(text, interval=0.01)
    return True


def screenshot(path=None):
    if not _ready():
        return None
    if path is None:
        path = str(Path.home() / "Pictures" / "Lucki_Screenshot.png")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    image = pyautogui.screenshot()
    image.save(path)
    return path


def open_phone_link():
    try:
        os.startfile("ms-phone:")
        return True
    except Exception:
        try:
            subprocess.Popen("start shell:AppsFolder\\Microsoft.YourPhone_8wekyb3d8bbwe!App", shell=True)
            return True
        except Exception:
            return False


def media_play_pause():
    return _press("playpause")


def media_next():
    return _press("nexttrack")


def media_previous():
    return _press("prevtrack")


def volume_up():
    return _press("volumeup", presses=3)


def volume_down():
    return _press("volumedown", presses=3)


def mute():
    return _press("volumemute")


def browser_back():
    return hotkey("alt", "left")


def browser_forward():
    return hotkey("alt", "right")


def switch_window():
    return hotkey("alt", "tab")


def minimize_window():
    return hotkey("alt", "space") and _press("n")


def maximize_window():
    return hotkey("alt", "space") and _press("x")


def close_window():
    return hotkey("alt", "f4")


def scroll_up():
    return scroll(6)


def scroll_down():
    return scroll(-6)


def page_up():
    return _press("pageup")


def page_down():
    return _press("pagedown")


def play_video():
    return _press("space")


def pause_video():
    return _press("space")
