import asyncio
import os
import tempfile
import time
import subprocess

import speech_recognition as sr

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pygame
    pygame.mixer.init()
except Exception:
    pygame = None


recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

VOICE_PROFILES = {
    "maple": {
        "label": "Maple - Female",
        "en": "en-US-AriaNeural",
        "hi": "hi-IN-SwaraNeural",
        "rate": "+0%",
        "pitch": "+0Hz",
    },
    "jarvis": {
        "label": "Jarvis-style - Male",
        "en": "en-US-GuyNeural",
        "hi": "hi-IN-MadhurNeural",
        "rate": "-4%",
        "pitch": "-2Hz",
    },
}

_current_voice = "jarvis"


def set_voice(name):
    global _current_voice
    name = str(name).lower().strip()
    if name in VOICE_PROFILES:
        _current_voice = name
        return True
    return False


def get_voice():
    return _current_voice


def voice_label():
    return VOICE_PROFILES[_current_voice]["label"]


def is_hindi(text):
    text = str(text or "")
    if any("\u0900" <= c <= "\u097F" for c in text):
        return True
    low = text.lower()
    roman_hindi = (
        " aaj ", " kya ", " hai ", " ho ", " kaise ", " kyu ", " kyun ",
        " mujhe ", " tum ", " aap ", " batao ", " kholo ", " karo ",
        " nahi ", " chahiye ", " mera ", " meri ", " ye ", " yeh ",
        " woh ", " aur ", " abhi ", " kal ", " kahan ", " kaun ",
    )
    padded = " " + low.strip() + " "
    return any(x in padded for x in roman_hindi)


async def make_voice(text, path):
    profile = VOICE_PROFILES[_current_voice]
    language = "hi" if is_hindi(text) else "en"
    voice = profile[language]

    communicator = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=profile["rate"],
        pitch=profile["pitch"],
    )
    await communicator.save(path)


def speak(text):
    if not text:
        return

    print("LUCKI:", text)

    if not edge_tts or not pygame:
        return

    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)

    try:
        asyncio.run(make_voice(text, path))
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            time.sleep(0.05)

        pygame.mixer.music.unload()

    except Exception as e:
        print("Speech error:", e)
        # Windows built-in SAPI fallback: still speaks if Edge TTS returns 403/offline.
        try:
            if os.name == "nt":
                safe_text = str(text).replace("'", "''")
                ps = (
                    "$ErrorActionPreference='Stop'; "
                    "$v=New-Object -ComObject SAPI.SpVoice; "
                    f"$v.Speak('{safe_text}') | Out-Null"
                )
                subprocess.run(
                    ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
                    timeout=90, check=True, capture_output=True, text=True
                )
        except Exception as fallback_error:
            print("Windows speech fallback error:", fallback_error)

    finally:
        try:
            os.remove(path)
        except Exception:
            pass


def listen(timeout=8, phrase_time_limit=20):
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        return recognizer.recognize_google(
            audio,
            language="en-IN",
        ).lower().strip()

    except (
        sr.WaitTimeoutError,
        sr.UnknownValueError,
    ):
        return ""

    except Exception as e:
        print("Listen error:", e)
        return ""
