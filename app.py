"""
Prime X Assistant — Render Web Service Entry Point
Run this file on Render (Start Command: python app.py)

Flask is the main process (required for Render Web Service).
Pyrogram bot runs in a background thread.
"""

from keep_alive import run_server

if __name__ == "__main__":
    run_server()
