import os
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")

def ask_ai(text):
    try:
        if not API_KEY:
            return "ERROR: GEMINI_API_KEY not found"

        genai.configure(api_key=API_KEY)

        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content(text)

        return response.text

    except Exception as e:
        return f"ERROR: {e}"
