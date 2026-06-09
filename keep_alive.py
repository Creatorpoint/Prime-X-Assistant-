"""
Prime X Assistant — Keep Alive (Render Web Service Compatible)
Flask is the MAIN process on Render Web Service.
Bot runs in a background thread.
"""

import os
import threading
import asyncio
from flask import Flask, jsonify

flask_app = Flask(__name__)

# ── Routes ──────────────────────────────────────────────────────────────────

@flask_app.route("/")
def home():
    return jsonify({
        "status": "✅ Running",
        "bot": "Prime X Assistant",
        "owner": "@PREMGUPTA2M"
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ── Bot runner ───────────────────────────────────────────────────────────────

def run_bot():
    """Run the Pyrogram bot in its own asyncio event loop (background thread)."""
    from database import init_db, reset_old_strikes
    from main import app as bot_app

    async def _start():
        init_db()
        print("✅ Database initialized.")

        async def _cleanup_loop():
            while True:
                await asyncio.sleep(86400)
                reset_old_strikes()

        async with bot_app:
            print("✅ Prime X Assistant bot is running!")
            asyncio.create_task(_cleanup_loop())
            await asyncio.Event().wait()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_start())


def start_bot_thread():
    """Start bot in a background daemon thread."""
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    print("✅ Bot thread started.")


def run_server():
    """
    Entry point for Render Web Service.
    Starts bot in background, Flask in foreground (main process).
    """
    start_bot_thread()
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask server starting on port {port}...")
    flask_app.run(host="0.0.0.0", port=port)
