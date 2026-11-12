from datetime import datetime


# Words/phrases that usually mean the user wants current information.
LIVE_KEYWORDS = [
    "latest",
    "current",
    "right now",
    "today",
    "today's",
    "abhi",
    "filhaal",
    "latest news",
    "current news",
    "breaking news",
    "aaj ki news",
    "aaj ki khabar",
    "abhi kya",
    "who is the current",
    "current minister",
    "current president",
    "current prime minister",
    "current education minister",
]


def needs_live_search(text):
    """
    Returns True when a question probably needs current/live information.
    """

    text = text.lower().strip()

    return any(
        keyword in text
        for keyword in LIVE_KEYWORDS
    )


def current_date_time():
    """
    Gets date and time directly from the computer.
    """

    now = datetime.now()

    return (
        f"Date: {now.strftime('%d %B %Y')}\n"
        f"Time: {now.strftime('%I:%M %p')}"
    )


def live_answer_unavailable(question):
    """
    Temporary safe response until the web-search backend is connected.
    """

    return (
        "Ye question current/live information maang raha hai. "
        "Live web search abhi Lucki me connect nahi hai, "
        "isliye main outdated information ko current bolkar nahi bataunga."
    )