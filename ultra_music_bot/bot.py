
from pyrogram import filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch
import yt_dlp
import asyncio
import logging
from promo import start_promo_scheduler

from player import app, call, start_stream, change_stream, user
from queues import add_to_queue, get_next_song, get_queue, clear_queue as clear_queue_db
from utils.thumbnail import generate_thumb
from utils.ui import premium_join_animation, get_progress_bar, format_duration

# Store duration for progress bar
PLAYING = {}
PROGRESS_TASKS = {}
LOG_CHANNELS = ["log_x_bott", "last_promise_chatting_212"]

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

async def send_logs(text):
    for ch in LOG_CHANNELS:
        try:
            await app.send_message(f"@{ch}", text)
        except Exception:
            pass

async def hourly_status():
    while True:
        try:
            active = []
            try:
                active = await call.get_active_chats()
            except Exception:
                active = []
            total_playing = len(PLAYING)
            total_queued = sum(len(get_queue(cid)) for cid in list(get_queue.__globals__["QUEUE"].keys())) if "QUEUE" in get_queue.__globals__ else 0
            text = f"Status Update\nActive Calls: {len(active)}\nPlaying: {total_playing}\nQueued: {total_queued}"
            logging.info(text)
            await send_logs(text)
        except Exception:
            pass
        await asyncio.sleep(3600)

async def six_hour_maintenance():
    while True:
        try:
            # Cancel progress tasks
            for cid, task in list(PROGRESS_TASKS.items()):
                try:
                    task.cancel()
                except Exception:
                    pass
                PROGRESS_TASKS.pop(cid, None)
            # Leave active calls
            try:
                active = await call.get_active_chats()
            except Exception:
                active = []
            for cid in active:
                try:
                    await call.leave_call(cid)
                except Exception:
                    pass
            # Clear queues
            try:
                q = get_queue.__globals__.get("QUEUE", {})
                for cid in list(q.keys()):
                    try:
                        q[cid] = []
                    except Exception:
                        pass
            except Exception:
                pass
            # Reset playing state
            PLAYING.clear()
            # Truncate log file
            try:
                with open("bot.log", "w", encoding="utf-8") as f:
                    f.write("")
            except Exception:
                pass
            msg = "Maintenance Reset Completed\nAll calls left, queues cleared, tasks cancelled."
            logging.info(msg)
            await send_logs(msg)
        except Exception:
            pass
        await asyncio.sleep(6 * 3600)

def parse_duration_to_seconds(d):
    if not d:
        return 0
    parts = [int(p) for p in d.split(":")]
    if len(parts) == 3:
        return parts[0]*3600 + parts[1]*60 + parts[2]
    if len(parts) == 2:
        return parts[0]*60 + parts[1]
    return parts[0]

async def live_slider(client, chat_id, message_id, title, duration):
    current = 0
    while current <= duration or duration == 0:
        bar = get_progress_bar(current, duration)
        label = f"{format_duration(current)} {bar} {format_duration(duration)}"
        buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(label, callback_data="progress")],
                [
                    InlineKeyboardButton("▶︎", callback_data="resume"),
                    InlineKeyboardButton("=", callback_data="pause"),
                    InlineKeyboardButton("❏", callback_data="stop"),
                ],
            ]
        )
        try:
            await client.edit_message_reply_markup(
                chat_id,
                message_id,
                reply_markup=buttons
            )
        except Exception:
            pass
        await asyncio.sleep(5)
        if duration == 0:
            current += 5
        else:
            current = min(current + 5, duration)

