import os
import asyncio
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

# ==== এনভায়রনমেন্ট ভেরিয়েবল ====
api_id = int(os.environ.get("API_ID", 0))
api_hash = os.environ.get("API_HASH")
bot_token = os.environ.get("BOT_TOKEN")

if not api_id or not api_hash or not bot_token:
    raise SystemExit("API_ID, API_HASH, BOT_TOKEN environment variable সেট করা নেই।")

# ==== বট ক্লায়েন্ট (bot_token দিয়ে, session_string লাগবে না) ====
app = Client(
    "reminder_bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
)

scheduler = AsyncIOScheduler()

# প্রতি ইউজারের রিমাইন্ডার মেমরিতে রাখা হচ্ছে (সহজ ভার্সন, সার্ভার রিস্টার্ট হলে মুছে যাবে)
# চাইলে পরে Firebase/SQLite দিয়ে persistent করা যাবে
user_reminders = {}  # {user_id: [ {job_id, text, when_str} ]}


async def send_reminder(chat_id: int, text: str):
    try:
        await app.send_message(chat_id, f"⏰ রিমাইন্ডার: {text}")
    except Exception as e:
        print(f"রিমাইন্ডার পাঠাতে সমস্যা: {e}")


@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply(
        "স্বাগতম! আমি একটা রিমাইন্ডার বট।\n\n"
        "ব্যবহারবিধি:\n"
        "`/remind <মিনিট> <মেসেজ>` — নির্দিষ্ট মিনিট পর একবার রিমাইন্ড করবে\n"
        "উদাহরণ: `/remind 30 পানি খাও`\n\n"
        "`/dailyremind <HH:MM> <মেসেজ>` — প্রতিদিন এই সময়ে রিমাইন্ড করবে (24-ঘণ্টা ফরম্যাট)\n"
        "উদাহরণ: `/dailyremind 21:30 ওষুধ খাও`\n\n"
        "`/myreminders` — আপনার সেট করা রিমাইন্ডার তালিকা\n"
        "`/cancelreminder <নাম্বার>` — নির্দিষ্ট রিমাইন্ডার বাতিল করুন"
    )


@app.on_message(filters.command("remind"))
async def remind_once(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("ব্যবহারবিধি: `/remind <মিনিট> <মেসেজ>`\nউদাহরণ: `/remind 30 পানি খাও`")
        return

    try:
        minutes = int(args[1])
        if minutes <= 0:
            raise ValueError
    except ValueError:
        await message.reply("মিনিট অবশ্যই একটা পজিটিভ সংখ্যা হতে হবে। উদাহরণ: `/remind 30 পানি খাও`")
        return

    text = args[2]
    chat_id = message.chat.id
    run_time = datetime.now() + timedelta(minutes=minutes)

    job = scheduler.add_job(
        send_reminder,
        trigger=DateTrigger(run_date=run_time),
        args=[chat_id, text],
    )

    user_reminders.setdefault(chat_id, []).append({
        "job_id": job.id,
        "text": text,
        "when": run_time.strftime("%Y-%m-%d %H:%M"),
        "type": "একবার",
    })

    await message.reply(f"ঠিক আছে! {minutes} মিনিট পর ({run_time.strftime('%H:%M')}) আপনাকে মনে করিয়ে দেব: \"{text}\"")


@app.on_message(filters.command("dailyremind"))
async def remind_daily(client: Client, message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("ব্যবহারবিধি: `/dailyremind <HH:MM> <মেসেজ>`\nউদাহরণ: `/dailyremind 21:30 ওষুধ খাও`")
        return

    time_str = args[1]
    text = args[2]
    chat_id = message.chat.id

    try:
        hour, minute = map(int, time_str.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await message.reply("সময় ফরম্যাট ভুল। HH:MM ফরম্যাটে দিন, উদাহরণ: `21:30`")
        return

    job = scheduler.add_job(
        send_reminder,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[chat_id, text],
    )

    user_reminders.setdefault(chat_id, []).append({
        "job_id": job.id,
        "text": text,
        "when": f"প্রতিদিন {time_str}",
        "type": "দৈনিক",
    })

    await message.reply(f"ঠিক আছে! প্রতিদিন {time_str}-এ আপনাকে মনে করিয়ে দেব: \"{text}\"")


@app.on_message(filters.command("myreminders"))
async def list_reminders(client: Client, message: Message):
    chat_id = message.chat.id
    reminders = user_reminders.get(chat_id, [])

    if not reminders:
        await message.reply("আপনার কোনো রিমাইন্ডার সেট করা নেই।")
        return

    lines = ["আপনার রিমাইন্ডার তালিকা:\n"]
    for idx, r in enumerate(reminders, start=1):
        lines.append(f"{idx}. [{r['type']}] {r['when']} — \"{r['text']}\"")
    lines.append("\nবাতিল করতে: `/cancelreminder <নাম্বার>`")

    await message.reply("\n".join(lines))


@app.on_message(filters.command("cancelreminder"))
async def cancel_reminder(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    chat_id = message.chat.id
    reminders = user_reminders.get(chat_id, [])

    if len(args) < 2 or not reminders:
        await message.reply("বাতিল করার মতো কোনো রিমাইন্ডার নেই বা নাম্বার দেওয়া হয়নি।")
        return

    try:
        idx = int(args[1]) - 1
        if idx < 0 or idx >= len(reminders):
            raise IndexError
    except (ValueError, IndexError):
        await message.reply("সঠিক নাম্বার দিন। `/myreminders` দিয়ে তালিকা দেখুন।")
        return

    job_id = reminders[idx]["job_id"]
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass

    removed = reminders.pop(idx)
    await message.reply(f"বাতিল করা হয়েছে: \"{removed['text']}\"")


# ==== /health এন্ডপয়েন্ট (Render uptime monitoring এর জন্য, অপশনাল) ====
async def start_health_server():
    from aiohttp import web

    async def health(request):
        return web.Response(text="OK")

    web_app = web.Application()
    web_app.router.add_get("/health", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    scheduler.start()
    await app.start()
    print("রিমাইন্ডার বট চালু হয়েছে ✅")

    try:
        await start_health_server()
    except Exception as e:
        print(f"Health server চালু করা যায়নি (ঐচ্ছিক, সমস্যা নেই): {e}")

    await asyncio.Event().wait()  # বট চালু রাখার জন্য


if __name__ == "__main__":
    asyncio.run(main())
