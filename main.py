"""
Prime X Assistant - Main Bot File
Owner: @PREMGUPTA2M
"""
import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
import asyncio
import time
import re
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    ChatPermissions
)
from pyrogram.errors import (
    UserNotParticipant, ChatAdminRequired, UserAdminInvalid,
    FloodWait, PeerIdInvalid
)
from pyrogram.enums import ChatMemberStatus, ChatType

from config import (
    BOT_TOKEN, API_ID, API_HASH, OWNER_ID,
    CHANNEL_LINK, GROUP_LINK, WELCOME_IMAGE
)
from database import (
    add_user, add_group, get_user_count, get_group_count,
    get_all_users, get_all_groups, add_strike, get_strikes,
    reset_strikes, get_moderation_logs, log_moderation,
    get_total_strikes, init_db, reset_old_strikes
)
from ai import get_ai_response, is_abusive_message

# ── Bot startup time ────────────────────────────────────────────────────────
START_TIME = time.time()

# ── Pyrogram Client ─────────────────────────────────────────────────────────
app = Client(
    "prime_x_assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ── Anti-flood tracker ──────────────────────────────────────────────────────
flood_tracker: dict = {}
duplicate_tracker: dict = {}

# ── Group AI keywords ───────────────────────────────────────────────────────
GROUP_KEYWORDS = [
    "bot", "telegram", "group", "channel", "earning", "earn",
    "income", "money", "review", "reviews", "map review",
    "google map", "google maps", "local guide", "rating",
    "help", "problem", "issue", "android", "app", "website",
    "hosting", "python", "coding", "developer", "ai", "gemini",
    "chatgpt", "support", "community", "social media", "growth",
    "promotion", "how", "kaise", "kya", "kyu", "kyon"
]

# ── Abusive keyword list (basic filter) ────────────────────────────────────
ABUSE_KEYWORDS = [
    "bc", "mc", "bhosdike", "madarchod", "bhenchod", "gaand",
    "chutiya", "harami", "kamina", "randi", "saala", "bkl",
    "lodu", "lauda", "fuck", "bitch", "asshole", "bastard",
    "shit", "motherfucker", "fucker", "dick", "pussy", "whore"
]


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def get_uptime() -> str:
    seconds = int(time.time() - START_TIME)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m {secs}s"


async def is_subscribed(client: Client, user_id: int) -> bool:
    try:
        channel_username = CHANNEL_LINK.split("/")[-1]
        if channel_username.startswith("+"):
            # Private invite link — can't verify without being admin; allow
            return True
        member = await client.get_chat_member(channel_username, user_id)
        return member.status not in [ChatMemberStatus.BANNED, ChatMemberStatus.LEFT]
    except UserNotParticipant:
        return False
    except Exception:
        return True


async def is_admin(client: Client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False


def force_subscribe_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("💬 Join Group", url=GROUP_LINK)
        ],
        [InlineKeyboardButton("✅ I've Joined — Try Again", callback_data="check_sub")]
    ])


def welcome_markup() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("💬 Group", url=GROUP_LINK)
        ],
        [InlineKeyboardButton("🤖 Start Chatting", callback_data="start_chat")]
    ])


# ═══════════════════════════════════════════════════════════════════════════
# /START COMMAND
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user = message.from_user
    add_user(user.id, user.first_name or "User")

    if not await is_subscribed(client, user.id):
        await message.reply_photo(
            photo=WELCOME_IMAGE,
            caption=(
                "🚫 **Access Denied!**\n\n"
                "Bhai, pehle humara **Channel** aur **Group** join karo,\n"
                "tabhi bot use kar paoge! 😊\n\n"
                "👇 Neeche diye buttons pe click karo:"
            ),
            reply_markup=force_subscribe_markup()
        )
        return

    welcome_text = (
        f"👋 **Hello {user.first_name}!**\n\n"
        "🤖 Main hoon **Prime X Assistant** — tera intelligent Hinglish AI bot!\n\n"
        "✨ **Main kya kar sakta hoon:**\n"
        "├ 💬 AI-powered conversations\n"
        "├ 🗺️ Google Maps & Local Guide help\n"
        "├ 💰 Online earning guidance\n"
        "├ 🤖 Telegram bot support\n"
        "├ 🐍 Python & coding help\n"
        "└ 📱 Tech support & more!\n\n"
        "💡 **Bas apna sawaal type karo — main ready hoon!**\n\n"
        f"👑 Owner: @PREMGUPTA2M"
    )

    await message.reply_photo(
        photo=WELCOME_IMAGE,
        caption=welcome_text,
        reply_markup=welcome_markup()
    )


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACK QUERIES
# ═══════════════════════════════════════════════════════════════════════════

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    user = callback_query.from_user

    if data == "check_sub":
        if await is_subscribed(client, user.id):
            await callback_query.answer("✅ Verified! Ab start karo.", show_alert=True)
            await start_command(client, callback_query.message)
        else:
            await callback_query.answer(
                "❌ Abhi join nahi kiya! Pehle join karo phir try karo.",
                show_alert=True
            )
    elif data == "start_chat":
        await callback_query.answer("💬 Apna sawaal type karo!", show_alert=False)


