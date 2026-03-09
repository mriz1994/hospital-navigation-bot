# ====================================================
# HOSPITAL NAVIGATION TELEGRAM BOT
# ====================================================

import logging
import os
import tempfile
from collections import deque

from gtts import gTTS
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# ================= TOKEN =================
BOT_TOKEN = "8794345159:AAHEjBzpFW98v81XcvgrnBGEeoXiBWbYZd8"

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

# ====================================================
# DESTINATIONS
# ====================================================

DESTINATIONS = {
"RAD": "🩻 الأشعة",
"OUT": "🏥 العيادات الخارجية",
"ICU": "❤️ العناية المركزة",
"SUR": "🔪 الجراحة",
"PHA": "💊 الصيدلية",
"LAB": "🧪 المعمل"
}

DEST_TO_LOCATION = {
"RAD": "RADIOLOGY",
"OUT": "OUTPATIENT",
"ICU": "ICU",
"SUR": "SURGERY",
"PHA": "PHARMACY",
"LAB": "LAB"
}

# ====================================================
# HOSPITAL GRAPH
# ====================================================

HOSPITAL_GRAPH = {

"ENTRANCE":[
("ELEVATOR_GF","امشي على طول لحد المصاعد"),
("PHARMACY","اتجه يسار للصيدلية"),
("LAB","المعمل قدامك")
],

"ELEVATOR_GF":[
("ELEVATOR_F1","خد المصعد للدور الأول"),
("ELEVATOR_F2","خد المصعد للدور التاني"),
("ENTRANCE","ارجع للمدخل")
],

"ELEVATOR_F1":[
("RADIOLOGY","اتجه يسار لقسم الأشعة"),
("OUTPATIENT","اتجه يمين للعيادات"),
("ELEVATOR_GF","انزل الأرضي")
],

"ELEVATOR_F2":[
("ICU","اتجه يسار للعناية المركزة"),
("SURGERY","اتجه يمين للجراحة"),
("ELEVATOR_GF","انزل الأرضي")
]

}

# ====================================================
# FIND ROUTE (BFS)
# ====================================================

def find_route(start, goal):

    visited = set()
    queue = deque([(start, [])])

    while queue:

        location, path = queue.popleft()

        if location == goal:
            return path

        visited.add(location)

        for neighbor, instruction in HOSPITAL_GRAPH.get(location, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [instruction]))

    return None


# ====================================================
# VOICE FUNCTION
# ====================================================

async def send_voice(update: Update, text: str):

    try:

        tts = gTTS(text=text, lang="ar")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:

            tts.save(f.name)
            filename = f.name

        with open(filename, "rb") as audio:
            await update.effective_message.reply_voice(audio)

        os.remove(filename)

    except Exception as e:

        logging.warning(e)


# ====================================================
# BUTTONS
# ====================================================

def destination_keyboard():

    keyboard = []

    items = list(DESTINATIONS.items())

    for i in range(0, len(items), 2):

        row = [
            InlineKeyboardButton(name, callback_data=code)
            for code, name in items[i:i+2]
        ]

        keyboard.append(row)

    return InlineKeyboardMarkup(keyboard)


def next_keyboard():

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("الخطوة الجاية ➡️", callback_data="NEXT")]]
    )


# ====================================================
# START
# ====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["location"] = "ENTRANCE"

    await update.message.reply_text(

        "أهلاً بيك في نظام إرشاد المستشفى 😊\n\n"
        "اختار المكان اللي عايز تروحه:",

        reply_markup=destination_keyboard()

    )


# ====================================================
# BEGIN ROUTE
# ====================================================

async def begin_route(update, context, destination):

    start = context.user_data.get("location", "ENTRANCE")

    goal = DEST_TO_LOCATION[destination]

    route = find_route(start, goal)

    if not route:

        await update.effective_message.reply_text("مش لاقي طريق دلوقتي")
        return

    context.user_data["route"] = route
    context.user_data["step"] = 0

    text = route[0]

    await update.effective_message.reply_text(
        f"الخطوة (1/{len(route)})\n{text}"
    )

    await send_voice(update, text)

    await update.effective_message.reply_text(
        "لما توصل اضغط التالي",
        reply_markup=next_keyboard()
    )


# ====================================================
# DEST BUTTON
# ====================================================

async def destination_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    await begin_route(update, context, query.data)


# ====================================================
# NEXT STEP
# ====================================================

async def next_step(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    step = context.user_data.get("step", 0) + 1
    route = context.user_data.get("route", [])

    context.user_data["step"] = step

    if step < len(route):

        text = route[step]

        await query.message.reply_text(
            f"الخطوة ({step+1}/{len(route)})\n{text}"
        )

        await send_voice(update, text)

        await query.message.reply_text(
            "التالي",
            reply_markup=next_keyboard()
        )

    else:

        await query.message.reply_text("🎉 وصلت للمكان!")

        await query.message.reply_text(
            "اختار مكان تاني:",
            reply_markup=destination_keyboard()
        )


# ====================================================
# MAIN
# ====================================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(destination_callback, pattern="^(RAD|OUT|ICU|SUR|PHA|LAB)$"))

    app.add_handler(CallbackQueryHandler(next_step, pattern="NEXT"))

    print("BOT RUNNING")

    app.run_polling()


if __name__ == "__main__":
    main()