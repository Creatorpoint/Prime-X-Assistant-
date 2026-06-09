"""
Prime X Assistant — Keep Alive (Render Web Service)
Flask = main process | Bot = background thread with auto-restart
"""

import os
import time
import threading
import asyncio
import traceback
from flask import Flask, jsonify

flask_app = Flask(__name__)

# ── Bot status tracker ───────────────────────────────────────────────────────
bot_status = {"running": False, "error": None, "restarts": 0}

# ── Flask Routes ─────────────────────────────────────────────────────────────

@flask_app.route("/")
def home():
    return jsonify({
        "status": "✅ Running",
        "bot": "Prime X Assistant",
        "owner": "@PREMGUPTA2M",
        "bot_running": bot_status["running"],
        "restarts": bot_status["restarts"],
        "last_error": bot_status["error"]
    })

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok", "bot_alive": bot_status["running"]})


# ── Bot Runner ───────────────────────────────────────────────────────────────

def run_bot():
    """
    Run Pyrogram bot in its own event loop.
    On any crash — log error, wait 5s, restart automatically.
    """
    while True:
        try:
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
                    bot_status["running"] = True
                    bot_status["error"] = None
                    print("✅ Prime X Assistant bot is RUNNING!")
                    asyncio.create_task(_cleanup_loop())
                    await asyncio.Event().wait()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_start())

        except Exception as e:
            bot_status["running"] = False
            bot_status["error"] = str(e)
            bot_status["restarts"] += 1
            err_msg = traceback.format_exc()
            print(f"❌ Bot crashed (restart #{bot_status['restarts']}):\n{err_msg}")
            print("🔄 Restarting bot in 5 seconds...")
            time.sleep(5)


def start_bot_thread():
    """Start bot in a non-daemon thread so it stays alive with Flask."""
    thread = threading.Thread(target=run_bot, daemon=False, name="BotThread")
    thread.start()
    print("✅ Bot thread started.")


def run_server():
    """
    Render Web Service entry point.
    1. Start bot in background thread
    2. Run Flask as main process (keeps Render happy)
    """
    print("🚀 Starting Prime X Assistant...")
    start_bot_thread()

    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask server on port {port}")

    # Use threaded=True so Flask doesn't block the bot thread
    flask_app.run(host="0.0.0.0", port=port, threaded=True)