# ═══════════════════════════════════════════════════════════════════════════
# PRIVATE CHAT — AI RESPONSE
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.private & filters.text & ~filters.command(
    ["start", "stats", "broadcast", "gbroadcast", "strikes", "resetstrikes", "warns"]
))
async def private_ai_chat(client: Client, message: Message):
    user = message.from_user
    add_user(user.id, user.first_name or "User")

    if not await is_subscribed(client, user.id):
        await message.reply(
            "🚫 **Pehle join karo, bhai!**\n\nBot use karne ke liye channel & group join karna zaroori hai.",
            reply_markup=force_subscribe_markup()
        )
        return

    await client.send_chat_action(message.chat.id, "typing")
    processing_msg = await message.reply("⚡ _Processing..._")

    try:
        response = await get_ai_response(message.text)
        await processing_msg.edit_text(response)
    except Exception:
        await processing_msg.edit_text(
            "😅 Bhai, kuch technical issue aa gaya. Thoda baad mein try karo!"
        )


# ═══════════════════════════════════════════════════════════════════════════
# GROUP — AI + MODERATION
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.group & filters.text)
async def group_handler(client: Client, message: Message):
    if not message.text or not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.lower()

    add_group(chat_id, message.chat.title or "Group")
    add_user(user_id, message.from_user.first_name or "User")

    # ── Anti-flood ──────────────────────────────────────────────────────
    now = time.time()
    if user_id not in flood_tracker:
        flood_tracker[user_id] = []
    flood_tracker[user_id] = [t for t in flood_tracker[user_id] if now - t < 5]
    flood_tracker[user_id].append(now)

    if len(flood_tracker[user_id]) > 8:
        if not await is_admin(client, chat_id, user_id):
            try:
                await message.delete()
                await message.reply(
                    f"⚠️ {message.from_user.mention} bhai, **itna fast mat bhejo!** Thoda slow down karo. 🙏"
                )
            except Exception:
                pass
            return

    # ── Duplicate message detection ─────────────────────────────────────
    chat_key = f"{chat_id}_{user_id}"
    if chat_key not in duplicate_tracker:
        duplicate_tracker[chat_key] = []
    duplicate_tracker[chat_key] = [
        (t, m) for t, m in duplicate_tracker[chat_key] if now - t < 30
    ]
    recent_texts = [m for _, m in duplicate_tracker[chat_key]]
    if recent_texts.count(text) >= 2:
        if not await is_admin(client, chat_id, user_id):
            try:
                await message.delete()
            except Exception:
                pass
            return
    duplicate_tracker[chat_key].append((now, text))

    # ── Link spam detection ─────────────────────────────────────────────
    link_pattern = re.compile(r"(https?://|t\.me/|@\w+)")
    if len(link_pattern.findall(message.text)) > 3 and not await is_admin(client, chat_id, user_id):
        try:
            await message.delete()
            await message.reply(
                f"🚫 {message.from_user.mention}, **itne saare links mat bhejo!** Spam allowed nahi hai. ⚠️"
            )
        except Exception:
            pass
        return

    # ── AI Moderation ───────────────────────────────────────────────────
    if not await is_admin(client, chat_id, user_id):
        is_abuse = any(kw in text.split() for kw in ABUSE_KEYWORDS)
        if not is_abuse:
            is_abuse = await is_abusive_message(message.text)

        if is_abuse:
            try:
                await message.delete()
            except Exception:
                pass

            strikes = add_strike(user_id, chat_id)
            log_moderation(user_id, chat_id, message.text[:200], strikes)

            strike_messages = {
                1: ("⚠️ **Warning 1/5**\n\nBhai, respectful language use karo please. 🙏", False),
                2: ("⚠️ **Warning 2/5**\n\nAbusive language se bacho. Aage rules break hua toh action liya jayega.", False),
                3: ("⚠️ **Warning 3/5**\n\nYe teri 3rd warning hai! Aage violations pe restriction aa sakti hai.", False),
                4: ("⚠️ **Warning 4/5**\n\nBhai, ek aur violation aur automatic mute ho jayega! 😤", False),
                5: ("🚫 **Strike 5/5 — Muted!**\n\nRules tod diye baar baar. **24 ghante ke liye mute** kar diya gaya hai.", True),
            }

            strike_level = min(strikes, 5)
            warn_text, do_mute = strike_messages[strike_level]
            await message.reply(f"{message.from_user.mention}\n\n{warn_text}")

            if do_mute:
                try:
                    mute_until = datetime.now() + timedelta(hours=24)
                    await client.restrict_chat_member(
                        chat_id, user_id,
                        ChatPermissions(can_send_messages=False),
                        until_date=mute_until
                    )
                    reset_strikes(user_id, chat_id)
                except (ChatAdminRequired, UserAdminInvalid):
                    await message.reply("⚠️ Bot ko admin rights chahiye mute karne ke liye!")
            return

    # ── Group AI Reply ──────────────────────────────────────────────────
    bot_mentioned = False
    if message.entities:
        for entity in message.entities:
            if entity.type.name == "MENTION":
                mention_text = message.text[entity.offset: entity.offset + entity.length]
                me = await client.get_me()
                if me.username and f"@{me.username}".lower() == mention_text.lower():
                    bot_mentioned = True
                    break

    reply_to_bot = False
    if message.reply_to_message and message.reply_to_message.from_user:
        me = await client.get_me()
        if message.reply_to_message.from_user.id == me.id:
            reply_to_bot = True

    keyword_match = any(kw in text for kw in GROUP_KEYWORDS)

    if bot_mentioned or reply_to_bot or keyword_match:
        await client.send_chat_action(chat_id, "typing")
        try:
            response = await get_ai_response(message.text)
            await message.reply(response)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("stats") & filters.user([OWNER_ID]))
