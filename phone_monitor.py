"""Best-effort Phone Link call monitor for Windows.

Phone Link itself handles the phone integration. This module only watches the
visible Phone Link UI for call-related text. It cannot bypass Android/Windows
permissions. If UI Automation is unavailable, the monitor simply stays off.
"""

import re
import threading
import time

try:
    from pywinauto import Desktop
except Exception:
    Desktop = None


CALL_WORDS = (
    "incoming call",
    "is calling",
    "calling you",
    "incoming phone call",
)


class PhoneCallMonitor:
    def __init__(self, on_call):
        self.on_call = on_call
        self.running = False
        self.thread = None
        self.last_event = ""

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        if Desktop is None:
            print("Phone monitor: pywinauto is not installed; monitor disabled.")
            return

        while self.running:
            try:
                text = self._read_phone_link_text()
                lower = text.lower()
                if any(word in lower for word in CALL_WORDS):
                    event = self._extract_event(text)
                    if event and event != self.last_event:
                        self.last_event = event
                        self.on_call(event)
            except Exception as e:
                print("Phone monitor error:", e)
            time.sleep(2.0)

    def _read_phone_link_text(self):
        pieces = []
        windows = Desktop(backend="uia").windows()
        for win in windows:
            title = win.window_text() or ""
            if "phone link" not in title.lower() and "your phone" not in title.lower():
                continue
            pieces.append(title)
            try:
                for child in win.descendants():
                    t = child.window_text() or ""
                    if t:
                        pieces.append(t)
            except Exception:
                pass
        return "\n".join(pieces)

    def _extract_event(self, text):
        lines = [x.strip() for x in text.splitlines() if x.strip()]
        for line in lines:
            low = line.lower()
            if any(word in low for word in CALL_WORDS):
                return line
        return "Incoming call"
