
import config
from pyrogram import Client
from userbot import user
try:
    from pytgcalls import PyTgCalls
    from pytgcalls.types import MediaStream, AudioQuality
    _PTG_V3 = False
except Exception:
    try:
        from pytgcalls import GroupCall as PyTgCalls
        from pytgcalls.types import MediaStream, AudioQuality
        _PTG_V3 = True
    except Exception:
        from pytgcalls import PyTgCalls
        from pytgcalls.types import MediaStream, AudioQuality
        _PTG_V3 = False

app = Client(
    config.SESSION,
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Use user client for PyTgCalls to allow group calls
call = PyTgCalls(user)

async def start_stream(chat_id, stream):
    await call.play(
        chat_id,
        MediaStream(stream, audio_parameters=AudioQuality.HIGH),
    )

async def change_stream(chat_id, stream):
    await call.change_stream(
        chat_id,
        MediaStream(stream, audio_parameters=AudioQuality.HIGH),
    )
