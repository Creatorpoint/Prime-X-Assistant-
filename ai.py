import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

def ask_ai(text):
    try:
        response = model.generate_content(text)
        return response.text

    except Exception as e:
        return f"❌ Gemini Error:\n{e}"
