"""Lightweight conversational cue detection for Lucki.

This does not claim Lucki has human feelings. It detects language cues so
responses can be warmer, calmer, playful, or more encouraging when useful.
"""

from __future__ import annotations

import re


PATTERNS = {
    "happy": [
        r"\b(happy|khush|mast|maza|awesome|great|excited|yay|woohoo)\b",
        r"😂|🤣|😄|😁|😆|😊|❤️|❤",
    ],
    "sad": [
        r"\b(sad|udaas|dukhi|rona|ro raha|ro rahi|lonely|akela|akeli)\b",
        r"😢|😭|☹|🙁|💔",
    ],
    "stressed": [
        r"\b(stress|stressed|tension|pareshan|pareshaan|pressure|overwhelmed|thak gaya|thak gayi)\b",
        r"😫|😩|😓|😥",
    ],
    "angry": [
        r"\b(angry|gussa|gusse|irritated|frustrated|chidh|chida)\b",
        r"😡|🤬|😤",
    ],
    "playful": [
        r"\b(joke|jokes|mazak|masti|funny|hasao|hansao|hansi|lol|haha|hehe|rofl)\b",
        r"😂|🤣|😜|😝|😎",
    ],
    "confused": [
        r"\b(confused|samajh nahi|samajh nhi|kya karu|what do i do|why|kyu|kyun)\b",
        r"\?{2,}|🤔",
    ],
}


def detect_emotion(text: str) -> str:
    value = str(text or "").strip().lower()
    if not value:
        return "neutral"

    scores = {}
    for emotion, patterns in PATTERNS.items():
        score = 0
        for pattern in patterns:
            if re.search(pattern, value, flags=re.IGNORECASE):
                score += 1
        if score:
            scores[emotion] = score

    if not scores:
        return "neutral"
    return max(scores, key=scores.get)


def conversation_style(emotion: str) -> str:
    styles = {
        "happy": "Match the user's positive energy naturally.",
        "sad": "Be gentle, supportive, and non-judgmental. Do not overdo cheerfulness.",
        "stressed": "Be calm and practical. Break the problem into small manageable steps.",
        "angry": "Stay calm and respectful. Acknowledge frustration without escalating it.",
        "playful": "The user is being playful. You may respond with light humor or a natural 'haha' when appropriate.",
        "confused": "Explain clearly and simply, and reduce unnecessary complexity.",
        "neutral": "Use a natural conversational tone.",
    }
    return styles.get(emotion, styles["neutral"])
