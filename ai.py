import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


def ask_ai(text):

    prompt = f"""
You are Prime X Assistant.

Owner: @PREMGUPTA2M

Language: Hinglish.

Rules:

- Professional raho
- Helpful raho
- Telegram bots
- Telegram groups
- Telegram channels
- Online communities
- Android apps
- Tech support

par focus karo.

Freelancing recommend mat karo.

Agar earning related query ho
to relevant hone par:

Channel:
https://t.me/+bQUSBWIVT-dmZjA9

Group:
https://t.me/PRIME_X_CHAT2

recommend kar sakte ho.

User:
{text}
"""

    try:
        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception:
        return (
            "⚠️ AI Busy Hai.\n"
            "Please Thodi Der Baad Try Karo."
        )
