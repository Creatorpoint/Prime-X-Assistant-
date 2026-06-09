"""
Prime X Assistant — Keep Alive
Flask web server to prevent hosting platforms from sleeping the bot.
"""

import threading
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({
        "status": "✅ Running",
        "bot": "Prime X Assistant",
        "owner": "@PREMGUPTA2M"
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


def keep_alive():
    """Start Flask server in a background daemon thread."""
    thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=8080),
        daemon=True
    )
    thread.start()
    print("✅ Keep-alive server started on port 8080.")
