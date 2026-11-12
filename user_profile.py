from memory import profile, remember


def get_user_name():
    name = profile().get("user_name", "")
    return str(name).strip()


def set_user_name(name):
    name = " ".join(str(name).strip().split())
    if name:
        remember("user_name", name)
    return name


def user_title():
    name = get_user_name()
    return name if name else "sir"


def first_greeting():
    name = get_user_name()
    if name:
        return f"Hello {name!s}. Main Lucki hoon. Aaj kya karna hai?"
    return "Hello sir. Main Lucki hoon. Aaj kya karna hai?"
