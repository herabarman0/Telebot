import os
import asyncio
from pyrogram import Client, filters

# রেন্ডার থেকে তথ্য সংগ্রহ করা হচ্ছে
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")
session_string = os.environ.get("SESSION_STRING")

# ১. ইউজার ক্লায়েন্ট (আপনার নিজের অ্যাকাউন্টের জন্য - সেশন স্ট্রিং ব্যবহার করে)
user = Client("my_account", api_id=api_id, api_hash=api_hash, session_string=session_string)

# ২. বট ক্লায়েন্ট (বট টোকেনের জন্য)
bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# মেসেজ পাঠানোর লজিক
@bot.on_message(filters.command("send"))
async def send_msg(client, message):
    try:
        # কমান্ড ফরম্যাট: /send [username/id] [text]
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.reply("ব্যবহারবিধি: /send [username] [message]")
            return
            
        target = args[1]
        text = args[2]
        
        # নিজের অ্যাকাউন্ট দিয়ে মেসেজ পাঠানো
        await user.send_message(target, text)
        await message.reply(f"সফলভাবে {target}-কে মেসেজ পাঠানো হয়েছে!")
    except Exception as e:
        await message.reply(f"ভুল হয়েছে: {str(e)}")

# বট এবং ইউজার ক্লায়েন্ট একসাথে চালানো
async def main():
    await user.start()
    await bot.start()
    print("বট এবং ইউজারবট সফলভাবে চালু হয়েছে!")
    # বটটি যেন রেন্ডারে বন্ধ না হয়
    await asyncio.gather(asyncio.Event().wait())

if __name__ == "__main__":
    asyncio.run(main())
