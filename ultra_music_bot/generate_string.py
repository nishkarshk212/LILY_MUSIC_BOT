
import asyncio
from pyrogram import Client
import config

async def gen_session():
    print("Generating Pyrogram Session String...")
    app = Client(
        "temp_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH
    )
    
    await app.start()
    s = await app.export_session_string()
    print("\nHERE IS YOUR SESSION STRING:\n")
    print(s)
    print("\nCopy it and paste it into config.py as SESSION_STRING")
    await app.stop()

if __name__ == "__main__":
    asyncio.run(gen_session())
