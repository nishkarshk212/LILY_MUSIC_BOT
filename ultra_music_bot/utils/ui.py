
import asyncio

async def premium_join_animation(message, song_title):
    msg = await message.reply("🎧 Connecting to Voice Chat...")
    frames = [
        "🎧 Connecting to Voice Chat ▱▱▱▱▱",
        "🎧 Connecting to Voice Chat ▰▱▱▱▱",
        "🎧 Connecting to Voice Chat ▰▰▱▱▱",
        "🎧 Connecting to Voice Chat ▰▰▰▱▱",
        "🎧 Connecting to Voice Chat ▰▰▰▰▱",
        "🎧 Connected ✔",
        f"🎶 Loading **{song_title}**..."
    ]
    for frame in frames:
        await msg.edit(frame)
        await asyncio.sleep(0.4)
    return msg

def get_progress_bar(current, total):
    bar_length = 15
    if total == 0:
        filled = 0
    else:
        filled = int(bar_length * current / total)
    
    bar = "━" * filled + "●" + "─" * (bar_length - filled)
    return f"{bar}"

def format_duration(seconds):
    if seconds == 0:
        return "Live"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"
