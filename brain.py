from datetime import datetime

from ai import ask_ai
from quick_answers import quick_answer
from safety import guard_command
from screen_vision import analyze_screen
from commands import execute_command
from live_web import needs_live_search
from student import local_student_command
from user_profile import user_title
from artifact_generator import generate_pdf, generate_ppt, generate_image
from capabilities import help_text


def _run_command_chain(command, mode="general"):
    """Run clearly chained commands in order; return None for ordinary requests."""
    import re
    raw = command.strip()
    # Require explicit sequencing language to avoid splitting normal questions.
    parts = re.split(r"\s*(?:;|\band then\b|\buske baad\b|\bthen\b|\bphir\b)\s*", raw, flags=re.I)
    if len(parts) < 2:
        return None
    parts = [part.strip(" ,.") for part in parts if part.strip(" ,.")]
    if len(parts) < 2 or len(parts) > 6:
        return None
    results = []
    for part in parts:
        answer = process_command(part, mode=mode, _allow_chain=False)
        if answer:
            results.append(str(answer))
    return "Ho gaya. " + " ".join(results) if results else None


def process_command(command, mode="general", _allow_chain=True):
    c = command.lower().strip()

    if _allow_chain:
        chained = _run_command_chain(command, mode)
        if chained:
            return chained

    # Safety/privacy guard MUST run before local actions or the AI.
    guarded = guard_command(command)
    if guarded:
        return guarded

    # Direct, low-latency answers for simple conversational questions.
    qa = quick_answer(command)
    if qa:
        return qa

    # Explicit screen-analysis requests. The result is spoken and shown by the UI.
    screen_phrases = [
        "screen dekho", "meri screen dekho", "screen analyze", "screen analysis",
        "what is on my screen", "what's on my screen", "dekho meri screen",
        "screen par kya hai", "screen pe kya hai", "screen check karo",
    ]
    if any(p in c for p in screen_phrases):
        return analyze_screen(command)

    # Time/date always come from the PC clock.
    if any(x in c for x in [
        "what time is it", "current time", "abhi time", "abhi kitne baje",
        "kitne baje ho rahe", "time kya hai", "abhi time kya hai", "samay kya hai",
    ]) or c in {"time", "samay"}:
        now = datetime.now()
        return f"Abhi {now.strftime('%I:%M %p')} baj rahe hain. Aaj {now.strftime('%d %B %Y')} hai."

    if any(x in c for x in [
        "today's date", "aaj ki date", "aaj date kya hai", "aaj ki tareekh",
        "date kya hai", "tareekh",
    ]) or c in {"date", "today"}:
        return f"Aaj {datetime.now().strftime('%d %B %Y')} hai."

    # Owner identity is fixed for this private installation: Narendra Soni.

    if c in {"help", "help me", "lucki help", "what can you do", "what can you help with",
             "tum kya kar sakte ho", "tum meri kya help kar sakte ho", "lucki kya kar sakta hai",
             "how can you help me", "how can you help"}:
        return help_text()

    # A project request gets the richer project-mentor instructions in ai.py.
    project_words = ["project bana", "project banao", "project help", "project me help",
                     "build my project", "make this project", "debug my project",
                     "app banana", "app banao", "website banana", "game banana"]
    if any(x in c for x in project_words):
        return ask_ai(command, mode="project")

    if c in {"hello", "hi", "hey", "hy", "hii", "namaste"}:
        return f"Hey {user_title()}! 👋 Main Lucki hoon. Batao, kya chal raha hai?"

    # Keep casual joking/playful conversations natural and fast.
    playful_phrases = [
        "joke suna", "joke sunao", "ek joke", "jokes suna",
        "mazak kar raha", "mazak kar rahi", "masti kar", "masti karo",
        "mujhe hasa", "hasao", "hansao", "funny batao", "kuch funny",
        "haha", "hehe", "lol",
    ]
    if any(x in c for x in playful_phrases):
        return ask_ai(
            command,
            mode="general",
        )

    if any(x in c for x in [
        "your name", "what is your name", "who are you", "tum kon ho", "tum kaun ho",
    ]):
        return "Main Lucki hoon — aapka personal AI assistant."

    if any(x in c for x in [
        "who am i", "who i am", "what is my name", "whats my name", "what's my name",
        "main kon hu", "main kaun hu", "main kaun hoon", "me kon hu", "mein kon hu",
        "mera naam kya hai", "mera naam batao", "mai kon hu",
    ]):
        return "Aap Narendra Soni hain — mere owner aur creator."

    if any(x in c for x in [
        "who created you", "who made you", "who is your creator", "who is your developer",
        "lucki ka developer", "lucki kisne banaya", "lucki ko kisne banaya", "narendra soni kaun hai",
    ]):
        return "Narendra Soni Lucki AI ke Founder aur Developer hain."

    # Local student artifact generation. These are safe, local file outputs.
    if any(k in c for k in ["make a pdf", "create a pdf", "pdf bana", "pdf banao"]):
        topic = command
        content = ask_ai(f"Create clean student-ready PDF content for this request: {topic}", mode="study")
        page_size = "A3" if "a3" in c else ("LETTER" if "letter" in c else "A4")
        path = generate_pdf("Lucki PDF", content, page_size=page_size)
        return f"PDF ready hai: {path}"

    if any(k in c for k in ["make a ppt", "create a ppt", "make ppt", "ppt bana", "ppt banao", "presentation bana"]):
        topic = command
        content = ask_ai(f"Create concise presentation content with slide-separated sections for: {topic}", mode="study")
        aspect = "4:3" if "4:3" in c else "16:9"
        path = generate_ppt("Lucki Presentation", content, aspect=aspect)
        return f"PPT ready hai: {path}"

    if any(k in c for k in ["generate image", "create image", "image bana", "image banao", "poster bana"]):
        path = generate_image("Lucki Image", command)
        return f"Image ready hai: {path}"

    # Local student commands first.
    x = local_student_command(command)
    if x:
        return x

    # Local PC/phone controls BEFORE AI so natural commands are executed.
    x = execute_command(command)
    if x:
        return x

    # Current questions are handled by ai.py's independent web search.
    return ask_ai(command, mode)
