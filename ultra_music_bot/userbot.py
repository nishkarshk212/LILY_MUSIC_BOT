
import config
from pyrogram import Client

user = Client(
    "user_client",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING
)