async def stats_command(client: Client, message: Message):
    await message.reply(
        "📊 **Prime X Assistant — Stats**\n\n"
        f"👥 **Total Users:** `{get_user_count()}`\n"
        f"🏘️ **Total Groups:** `{get_group_count()}`\n"
        f"⚠️ **Total Strikes:** `{get_total_strikes()}`\n"
        f"⏱️ **Uptime:** `{get_uptime()}`\n\n"
        f"👑 Owner: @PREMGUPTA2M"
    )


@app.on_message(filters.command("broadcast") & filters.user([OWNER_ID]))
async def broadcast_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("📢 Jo message broadcast karna hai usse **reply** karke `/broadcast` use karo.")
        return

    broadcast_msg = message.reply_to_message
    users = get_all_users()
    success, failed = 0, 0
    status_msg = await message.reply(f"📤 Broadcasting to `{len(users)}` users...")

    for user_id in users:
        try:
            await broadcast_msg.copy(user_id)
            success += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ **Broadcast Complete!**\n\n✔️ Success: `{success}`\n❌ Failed: `{failed}`"
    )


@app.on_message(filters.command("gbroadcast") & filters.user([OWNER_ID]))
async def gbroadcast_command(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply("📢 Jo message broadcast karna hai usse **reply** karke `/gbroadcast` use karo.")
        return

    broadcast_msg = message.reply_to_message
    groups = get_all_groups()
    success, failed = 0, 0
    status_msg = await message.reply(f"📤 Broadcasting to `{len(groups)}` groups...")

    for group_id in groups:
        try:
            await broadcast_msg.copy(group_id)
            success += 1
            await asyncio.sleep(0.05)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ **Group Broadcast Complete!**\n\n✔️ Success: `{success}`\n❌ Failed: `{failed}`"
    )


# ═══════════════════════════════════════════════════════════════════════════
# STRIKE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.command("strikes"))
async def strikes_command(client: Client, message: Message):
    strikes = get_strikes(message.from_user.id, message.chat.id)
    await message.reply(
        f"⚠️ **Strike Status**\n\n"
        f"👤 User: {message.from_user.mention}\n"
        f"📊 Strikes: `{strikes}/5`\n\n"
        f"{'🟢 Safe — Koi strike nahi!' if strikes == 0 else '🔴 Careful bhai!'}"
    )


@app.on_message(filters.command("resetstrikes"))
async def reset_strikes_command(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply("❌ Sirf admins yeh command use kar sakte hain.")
        return
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    reset_strikes(target.id, message.chat.id)
    await message.reply(f"✅ {target.mention} ke strikes reset kar diye gaye!")


@app.on_message(filters.command("warns"))
async def warns_command(client: Client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        await message.reply("❌ Sirf admins yeh command use kar sakte hain.")
        return
    logs = get_moderation_logs(message.chat.id, limit=10)
    if not logs:
        await message.reply("✅ Koi moderation logs nahi mili.")
        return
    log_text = "📋 **Recent Moderation Logs**\n\n"
    for uid, content, strike, ts in logs:
        log_text += (
            f"👤 User: `{uid}`\n⚠️ Strike: `{strike}`\n"
            f"💬 Message: _{content[:60]}..._\n🕐 Time: `{ts}`\n──────────────\n"
        )
    await message.reply(log_text)


# ═══════════════════════════════════════════════════════════════════════════
# BOT ADDED TO GROUP
# ═══════════════════════════════════════════════════════════════════════════

@app.on_message(filters.new_chat_members)
async def new_member_handler(client: Client, message: Message):
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            chat = message.chat
            add_group(chat.id, chat.title or "Group")
            await message.reply(
                "👋 **Hello Everyone!**\n\n"
                "Main hoon **Prime X Assistant** — ab is group mein aa gaya hoon!\n\n"
                "✅ **Kya kar sakta hoon:**\n"
                "• AI-powered answers\n• Group moderation\n"
                "• Anti-spam & anti-flood\n• Strike system\n\n"
                f"📢 Channel: [Join Karo]({CHANNEL_LINK})\n"
                f"💬 Main Group: [Join Karo]({GROUP_LINK})\n\n"
                "👑 Owner: @PREMGUPTA2M",
                disable_web_page_preview=True
            )
        else:
            add_user(member.id, member.first_name or "User")
