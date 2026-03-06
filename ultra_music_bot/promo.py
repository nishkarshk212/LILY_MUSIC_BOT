import os
import asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

async def _send(app, target, text, buttons=None):
    try:
        await app.send_message(
            target,
            text,
            reply_markup=buttons
        )
    except Exception:
        try:
            chat = await app.get_chat(target)
            await app.send_message(chat.id, text, reply_markup=buttons)
        except Exception:
            pass

async def _compose_bot_promo(app):
    me = await app.get_me()
    add_link = os.getenv("PROMO_BOT_LINK") or f"https://t.me/{me.username}?startgroup=true"
    support_link = os.getenv("SUPPORT_GROUP_LINK") or "https://t.me/Tele_212_bots"
    text = (
        "⚡ 𝗨𝗟𝗧𝗥𝗔 𝗩𝗖 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧\n\n"
        "🎶 Stream YouTube Music in Telegram Voice Chats\n"
        "⚡ Super Fast • Stable • Premium UI\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "🎧 Features\n\n"
        "• 🎵 Play YouTube Songs\n"
        "• 📜 Smart Queue System\n"
        "• 🎛 Premium Control Buttons\n"
        "• 🎬 Cinematic Thumbnails\n"
        "• 📊 Live Progress Bar\n"
        "• ⚡ Fast Streaming Engine\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "➕ Add Bot To Your Group\n"
        "👉\n\n"
        "💬 Join Official Support Group\n"
        "👉\n\n"
        "❝ Experience Music Like Never Before ❞"
    )
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Add Bot", url=add_link),
                InlineKeyboardButton("Support Group", url=support_link),
            ]
        ]
    )
    return text, buttons

async def _compose_group_promo():
    group_link = os.getenv("PROMO_GROUP_LINK") or "https://t.me/last_promise_chatting_212"
    text = (
        "╔══════════════════╗\n"
        "🎧           𝑱𝒐𝒊𝒏 𝑶𝒖𝒓 𝑮𝒓𝒐𝒖𝒑\n"
        "╚══════════════════╝\n\n"
        "🎵 Friendly Community\n"
        "💬 Active Members\n"
        "⚡ Daily Music Talks\n\n"
        "━━━━━━━━━━━━━━━\n\n"
        "👥 Join Our Group\n\n"
        "👉  Promo group link"
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Join Group", url=group_link)]
        ]
    )
    return text, buttons

async def _promo_loop(app, target, compose_callable, interval):
    while True:
        try:
            text, buttons = await compose_callable() if callable(compose_callable) else (compose_callable[0], compose_callable[1])
            await _send(app, target, text, buttons)
        except Exception:
            pass
        await asyncio.sleep(interval)

async def start_promo_scheduler(app):
    bot_target = (os.getenv("PROMO_BOT_TARGET") or "@log_x_bott").strip()
    group_target = (os.getenv("PROMO_GROUP_TARGET") or "").strip()
    bot_interval_str = (os.getenv("PROMO_BOT_INTERVAL_SECONDS") or os.getenv("PROMO_INTERVAL_SECONDS") or "14400").strip()
    group_interval_str = (os.getenv("PROMO_GROUP_INTERVAL_SECONDS") or "").strip()
    bot_interval = int(bot_interval_str) if bot_interval_str.isdigit() else 14400
    if bot_target:
        app.loop.create_task(_promo_loop(app, bot_target, lambda: _compose_bot_promo(app), bot_interval))
    if group_target and group_interval_str and group_interval_str.isdigit():
        app.loop.create_task(_promo_loop(app, group_target, _compose_group_promo, int(group_interval_str)))
