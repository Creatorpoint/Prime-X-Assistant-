"""
Prime X Assistant — Configuration
Loads all env variables from .env or system environment.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram credentials ────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
API_ID: int = int(os.environ.get("API_ID", "0"))
API_HASH: str = os.environ.get("API_HASH", "")
OWNER_ID: int = int(os.environ.get("OWNER_ID", "5889016144"))

# ── AI ──────────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")

# ── Links ───────────────────────────────────────────────────────────────────
CHANNEL_LINK: str = os.environ.get("CHANNEL_LINK", "https://t.me/+bQUSBWIVT-dmZjA9")
GROUP_LINK: str = os.environ.get("GROUP_LINK", "https://t.me/PRIME_X_CHAT2")

# ── Assets ──────────────────────────────────────────────────────────────────
WELCOME_IMAGE: str = os.environ.get(
    "WELCOME_IMAGE",
    "https://files.catbox.moe/splh4m.jpg"
)

# ── Validation ──────────────────────────────────────────────────────────────
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable not set!")
if not API_ID or API_ID == 0:
    raise ValueError("❌ API_ID environment variable not set!")
if not API_HASH:
    raise ValueError("❌ API_HASH environment variable not set!")
