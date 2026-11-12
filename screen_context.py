_last_screen_analysis = ""


def set_screen_context(text):
    global _last_screen_analysis
    _last_screen_analysis = str(text or "").strip()


def get_screen_context():
    return _last_screen_analysis


def clear_screen_context():
    global _last_screen_analysis
    _last_screen_analysis = ""
