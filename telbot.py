import os
import asyncio
from pyrogram import Client, filters

# এনভায়রনমেন্ট ভেরিয়েবল থেকে ডাটা নেওয়া
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
session_string = os.environ.get("SESSION_STRING")

# ক্লায়েন্ট সেটআপ
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token, session_string=session_string)

# অটোমেশন ফাংশন
@app.on_message(filters.command("start_auto"))
async def start_auto(client, message):
    # কমান্ড ফরম্যাট: /start_auto [target] [message] [count] [interval]
    args = message.text.split(maxsplit=4)
    if len(args) < 5:
        await message.reply("ব্যবহারবিধি: `/start_auto [target] [message] [count] [interval]`\nউদাহরণ: `/start_auto @username হ্যালো 5 10` (৫ বার, ১০ সেকেন্ড পর পর)")
        return
    
    target = args[1]
    text = args[2]
    count = int(args[3])
    interval = int(args[4])
    
    await message.reply(f"✅ অটোমেশন শুরু হচ্ছে: {target}-কে {count} বার মেসেজ পাঠানো হবে।")
    
    for i in range(count):
        try:
            await app.send_message(target, text)
            await asyncio.sleep(interval) # নির্ধারিত সময় বিরতি
        except Exception as e:
            await message.reply(f"❌ এরর: {str(e)}")
            break
            
    await message.reply("🎉 অটোমেশন সম্পন্ন হয়েছে!")

async def main():
    await app.start()
    print("অটোমেশন বট সচল হয়েছে!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