@app.on_message(filters.command("start"))
async def start(client, message):
    me = await client.get_me()
    user_name = message.from_user.first_name
    bot_name = me.first_name
    boot = await message.reply_text("⚡ Initializing Music Engine...")
    await asyncio.sleep(1.5)
    await boot.edit("🎧 Connecting Voice Chat System...")
    await asyncio.sleep(1.5)
    await boot.edit("🎶 Loading Streaming Modules...")
    await asyncio.sleep(1.5)
    await boot.delete()
    caption = f"""<blockquote>нєу {user_name}, 🥀</blockquote>

๏ ᴛʜɪs ɪs ❛ {bot_name} ❜ !

➻ ᴀ ғᴀsᴛ & ᴘᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜsɪᴄ ᴘʟᴀʏᴇʀ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs.

──────────────────
๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs."""
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("𝐀𝐝𝐝 𝐦𝐞", url=f"https://t.me/{me.username}?startgroup=true"),
                InlineKeyboardButton("𝐇𝐞𝐥𝐩", callback_data="help"),
            ],
            [
                InlineKeyboardButton("𝐂𝐨𝐦𝐦𝐚𝐧𝐝", callback_data="commands"),
                InlineKeyboardButton("𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url="https://t.me/Tele_212_bots"),
            ],
            [
                InlineKeyboardButton("𝐎𝐰𝐧𝐞𝐫", url="https://t.me/Jayden_212"),
            ],
        ]
    )
    try:
        photos = await client.get_profile_photos(me.id, limit=1)
        if photos and len(photos) > 0:
            await message.reply_photo(
                photo=photos[0].file_id,
                caption=caption,
                reply_markup=buttons,
                has_spoiler=True,
                parse_mode=ParseMode.HTML,
            )
            logging.info(f"Start used by {user_name}")
            return
    except Exception:
        pass
    await message.reply_text(caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
    logging.info(f"Start used by {user_name}")

@app.on_message(filters.command("play"))
async def play(client, message):
    if len(message.command) < 2:
        return await message.reply("Give song name")

    query = message.text.split(None,1)[1]
    
    # Animation
    wait_msg = await premium_join_animation(message, query)

    search = VideosSearch(query, limit=1).result()
    video = search["result"][0]

    title = video["title"]
    duration_str = video["duration"]
    thumb = video["thumbnails"][-1]["url"]
    url = video["link"]
    
    # Extract additional info
    channel = video.get("channel", {}).get("name", "Unknown Artist")
    views = video.get("viewCount", {}).get("short", "N/A Views")

    ydl_opts = {
        "format": "bestaudio",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream = info["url"]
        
    song = {
        "title": title,
        "stream": stream,
        "thumb": thumb,
        "channel": channel,
        "views": views,
        "duration": duration_str,
        "url": url,
        "user": message.from_user.mention
    }

    # Add to queue logic
    chat_id = message.chat.id
    try:
        await app.get_chat(chat_id)
    except Exception:
        pass
    
    # Check if there is an active playback for this chat
    is_playing = chat_id in PLAYING
    if not is_playing:
        try:
            active_calls = await call.get_active_chats()
            if chat_id in active_calls:
                is_playing = True
        except Exception:
            pass
    
    if is_playing:
        position = add_to_queue(chat_id, song)
        await wait_msg.delete()
        queued_caption = f"""<blockquote>🎵 Added to Queue</blockquote>

🅣🅘🅣🅛🅔 : {title}
🅓🅤🅡🅐🅣🅘🅞🅝 : {duration_str}
🅡🅔🅠🅤🅔🅢🅣🅔🅓 🅑🅨 : {message.from_user.first_name}

𝔼𝕟𝕛𝕠𝕪 𝕒𝕟𝕕 𝕘𝕖𝕥 𝕞𝕠𝕣𝕖 𝕙𝕖𝕣𝕖 @Tele_212_bots"""
        close_buttons = InlineKeyboardMarkup([[InlineKeyboardButton("✖︎", callback_data="close")]])
        resp = await message.reply_photo(
            photo=thumb,
            caption=queued_caption,
            reply_markup=close_buttons,
            parse_mode=ParseMode.HTML
        )
        logging.info(f"Queued in {message.chat.id}: {title} by {message.from_user.first_name} pos {position}")
        await send_logs(f"Queued: {title}\nChat: {message.chat.title if message.chat and message.chat.title else message.chat.id}\nBy: {message.from_user.first_name}\nPosition: {position}")
        return resp

    # If not playing, play immediately

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⏮",callback_data="prev"),
                InlineKeyboardButton("⏯",callback_data="pause"),
                InlineKeyboardButton("⏭",callback_data="skip")
            ],
            [
                InlineKeyboardButton("� Queue",callback_data="queue"),
                InlineKeyboardButton("�� Loop",callback_data="loop"),
                InlineKeyboardButton("🔀 Shuffle",callback_data="shuffle")
            ],
            [
                InlineKeyboardButton("❌ Close",callback_data="close")
            ]
        ]
    )
    
    caption = f"""<blockquote>⚡ Started Streaming by ‘{(await client.get_me()).first_name}’.</blockquote>

🅣🅘🅣🅛🅔 : {title}
🅓🅤🅡🅐🅣🅘🅞🅝 : {duration_str}
🅡🅔🅠🅤🅔🅢🅣🅔🅓 🅑🅨 : {message.from_user.first_name}

𝔼𝕟𝕛𝕠𝕪 𝕒𝕟𝕕 𝕘𝕖𝕥 𝕞𝕠𝕣𝕖 𝕙𝕖𝕣𝕖 @Tele_212_bots"""

    await wait_msg.delete()
    duration_seconds = parse_duration_to_seconds(duration_str)
    bar_init = get_progress_bar(0, duration_seconds)
    label_init = f"{format_duration(0)} {bar_init} {format_duration(duration_seconds)}"
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(label_init, callback_data="progress")],
            [
                InlineKeyboardButton("▶︎", callback_data="resume"),
                InlineKeyboardButton("=", callback_data="pause"),
                InlineKeyboardButton("❏", callback_data="stop"),
            ],
        ]
    )
    msg = await message.reply_photo(
        photo=thumb_path,
        caption=caption,
        reply_markup=buttons,
        parse_mode=ParseMode.HTML
    )

    await start_stream(message.chat.id, stream)
    PLAYING[chat_id] = {**song, "message_id": msg.id}
    task = asyncio.create_task(live_slider(app, message.chat.id, msg.id, title, duration_seconds))
    PROGRESS_TASKS[chat_id] = task
    logging.info(f"Started streaming in {message.chat.id}: {title} by {message.from_user.first_name}")
    await send_logs(f"Started Streaming\nChat: {message.chat.title if message.chat and message.chat.title else message.chat.id}\nSong: {title}\nBy: {message.from_user.first_name}")

