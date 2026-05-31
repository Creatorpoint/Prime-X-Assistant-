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
@app.on_message(filters.group)
async def save_group_handler(client, message):

    add_group(
        message.chat.id,
        message.chat.title
    )


@app.on_message(
    filters.private &
    ~filters.command(
        [
            "start",
            "stats",
            "broadcast",
            "gbroadcast"
        ]
    )
)
async def ai_private(client, message):

    add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    wait = await message.reply_text(
        "🤖 Thinking..."
    )

    try:
        reply = ask_ai(
            message.text
        )

        await wait.edit_text(reply)

    except Exception as e:

        await wait.edit_text(
            f"❌ Error:\n{e}"
        )


@app.on_message(
    filters.group &
    filters.text
)
async def group_ai(client, message):

    add_group(
        message.chat.id,
        message.chat.title
    )

    text = message.text.lower()

    keywords = [
        "bot",
        "telegram",
        "earning",
        "help",
        "problem",
        "issue",
        "app",
        "android",
        "channel",
        "group",
        "kaise",
        "kya",
        "kyu",
        "how"
    ]

    if any(
        word in text
        for word in keywords
    ):

        try:

            reply = ask_ai(
                message.text
            )

            await message.reply_text(
                reply
            )

        except:
            pass


@app.on_message(
    filters.command("stats")
)
async def stats(client, message):

    if message.from_user.id != OWNER_ID:
        return

    users = total_users()
    groups = total_groups()

    await message.reply_text(
f"""
📊 Prime X Statistics

👥 Users : {users}
🏘 Groups : {groups}

👨‍💻 Owner : @PREMGUPTA2M
"""
    )


@app.on_message(
    filters.command("broadcast")
)
async def broadcast(client, message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/broadcast message"
        )

    text = message.text.split(
        None,
        1
    )[1]

    sent = 0

    for user in all_users():

        try:

            await client.send_message(
                user[0],
                text
            )

            sent += 1

        except:
            pass

    await message.reply_text(
        f"✅ Broadcast Sent To {sent} Users"
    )


@app.on_message(
    filters.command("gbroadcast")
)
async def gbroadcast(client, message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 2:
        return await message.reply_text(
            "Usage:\n/gbroadcast message"
        )

    text = message.text.split(
        None,
        1
    )[1]

    sent = 0

    for group in all_groups():

        try:

            await client.send_message(
                group[0],
                text
            )

            sent += 1

        except:
            pass

    await message.reply_text(
        f"✅ Broadcast Sent To {sent} Groups"
    )


print(
    "✅ Prime X Assistant Started"
)

keep_alive()

app.run()

