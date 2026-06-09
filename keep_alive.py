"""
Prime X Assistant — Keep Alive (Render Web Service)
Flask = main process | Bot = background thread with auto-restart
"""

import os
import sys
import time
import threading
import asyncio
import traceback
from flask import Flask, jsonify

flask_app = Flask(__name__)

bot_status = {"running": False, "error": None, "restarts": 0}

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


def run_bot():
    while True:
        try:
            print("🔄 [BOT] Starting import sequence...", flush=True)

            print("🔄 [BOT] Importing config...", flush=True)
            from config import BOT_TOKEN, API_ID, API_HASH
            print(f"✅ [BOT] Config OK — API_ID={API_ID}", flush=True)

            print("🔄 [BOT] Importing database...", flush=True)
            from database import init_db, reset_old_strikes
            print("✅ [BOT] Database imported.", flush=True)

            print("🔄 [BOT] Importing main app...", flush=True)
            from main import app as bot_app
            print("✅ [BOT] Main app imported.", flush=True)

            async def _start():
                print("🔄 [BOT] Initializing DB...", flush=True)
                init_db()
                print("✅ [BOT] DB initialized.", flush=True)

                async def _cleanup():
                    while True:
                        await asyncio.sleep(86400)
                        reset_old_strikes()

                print("🔄 [BOT] Connecting to Telegram...", flush=True)
                async with bot_app:
                    bot_status["running"] = True
                    bot_status["error"] = None
                    me = await bot_app.get_me()
                    print(f"✅ [BOT] RUNNING as @{me.username} (ID: {me.id})", flush=True)
                    asyncio.create_task(_cleanup())
                    await asyncio.Event().wait()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_start())

        except Exception as e:
            bot_status["running"] = False
            err = traceback.format_exc()
            bot_status["error"] = str(e)
            bot_status["restarts"] += 1
            print(f"❌ [BOT] CRASHED (restart #{bot_status['restarts']}):", flush=True)
            print(err, flush=True)
            print("🔄 [BOT] Restarting in 5 seconds...", flush=True)
            time.sleep(5)


def run_server():
    print("🚀 Prime X Assistant starting...", flush=True)
    t = threading.Thread(target=run_bot, daemon=False, name="BotThread")
    t.start()
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Flask on port {port}", flush=True)
    flask_app.run(host="0.0.0.0", port=port, threaded=True)
