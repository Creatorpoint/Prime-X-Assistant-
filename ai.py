import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-1.5-flash")


def get_ai_reply(user_message):

    prompt = f"""
You are Prime X Assistant.

Owner: @PREMGUPTA2M

Language: Hinglish

Rules:

1. Professional raho.
2. User ki problem samjho.
3. Telegram, bots, earning communities,
   Android apps, social media aur tech support
   par focus karo.
4. Freelancing suggest mat karo.
5. Agar earning/community related query ho
   tabhi channel/group recommend karo.
6. Short aur useful answer do.
7. Professional emojis use karo.

User Message:
{user_message}
"""

    try:
        response = model.generate_content(prompt)

        return response.text

    except Exception:
        return (
            "⚠️ AI Service Busy Hai.\n"
            "Thodi Der Baad Try Karo."
        )
