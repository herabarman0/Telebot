import os
import asyncio
from telethon import TelegramClient, events

# ১. রেন্ডার থেকে তথ্য সংগ্রহ
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
session_string = os.environ.get("SESSION_STRING")

# ২. ক্লায়েন্ট সেটআপ (Telethon)
client = TelegramClient(None, api_id, api_hash).start(session=session_string)

# ৩. অটোমেশন কমান্ড: /start_auto [target] [message] [count] [interval]
@client.on(events.NewMessage(pattern='/start_auto'))
async def start_auto(event):
    args = event.raw_text.split(maxsplit=4)
    if len(args) < 5:
        await event.reply("ব্যবহারবিধি: `/start_auto [target] [message] [count] [interval]`")
        return
    
    target = args[1]
    text = args[2]
    count = int(args[3])
    interval = int(args[4])
    
    await event.reply(f"✅ অটোমেশন শুরু: {target}-কে {count} বার মেসেজ দেওয়া হচ্ছে।")
    
    for i in range(count):
        try:
            await client.send_message(target, text)
            await asyncio.sleep(interval)
        except Exception as e:
            await event.reply(f"❌ এরর: {str(e)}")
            break
            
    await event.reply("🎉 অটোমেশন সম্পন্ন হয়েছে!")

# ৪. বট চালানো
print("বট সচল হয়েছে!")
client.run_until_disconnected()
