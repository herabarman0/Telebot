import os
import asyncio
from pyrogram import Client, filters

# রেন্ডার থেকে তথ্য গ্রহণ
api_id = int(os.environ.get("API_ID"))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

# ক্লায়েন্ট সেটআপ
# User account client (নিজের অ্যাকাউন্টের জন্য)
user = Client("my_account", api_id=api_id, api_hash=api_hash)
# Bot client (বট টোকেনের জন্য)
bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("আমি প্রস্তুত! যেকোনো মেসেজ পাঠানোর জন্য /send [username] [message] কমান্ডটি ব্যবহার করুন।")

@bot.on_message(filters.command("send"))
async def send_msg(client, message):
    try:
        # কমান্ড ফরম্যাট: /send [username] [text]
        args = message.text.split(maxsplit=2)
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
    print("বট সফলভাবে চালু হয়েছে!")
    await asyncio.gather(asyncio.Event().wait()) # প্রোগ্রামটি বন্ধ না করার জন্য

if __name__ == "__main__":
    asyncio.run(main())
