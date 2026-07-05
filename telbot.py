import os
import asyncio
from pyrogram import Client, filters

# এনভায়রনমেন্ট ভেরিয়েবল থেকে তথ্য নেওয়া
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
session_string = os.environ.get("SESSION_STRING")

# ক্লায়েন্ট তৈরি
app = Client(
    "auto_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    session_string=session_string
)

@app.on_message(filters.command("start_auto"))
async def start_auto(client, message):
    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.reply("ব্যবহারবিধি: `/start_auto [target] [message] [count] [interval]`")
        return
    
    target = args[1]
    text = args[2]
    count = int(args[3])
    interval = int(args[4])
    
    await message.reply(f"অটোমেশন শুরু: {target}-কে {count} বার মেসেজ দেওয়া হবে।")
    
    for i in range(count):
        try:
            await client.send_message(target, text)
            await asyncio.sleep(interval)
        except Exception as e:
            await message.reply(f"এরর: {str(e)}")
            break
            
    await message.reply("অটোমেশন সম্পন্ন।")

# মেইন লুপ
if __name__ == "__main__":
    app.run()
