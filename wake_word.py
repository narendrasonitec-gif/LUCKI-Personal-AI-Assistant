"""Wake-word detection for Lucki. Uses online Google speech recognition via SpeechRecognition."""
import speech_recognition as sr

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
WAKE_WORDS = {"lucki", "lucky"}


def wait_for_wake_word(should_continue=lambda: True):
    """Return command text following 'Lucki', or True for a wake-only utterance."""
    while should_continue():
        try:
            with sr.Microphone() as source:
                audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
            text = recognizer.recognize_google(audio, language="en-IN").lower().strip()
            print("Wake:", text)
            cleaned = re.sub(r"[^\w\s]", " ", text)
            words = cleaned.split()
            for i, word in enumerate(words):
                if word in WAKE_WORDS:
                    print("LUCKI WAKE:", word)
                    remaining_words = words[i + 1:]
                    # Drop a repeated assistant name in phrases like "Hey Lucki".
                    while remaining_words and remaining_words[0] in WAKE_WORDS:
                        remaining_words.pop(0)
                    remainder = " ".join(remaining_words).strip()
                    return remainder if remainder else True
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            pass
        except sr.RequestError as e:
            print("Speech recognition service error:", e)
        except Exception as e:
            print("Wake error:", e)
    return False

import re
