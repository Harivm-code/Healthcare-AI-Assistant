
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def get_gemini_response(user_message):

    if not GEMINI_API_KEY:
        return "Error: Gemini API key not found. Check your .env file."

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{GEMINI_MODEL}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [{
            "parts": [{
                "text": (
                    "You are a healthcare information assistant. "
                    "Provide general health information in simple English. "
                    "Do not diagnose diseases or prescribe medicines. "
                    "Encourage users to consult qualified healthcare "
                    "professionals for personal medical concerns.\n\n"
                    f"User: {user_message}"
                )
            }]
        }]
    }

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=45
            )

            if response.status_code in [429, 500, 502, 503, 504]:
                if attempt < 2:
                    time.sleep(2 ** attempt)
                    continue

            response.raise_for_status()

            result = response.json()

            candidates = result.get("candidates", [])

            if not candidates:
                return "Sorry, Gemini could not generate a response. Please try again."

            parts = candidates[0].get("content", {}).get("parts", [])

            if not parts:
                return "Sorry, no response was generated. Please try again."

            return parts[0].get("text", "No response available.")

        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return "Gemini timed out. Please try again."

        except requests.exceptions.RequestException as error:
            return f"API connection error: {error}"

    return "Gemini is temporarily unavailable. Please try again later."
