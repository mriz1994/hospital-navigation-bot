from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8794345159:AAFXnNclJ43wRpJSJ8dSqAc6l1X2TSmEOGA"
locations = {
    "mri": "Main Gate → Main Building → Major Surgery Corridor → MRI Room",
    "icu": "Main Gate → Main Building → Major Surgery Corridor → ICU",
    "emergency": "Main Gate → Emergency Corridor → Emergency Department"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Hospital Navigation Bot ready.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    for place in locations:
        if place in text:
            await update.message.reply_text(locations[place])
            return

    await update.message.reply_text("Sorry, I don't know that location yet.")

    if "mri" in text:
        reply = "Main Gate → Main Building → Major Surgery Corridor → MRI Room"
    else:
        reply = "Department not found."

    await update.message.reply_text(reply)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
