import json
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    _data_root = Path(os.getenv("APPDATA", str(Path.home()))) / "LuckiAI"
    _data_root.mkdir(parents=True, exist_ok=True)
    FILE = _data_root / "lucki_data.json"
else:
    FILE = Path(__file__).with_name("lucki_data.json")

DEFAULT_DATA = {
    "conversation": [],
    "profile": {},
    "notes": [],
    "tasks": []
}

data = DEFAULT_DATA.copy()


def load():
    global data

    try:
        if FILE.exists():
            saved = json.loads(
                FILE.read_text(encoding="utf-8")
            )

            if isinstance(saved, dict):
                for key in DEFAULT_DATA:
                    if key in saved:
                        data[key] = saved[key]

    except Exception as e:
        print("Memory load error:", e)


load()


def save():
    try:
        FILE.write_text(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

    except Exception as e:
        print("Memory save error:", e)


# -------------------------------------------------
# CONVERSATION MEMORY
# -------------------------------------------------

def add_message(role, message):

    # Don't save empty messages
    if not message:
        return

    data["conversation"].append({
        "role": role,
        "message": str(message)
    })

    # Keep only the latest 12 messages
    data["conversation"] = data["conversation"][-12:]

    save()


def get_context():

    if not data["conversation"]:
        return "No recent conversation."

    return "\n".join(
        f"{x.get('role', 'Unknown')}: {x.get('message', '')}"
        for x in data["conversation"]
    )


def clear_memory():
    data["conversation"] = []
    save()


# -------------------------------------------------
# PROFILE
# -------------------------------------------------

def remember(key, value):

    data["profile"][key] = value
    save()


def profile():
    return dict(data["profile"])


# -------------------------------------------------
# NOTES
# -------------------------------------------------

def add_note(title, body):

    data["notes"].append({
        "title": title,
        "content": body
    })

    save()


def notes():
    return list(data["notes"])


def delete_note(index):

    if 0 <= index < len(data["notes"]):
        data["notes"].pop(index)
        save()


# -------------------------------------------------
# TASKS
# -------------------------------------------------

def add_task(title):

    data["tasks"].append({
        "title": title,
        "done": False
    })

    save()


def tasks():
    return list(data["tasks"])


def toggle_task(index):

    if 0 <= index < len(data["tasks"]):
        data["tasks"][index]["done"] = not data["tasks"][index]["done"]
        save()


def delete_task(index):

    if 0 <= index < len(data["tasks"]):
        data["tasks"].pop(index)
        save()