@app.on_message(filters.command("skip"))
async def skip_msg(client, message):
    chat_id = message.chat.id
    await skip_song(chat_id, message)

async def skip_song(chat_id, message_obj=None):
    next_song_data = get_next_song(chat_id)
    
    if not next_song_data:
        await call.leave_call(chat_id)
        if message_obj:
            await message_obj.reply("Queue ended")
        logging.info(f"Left call in {chat_id}")
        await send_logs(f"Left Voice Chat\nChat: {chat_id}")
        return
    if chat_id in PROGRESS_TASKS:
        try:
            PROGRESS_TASKS[chat_id].cancel()
        except Exception:
            pass
        del PROGRESS_TASKS[chat_id]

    await change_stream(chat_id, next_song_data["stream"])
    prev_msg_id = None
    if chat_id in PLAYING and "message_id" in PLAYING[chat_id]:
        prev_msg_id = PLAYING[chat_id]["message_id"]
    PLAYING[chat_id] = {**next_song_data, "message_id": prev_msg_id}
    try:
        if prev_msg_id:
            duration_seconds = parse_duration_to_seconds(next_song_data.get("duration", "0"))
            bar_init = get_progress_bar(0, duration_seconds)
            label_init = f"{format_duration(0)} {bar_init} {format_duration(duration_seconds)}"
            buttons = InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(label_init, callback_data="progress")],
                    [
                        InlineKeyboardButton("▶︎", callback_data="resume"),
                        InlineKeyboardButton("=", callback_data="pause"),
                        InlineKeyboardButton("❏", callback_data="stop"),
                    ],
                ]
            )
            caption = f"""
“⚡ Started Streaming by {(await app.get_me()).first_name}:”

🅣🅘🅣🅛🅔 : {next_song_data['title']}
🅓🅤🅡🅐🅣🅘🅞🅝 : {next_song_data.get('duration','Live')}
🅡🅔🅠🅤🅔🅢🅣🅔🅓 🅑🅨 : {next_song_data.get('user','Unknown')}

𝔼𝕟𝕛𝕠𝕪 𝕒𝕟𝕕 𝕘𝕖𝕥 𝕞𝕠𝕣𝕖 𝕙𝕖𝕣𝕖 @Tele_212_bots
"""
            await app.edit_message_caption(chat_id, prev_msg_id, caption=caption, reply_markup=buttons, parse_mode=ParseMode.HTML)
            task = asyncio.create_task(live_slider(app, chat_id, prev_msg_id, next_song_data['title'], duration_seconds))
            PROGRESS_TASKS[chat_id] = task
    except Exception:
        pass
    
    if message_obj:
        await message_obj.reply(f"⏭ **Skipped! Playing Next:**\n\n🎵 {next_song_data['title']}")

