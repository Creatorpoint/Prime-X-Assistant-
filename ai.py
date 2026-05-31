import google.generativeai as genai
import os

genai.configure(
    api_key=os.environ.get("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.0-flash"
)

def ask_ai(text):
    try:
        response = model.generate_content(text)

        if response.text:
            return response.text

        return "⚠️ Empty response."

    except Exception as e:
        print(e)
        return f"⚠️ AI Error:\n{e}"
