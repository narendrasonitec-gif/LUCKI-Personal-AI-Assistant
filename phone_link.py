"""Phone Link helpers.

Phone Link is a Microsoft app. Lucki can open it and automate the visible
PC interface, but availability of calls/messages depends on the phone,
Windows, Bluetooth/Wi-Fi, permissions, and Phone Link support.
"""

import re
import subprocess
import time

from computer_control import open_phone_link, hotkey, _press


def open_phone():
    return open_phone_link()


def answer_call():
    """Best-effort keyboard action after Phone Link's call UI is focused."""
    # Enter is intentionally used only after the user explicitly asks to answer.
    return _press("enter")


def reject_call():
    """Best-effort escape action for the visible Phone Link call UI."""
    return _press("esc")


def open_messages():
    if not open_phone_link():
        return False
    time.sleep(1.2)
    return True


def send_message_text(text):
    """Type text into the currently focused Phone Link message box.

    The user must explicitly request sending. This function does not press
    Send automatically; it types the message so the user can verify it.
    """
    from computer_control import type_text
    return type_text(text)


def notification_text_is_call(text):
    if not text:
        return False
    t = text.lower()
    patterns = [
        "incoming call",
        "is calling",
        "calling you",
        "missed call",
        "incoming phone call",
    ]
    return any(p in t for p in patterns)


def extract_caller_name(text):
    if not text:
        return "Unknown caller"
    patterns = [
        r"^(.+?)\s+is calling",
        r"call from\s+(.+)$",
        r"incoming call[:\- ]+(.+)$",
    ]
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return m.group(1).strip()
    return "Unknown caller"
