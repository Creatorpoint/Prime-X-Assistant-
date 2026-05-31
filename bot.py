import os
from dotenv import load_dotenv

from pyrogram import Client
from pyrogram import filters

from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import *
from ai import ask_ai
from keep_alive import keep_alive

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

OWNER_ID = int(
    os.getenv("OWNER_ID")
)

CHANNEL_LINK = os.getenv(
    "CHANNEL_LINK"
)

GROUP_LINK = os.getenv(
    "GROUP_LINK"
)

WELCOME_IMAGE = os.getenv(
    "WELCOME_IMAGE"
)

app = Client(
    "PrimeXAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)


buttons = InlineKeyboardMarkup(
[
[
InlineKeyboardButton(
"📢 Channel",
url=CHANNEL_LINK
),
InlineKeyboardButton(
"💬 Group",
url=GROUP_LINK
)
]
]
)


@app.on_message(
filters.private &
filters.command("start")
)
async def start(client, message):

    add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    await client.send_photo(
        chat_id=message.chat.id,
        photo=WELCOME_IMAGE,
        caption="""
✨ Welcome To Prime X Assistant

🤖 AI Powered Community Assistant

💬 Ask Anything
📱 Telegram Help
🛠 Bot Support
🚀 Fast AI Replies

👨‍💻 Developed By
@PREMGUPTA2M
""",
        reply_markup=buttons
    )


@app.on_message(
filters.group
)
async def save_group(
client,
message
):

    add_group(
        message.chat.id,
        message.chat.title
    )


@app.on_message(
filters.private &
~filters.command(
[
"start",
"stats"
]
)
)
async def ai_private(
client,
message
):

    add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    wait = await message.reply_text(
        "🤖 Thinking..."
    )

    reply = ask_ai(
        message.text
    )

    await wait.edit_text(
        reply
    )


@app.on_message(
filters.command("stats")
)
async def stats(
client,
message
):

    if (
        message.from_user.id
        != OWNER_ID
    ):
        return

    users = total_users()
    groups = total_groups()

    await message.reply_text(
f"""
📊 Prime X Statistics

👥 Users : {users}
🏘 Groups : {groups}

👨‍💻 Owner
@PREMGUPTA2M
"""
)


print(
"✅ Prime X Assistant Started"
)

keep_alive()

app.run()
