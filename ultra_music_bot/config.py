
import os
from dotenv import load_dotenv
import pyrogram.errors

# Patch for pytgcalls compatibility
if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    class GroupcallForbidden(pyrogram.errors.Forbidden):
        pass
    pyrogram.errors.GroupcallForbidden = GroupcallForbidden

load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SESSION_STRING = os.getenv("SESSION_STRING", "")
SESSION = os.getenv("SESSION", "ultra_music_bot_session")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
USERBOT_ENABLED = os.getenv("USERBOT_ENABLED", "0") == "1"
