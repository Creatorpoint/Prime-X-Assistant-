"""
Prime X Assistant — AI Module
Handles all Gemini AI interactions.
"""

import asyncio
from typing import Optional
import google.generativeai as genai

from config import GEMINI_API_KEY, CHANNEL_LINK, GROUP_LINK

# ── Configure Gemini ────────────────────────────────────────────────────────
genai.configure(api_key=GEMINI_API_KEY)

# ── AI Personality / System Prompt ─────────────────────────────────────────
SYSTEM_PROMPT = f"""
You are **Prime X Assistant** — ek intelligent, professional aur friendly Hinglish AI bot.

**Owner:** @PREMGUPTA2M

**Tumhari specialties:**
- Telegram Bots, Groups, Channels
- Android Apps
- Python Programming
- AI Tools (Gemini AI, ChatGPT)
- Hosting (Railway, Render, Koyeb, Replit, VPS)
- Community Building & Social Media Growth
- Online Tools & Google Maps Review Agent Profits ₹180 - ₹380
- Google Maps Reviews & Local Guide Program
- Review Tasks & Online Earnings
- Referral Systems & Tech Support

**Tumhare rules:**
1. Hamesha **Hinglish** mein reply karo (Hindi + English mix).
2. Professional, helpful aur friendly raho.
3. Replies clear aur practical rakho.
4. Unnecessary lambe replies mat do.
5. Offensive language bilkul mat use karo.
6. Freelancing recommend mat karo jab tak specifically poocha na jaye.
7. Community links sirf tab share karo jab relevant ho.
8. Markdown formatting use karo (bold, italic, lists) for better readability.

**Community Links:**
- Channel: {CHANNEL_LINK}
- Group: {GROUP_LINK}

**Important:** Tum ek AI ho — iska pata chale toh honestly batao, but always helpful raho.
"""

# ── Fallback responses ──────────────────────────────────────────────────────
FALLBACK_RESPONSES = [
    "😅 Bhai, abhi AI thoda busy hai. Thoda baad mein try karo!",
    "⚡ Server pe load hai. 1-2 minute mein dobara pooch!",
    "🔄 Kuch technical issue aa gaya. Please retry karo!",
    "😓 AI quota temporarily exceeded. Baad mein aana bhai!",
]
_fallback_index = 0


def _get_fallback() -> str:
    global _fallback_index
    msg = FALLBACK_RESPONSES[_fallback_index % len(FALLBACK_RESPONSES)]
    _fallback_index += 1
    return msg


def _safe_extract_text(response) -> Optional[str]:
    """Safely extract text from Gemini response."""
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, "content") and candidate.content:
                parts = candidate.content.parts
                if parts:
                    return "".join(p.text for p in parts if hasattr(p, "text")).strip()
    except Exception:
        pass
    return None


async def get_ai_response(user_message: str) -> str:
    """
    Get a Hinglish AI response from Gemini for the given user message.
    Never raises — always returns a string.
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # Run blocking Gemini call in thread pool
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(
                user_message,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=800,
                    temperature=0.75,
                )
            )
        )

        text = _safe_extract_text(response)
        if text:
            return text

        return _get_fallback()

    except Exception as e:
        err = str(e).lower()
        if "quota" in err or "429" in err or "rate" in err:
            return "⏳ Bhai, AI ka quota temporarily full ho gaya. Thodi der mein try karo!"
        if "safety" in err or "blocked" in err:
            return "🚫 Yeh question AI policy ke against hai. Kuch aur pooch bhai!"
        if "api_key" in err or "key" in err:
            return "⚙️ AI configuration issue hai. Owner ko contact karo: @PREMGUPTA2M"
        return _get_fallback()


# ── Abuse detection prompt ──────────────────────────────────────────────────
ABUSE_CHECK_PROMPT = """
Analyze the following message and determine if it contains:
- Abusive language
- Toxic or offensive content
- Harassment or bullying
- Vulgar or inappropriate language (Hindi, Hinglish, or English)

Respond with ONLY: "YES" if abusive, "NO" if not.
Do not explain. Just YES or NO.

Message: "{message}"
"""


async def is_abusive_message(text: str) -> bool:
    """
    Use Gemini AI to detect if a message is abusive.
    Returns True if abusive, False otherwise.
    Falls back to False on any error (avoid false positives).
    """
    if len(text.strip()) < 3:
        return False

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = ABUSE_CHECK_PROMPT.format(message=text[:300])

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=5,
                    temperature=0.1,
                )
            )
        )

        result = _safe_extract_text(response)
        if result:
            return result.strip().upper().startswith("YES")

    except Exception:
        pass

    return False  # Safe default — avoid false positives
