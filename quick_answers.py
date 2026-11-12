from datetime import datetime


def quick_answer(text):
    c = str(text or "").strip().lower()
    table = {
        "hello": "Hello! Batao.",
        "hi": "Hi! Batao.",
        "hey": "Hey! Batao.",
        "namaste": "Namaste! Batao.",
        "how are you": "Main bilkul ready hoon. Batao kya karna hai.",
        "how are you doing": "Main bilkul ready hoon. Batao kya karna hai.",
        "what is your name": "Main Lucki hoon, aapka AI assistant.",
        "tumhara naam kya hai": "Main Lucki hoon, aapka AI assistant.",
        "who are you": "Main Lucki hoon, aapka AI assistant.",
        "tum kaun ho": "Main Lucki hoon, aapka AI assistant.",
        "time": f"Abhi {datetime.now().strftime('%I:%M %p')} baj rahe hain.",
        "what time is it": f"Abhi {datetime.now().strftime('%I:%M %p')} baj rahe hain.",
        "aaj ki date kya hai": f"Aaj {datetime.now().strftime('%d %B %Y')} hai.",
        "what is today's date": f"Aaj {datetime.now().strftime('%d %B %Y')} hai.",
    }
    return table.get(c)