@app.on_message(filters.command("queue"))
async def show_queue(client, message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    if not queue:
        return await message.reply("📭 Queue is empty")
    
    text = "📜 **Music Queue**\n\n"
    for i, song in enumerate(queue):
        text += f"{i+1}. {song['title']}\n"
    
    await message.reply(text)

@app.on_message(filters.command("clear"))
async def clear_queue_cmd(client, message):
    chat_id = message.chat.id
    clear_queue_db(chat_id)
    await message.reply("🗑 Queue cleared")

@app.on_callback_query()
async def controls(client, query):
    data = query.data
    chat_id = query.message.chat.id

    if data == "pause":
        await call.pause(chat_id)
        await query.answer("Paused")
        
    elif data == "resume": # Added resume handling
        await call.resume(chat_id)
        await query.answer("Resumed")

    elif data == "skip":
        await query.answer("Skipped")
        await skip_song(chat_id, query.message)

    elif data == "close":
        await query.message.delete()
        
    elif data == "stop":
        if chat_id in PROGRESS_TASKS:
            try:
                PROGRESS_TASKS[chat_id].cancel()
            except Exception:
                pass
            del PROGRESS_TASKS[chat_id]
        try:
            await call.leave_call(chat_id)
        except Exception:
            pass
        try:
            await query.message.delete()
        except Exception:
            pass
        await query.answer("Stopped")
        try:
            logging.info(f"Stopped streaming in {chat_id}")
            await send_logs(f"Stopped Streaming\nChat: {chat_id}")
        except Exception:
            pass
        
    elif data == "queue":
        queue = get_queue(chat_id)
        if not queue:
            await query.answer("Queue is empty", show_alert=True)
        else:
            text = "📜 **Music Queue**\n\n"
            for i, song in enumerate(queue):
                text += f"{i+1}. {song['title']}\n"
            await query.message.reply(text)
    elif data == "help":
        await query.message.reply("Use /play <song name>, /skip, /queue, /clear")
        await query.answer()
    elif data == "commands":
        await query.message.reply("Commands:\n/play <name>\n/skip\n/queue\n/clear")
        await query.answer()

if __name__ == "__main__":
    app.start()
    user.start()
    call.start()
    try:
        for ch in LOG_CHANNELS:
            try:
                asyncio.get_event_loop().run_until_complete(app.get_chat(f"@{ch}"))
            except Exception:
                pass
        app.loop.create_task(hourly_status())
        app.loop.create_task(six_hour_maintenance())
        app.loop.create_task(start_promo_scheduler(app))
    except Exception:
        pass
    print("Music Bot Started")
    idle()
    call.stop()
    user.stop()
    app.stop()
