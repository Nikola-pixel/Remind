import os
import json
from datetime import date, time
from dotenv import load_dotenv
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(i) for i in os.getenv("ADMIN_IDS", "").split(",") if i]

challenges_file = "challenges.json"
reminders_file = "reminders.json"
results_file = "results.json"
TRAINING = 1

# Заглушки (вставь свои функции сюда)
async def challenge(update, context): pass
async def choose_challenge(update, context): pass
async def mark(update, context): pass
async def mychallenge(update, context): pass
async def register_reminders(update, context): pass
async def morning_reminder(context): pass
async def evening_reminder(context): pass

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Нет доступа.")
        return
    if not os.path.exists(results_file):
        await update.message.reply_text("Нет данных.")
        return
    with open(results_file, "r") as f:
        data = json.load(f)
    import csv
    filename = "report.csv"
    with open(filename, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["UserID", "Date", "Theme", "Score"])
        for uid, entries in data.items():
            for e in entries:
                writer.writerow([uid, e["date"], e["theme"], e["score"]])
    await update.message.reply_document(InputFile(filename))
    os.remove(filename)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("mark", mark))
    app.add_handler(CommandHandler("mychallenge", mychallenge))
    app.add_handler(CommandHandler("remindme", register_reminders))
    challenge_conv = ConversationHandler(
        entry_points=[CommandHandler("challenge", challenge)],
        states={
            TRAINING: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_challenge)],
        },
        fallbacks=[]
    )
    app.add_handler(challenge_conv)
    app.job_queue.run_daily(morning_reminder, time=time(hour=8))
    app.job_queue.run_daily(evening_reminder, time=time(hour=20))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()