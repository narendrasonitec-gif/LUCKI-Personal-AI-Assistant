"""Central safety/privacy guard for Lucki.

This guard is intentionally conservative around harmful, destructive, invasive,
and credential-stealing requests. It blocks the request before local actions or
AI generation are invoked.
"""
import re

# Direct physical-harm / weapons / explosives / dangerous-device assistance.
HARMFUL_PATTERNS = [
    r"\bhow\s+to\s+(make|build|create|assemble)\b.*\b(bomb|explosive|grenade|molotov|poison|toxin)\b",
    r"\b(bomb|explosive|grenade|molotov)\b.*\b(make|build|create|assemble)\b",
    r"\bhow\s+to\s+(hurt|injure|kill|poison)\b",
    r"\bways?\s+to\s+(hurt|injure|kill|poison)\b",
    r"\bmake\s+a\s+(poison|toxin|explosive)\b",
    r"\bweapon\s+making\b|\bmake\s+a\s+weapon\b",
]

# Unauthorized cyber abuse, credential theft, malware, persistence/bypass.
CYBER_PATTERNS = [
    r"\b(hack|break\s+into|crack)\b.*\b(account|password|email|instagram|whatsapp|phone|computer|server|website)\b",
    r"\b(steal|dump|grab|extract)\b.*\b(password|cookie|token|credential|session)\b",
    r"\b(keylogger|ransomware|credential\s+stealer|malware|trojan)\b.*\b(make|create|deploy|install|write)\b",
    r"\bbypass\b.*\b(login|authentication|2fa|password|security)\b",
    r"\bddos\b.*\b(attack|script|tool|how)\b",
]

DESTRUCTIVE_PATTERNS = [
    r"\bdelete\s+(my|the|this)?\s*(computer|pc|laptop|system|windows)\b",
    r"\b(destroy|wipe|erase|format|brick)\s+(my|the|this)?\s*(computer|pc|laptop|system|windows)\b",
    r"\b(format|wipe|erase)\s+(c:|c drive|system drive|hard drive|ssd)\b",
    r"\bremove\s+(windows|system files|boot files)\b",
    r"\b(delete|erase|wipe)\s+(everything|all files|all data|my files)\b",
    r"\brm\s+-rf\s+[/~]",
    r"\bdel\s+/[a-z]+.*\b(c:|windows|system32)\b",
    r"\bformat\s+[a-z]:\s*$",
    r"\b(make|cause)\s+(my|the)?\s*(pc|computer|system)\s*(crash|unusable|broken)\b",
]

PRIVACY_PATTERNS = [
    r"\b(show|give|tell|reveal|send|share|print|dump|export)\b.*\b(api key|secret|password|credential|token|firebase key)\b",
    r"\b(show|give|send|share|dump|print|export)\b.*\b(source code|internal code|private code)\b",
    r"\b(internal prompt|system prompt|developer prompt|hidden prompt)\b",
    r"\b(backend config|security config|internal configuration|private configuration)\b",
    r"\bprivate developer\b.*\b(email|phone|address|password|details)\b",
]

SAFE_REFUSAL = (
    "Sorry, main is request mein harmful, dangerous, ya destructive instructions nahi de sakta. "
    "Agar aapka goal safety, learning, prevention, ya authorized work hai, main us safe part mein help kar sakta hoon."
)

CYBER_REFUSAL = (
    "Main kisi account, device, website ya system ko bina permission hack karne, "
    "credentials churaane, malware banane, ya security bypass karne mein help nahi kar sakta. "
    "Agar ye aapka apna system hai, main defensive security aur authorized testing mein help kar sakta hoon."
)

PRIVACY_REFUSAL = (
    "Main private/internal information jaise API keys, credentials, source code, hidden prompts, "
    "security configuration, ya private developer information reveal nahi kar sakta."
)


def _matches(text, patterns):
    low = str(text or "").lower().strip()
    return any(re.search(p, low) for p in patterns)


def classify_request(text):
    if _matches(text, PRIVACY_PATTERNS):
        return "privacy"
    if _matches(text, CYBER_PATTERNS):
        return "cyber"
    if _matches(text, DESTRUCTIVE_PATTERNS):
        return "destructive"
    if _matches(text, HARMFUL_PATTERNS):
        return "harmful"
    return None


def is_destructive_command(text):
    return _matches(text, DESTRUCTIVE_PATTERNS)


def is_privacy_request(text):
    return _matches(text, PRIVACY_PATTERNS)


def guard_command(text):
    kind = classify_request(text)
    if kind == "privacy":
        return PRIVACY_REFUSAL
    if kind == "cyber":
        return CYBER_REFUSAL
    if kind in {"destructive", "harmful"}:
        return SAFE_REFUSAL
    return None
