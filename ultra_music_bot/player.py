
import config
from pyrogram import Client
from userbot import user
_PTG_V3 = False
try:
    from pytgcalls import GroupCallFactory
    from pytgcalls.types import StreamType
    from pytgcalls.types.input_stream import AudioPiped
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
if _PTG_V3:
    class CallAdapter:
        def __init__(self, client):
            self.client = client
            self.factory = GroupCallFactory(client)
            self.calls = {}
        def start(self):
            return None
        def stop(self):
            return None
        async def play(self, chat_id, stream_url):
            if chat_id not in self.calls:
                self.calls[chat_id] = self.factory.get_group_call()
                await self.calls[chat_id].join(chat_id, AudioPiped(stream_url), stream_type=StreamType().local_stream)
            else:
                await self.calls[chat_id].change_stream(AudioPiped(stream_url))
        async def change_stream(self, chat_id, stream_url):
            if chat_id in self.calls:
                await self.calls[chat_id].change_stream(AudioPiped(stream_url))
        async def pause(self, chat_id):
            if chat_id in self.calls:
                await self.calls[chat_id].pause_stream()
        async def resume(self, chat_id):
            if chat_id in self.calls:
                await self.calls[chat_id].resume_stream()
        async def leave_call(self, chat_id):
            if chat_id in self.calls:
                try:
                    await self.calls[chat_id].leave()
                finally:
                    self.calls.pop(chat_id, None)
        async def get_active_chats(self):
            return list(self.calls.keys())
    call = CallAdapter(user)
else:
    call = PyTgCalls(user)

async def start_stream(chat_id, stream):
    if _PTG_V3:
        await call.play(chat_id, stream)
    else:
        await call.play(chat_id, MediaStream(stream, audio_parameters=AudioQuality.HIGH))

async def change_stream(chat_id, stream):
    if _PTG_V3:
        await call.change_stream(chat_id, stream)
    else:
        await call.change_stream(chat_id, MediaStream(stream, audio_parameters=AudioQuality.HIGH))
