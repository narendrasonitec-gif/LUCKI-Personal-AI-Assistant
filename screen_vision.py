from pathlib import Path

from computer_control import screenshot
from screen_context import set_screen_context


def capture_screen():
    path = Path.home() / "Pictures" / "Lucki_Screenshot.png"
    return screenshot(str(path))


def analyze_screen(prompt=None):
    """Capture the current screen and ask the configured Gemini vision model to analyze it."""
    try:
        from google import genai
        from google.genai import types
        from config import GEMINI_API_KEY, GEMINI_MODEL

        if not GEMINI_API_KEY:
            return "Gemini API key is missing."

        path = capture_screen()
        if not path:
            return "I couldn't capture the screen."

        image_bytes = Path(path).read_bytes()
        client = genai.Client(api_key=GEMINI_API_KEY)
        instruction = prompt or (
            "Look at this computer screenshot. Tell me directly what is visible, "
            "what app/window is open, and explain any obvious error or text. "
            "Do not claim that you clicked or changed anything."
        )
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                instruction,
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            ],
        )
        result = (response.text or "I couldn't understand the screen.").strip()
        set_screen_context(result)
        return result
    except Exception as e:
        print("Screen vision error:", e)
        return "Screen vision is unavailable with the current Gemini model or setup."
