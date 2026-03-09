# ================================================================
#  HOSPITAL GUIDE BOT — Egyptian Arabic Navigation System
#  Compatible with python-telegram-bot 22.x and Python 3.14
# ================================================================

import logging
import os
import tempfile

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

# ── Token — paste your token directly here ────────────────────────────────────
BOT_TOKEN = "8794345159:AAHFNee0Vz4sB7Sm8NqMM_l2E5_yicE_2EA"
BOT_USERNAME = "SCUMapBot"

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

# ================================================================
#  LOCATIONS DATABASE
# ================================================================
LOCATIONS = {
    "LOC_GF_ENTRANCE_MAIN":  {"name": "المدخل الرئيسي",               "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند المدخل الرئيسي للمستشفى"},
    "LOC_GF_RECEPTION_A":    {"name": "الاستعلامات — مدخل A",         "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند الاستعلامات مدخل A"},
    "LOC_GF_RECEPTION_B":    {"name": "الاستعلامات — مدخل B",         "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند الاستعلامات مدخل B"},
    "LOC_GF_EMERGENCY_DOOR": {"name": "مدخل الطوارئ",                 "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند باب قسم الطوارئ"},
    "LOC_GF_PHARMACY":       {"name": "الصيدلية",                     "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند الصيدلية"},
    "LOC_GF_LAB":            {"name": "التحاليل / المعمل",            "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند قسم التحاليل"},
    "LOC_GF_ELEVATOR":       {"name": "المصاعد — الدور الأرضي",       "floor": "الدور الأرضي",  "description": "أنت دلوقتي أمام المصاعد في الدور الأرضي"},
    "LOC_GF_STAIRS":         {"name": "السلم — الدور الأرضي",         "floor": "الدور الأرضي",  "description": "أنت دلوقتي عند السلم في الدور الأرضي"},
    "LOC_F1_ELEVATOR":       {"name": "المصاعد — الدور الأول",        "floor": "الدور الأول",   "description": "أنت دلوقتي عند المصاعد في الدور الأول"},
    "LOC_F1_CORRIDOR_MAIN":  {"name": "الممر الرئيسي — الدور الأول",  "floor": "الدور الأول",   "description": "أنت دلوقتي في الممر الرئيسي بالدور الأول"},
    "LOC_F1_RADIOLOGY":      {"name": "قسم الأشعة",                   "floor": "الدور الأول",   "description": "أنت دلوقتي عند قسم الأشعة"},
    "LOC_F1_OUTPATIENT":     {"name": "العيادات الخارجية",            "floor": "الدور الأول",   "description": "أنت دلوقتي عند العيادات الخارجية"},
    "LOC_F1_INTERNAL_MED":   {"name": "قسم الباطنة",                  "floor": "الدور الأول",   "description": "أنت دلوقتي عند قسم الباطنة"},
    "LOC_F2_ELEVATOR":       {"name": "المصاعد — الدور التاني",       "floor": "الدور التاني",  "description": "أنت دلوقتي عند المصاعد في الدور التاني"},
    "LOC_F2_CORRIDOR_MAIN":  {"name": "الممر الرئيسي — الدور التاني", "floor": "الدور التاني",  "description": "أنت دلوقتي في الممر الرئيسي بالدور التاني"},
    "LOC_F2_ICU":            {"name": "العناية المركزة",              "floor": "الدور التاني",  "description": "أنت دلوقتي عند قسم العناية المركزة"},
    "LOC_F2_SURGERY":        {"name": "قسم الجراحة",                  "floor": "الدور التاني",  "description": "أنت دلوقتي عند قسم الجراحة"},
    "LOC_F2_RECEPTION":      {"name": "الاستعلامات — الدور التاني",   "floor": "الدور التاني",  "description": "أنت دلوقتي عند الاستعلامات في الدور التاني"},
    "LOC_F3_ELEVATOR":       {"name": "المصاعد — الدور التالت",       "floor": "الدور التالت",  "description": "أنت دلوقتي عند المصاعد في الدور التالت"},
    "LOC_F3_CORRIDOR_MAIN":  {"name": "الممر الرئيسي — الدور التالت", "floor": "الدور التالت",  "description": "أنت دلوقتي في الممر الرئيسي بالدور التالت"},
}

# ================================================================
#  DESTINATIONS
# ================================================================
DESTINATIONS = {
    "DEST_EMERGENCY":    "🚨 الطوارئ",
    "DEST_PHARMACY":     "💊 الصيدلية",
    "DEST_LAB":          "🧪 التحاليل",
    "DEST_RADIOLOGY":    "🩻 الأشعة",
    "DEST_OUTPATIENT":   "🏥 العيادات الخارجية",
    "DEST_ICU":          "❤️ العناية المركزة",
    "DEST_SURGERY":      "🔪 الجراحة",
    "DEST_INTERNAL_MED": "🩺 الباطنة",
    "DEST_RECEPTION":    "ℹ️ الاستعلامات",
    "DEST_BATHROOM":     "🚻 الحمام",
    "DEST_CAFETERIA":    "☕ الكافيتيريا",
    "DEST_PARKING":      "🚗 موقف السيارات",
}

# ================================================================
#  ROUTES
# ================================================================
ROUTES = {
    "LOC_GF_ENTRANCE_MAIN": {
        "DEST_EMERGENCY":    ["من المدخل الرئيسي، اتجه يمين فورًا", "هتشوف لافتة حمرا كبيرة مكتوب عليها طوارئ", "امشي ناحيتها — وصلت! 🚨"],
        "DEST_PHARMACY":     ["من المدخل الرئيسي، اتجه يسار", "امشي على طول الممر لحد آخره", "الصيدلية على إيدك اليمين — وصلت! 💊"],
        "DEST_LAB":          ["من المدخل الرئيسي، امشي على طول", "عند نهاية الممر، اتجه يسار", "التحاليل أول باب على يمينك — وصلت! 🧪"],
        "DEST_RADIOLOGY":    ["من المدخل الرئيسي، امشي على طول لحد المصاعد", "خد المصعد للدور الأول", "اتجه يسار من المصعد وامشي على طول", "قسم الأشعة على يمينك — وصلت! 🩻"],
        "DEST_OUTPATIENT":   ["من المدخل الرئيسي، امشي على طول", "خد المصعد للدور الأول", "اتجه يمين من المصعد", "العيادات في آخر الممر — وصلت! 🏥"],
        "DEST_ICU":          ["من المدخل الرئيسي، امشي على طول لحد المصاعد", "خد المصعد للدور التاني", "اتجه يسار من المصعد", "العناية المركزة في آخر الممر — وصلت! ❤️"],
        "DEST_SURGERY":      ["من المدخل الرئيسي، امشي على طول لحد المصاعد", "خد المصعد للدور التاني", "اتجه يمين من المصعد", "الجراحة في آخر الممر على اليسار — وصلت! 🔪"],
        "DEST_INTERNAL_MED": ["من المدخل الرئيسي، خد المصعد للدور الأول", "اتجه يمين من المصعد", "الباطنة تاني باب على اليسار — وصلت! 🩺"],
        "DEST_RECEPTION":    ["من المدخل الرئيسي، الاستعلامات أمامك مباشرةً", "امشي ١٠ خطوات للأمام — وصلت! ℹ️"],
        "DEST_BATHROOM":     ["من المدخل الرئيسي، اتجه يسار", "امشي ٢٠ خطوة — الحمام على يمينك — وصلت! 🚻"],
        "DEST_CAFETERIA":    ["من المدخل الرئيسي، اتجه يسار", "في آخر الممر، اتجه يسار تاني", "الكافيتيريا على يمينك — وصلت! ☕"],
        "DEST_PARKING":      ["ارجع للخلف من المدخل الرئيسي", "موقف السيارات على إيدك اليمين مباشرةً — وصلت! 🚗"],
    },
    "LOC_GF_ELEVATOR": {
        "DEST_RADIOLOGY":    ["أنت عند المصاعد — تمام!", "خد المصعد للدور الأول", "اتجه يسار من المصعد وامشي على طول", "قسم الأشعة على يمينك — وصلت! 🩻"],
        "DEST_ICU":          ["خد المصعد للدور التاني", "اتجه يسار من المصعد", "العناية المركزة في آخر الممر — وصلت! ❤️"],
        "DEST_SURGERY":      ["خد المصعد للدور التاني", "اتجه يمين من المصعد", "الجراحة في آخر الممر على اليسار — وصلت! 🔪"],
        "DEST_OUTPATIENT":   ["خد المصعد للدور الأول", "اتجه يمين من المصعد", "العيادات في آخر الممر — وصلت! 🏥"],
        "DEST_EMERGENCY":    ["مش محتاج مصعد — الطوارئ في الدور الأرضي", "ارجع للممر الرئيسي واتجه يمين", "اتبع اللافتة الحمرا — وصلت! 🚨"],
        "DEST_PHARMACY":     ["مش محتاج مصعد — الصيدلية في الدور الأرضي", "ارجع للممر الرئيسي واتجه يسار", "الصيدلية في آخر الممر — وصلت! 💊"],
    },
    "LOC_F1_ELEVATOR": {
        "DEST_RADIOLOGY":    ["أنت في الدور الأول عند المصاعد", "اتجه يسار وامشي على طول الممر", "قسم الأشعة على يمينك — وصلت! 🩻"],
        "DEST_OUTPATIENT":   ["اتجه يمين من المصاعد", "العيادات في آخر الممر — وصلت! 🏥"],
        "DEST_INTERNAL_MED": ["اتجه يمين من المصاعد", "الباطنة تاني باب على اليسار — وصلت! 🩺"],
        "DEST_ICU":          ["خد المصعد للدور التاني", "اتجه يسار من المصعد", "العناية المركزة في آخر الممر — وصلت! ❤️"],
        "DEST_EMERGENCY":    ["خد المصعد للدور الأرضي", "من المصعد، اتجه يمين", "الطوارئ واضحة باللافتة الحمرا — وصلت! 🚨"],
        "DEST_PHARMACY":     ["خد المصعد للدور الأرضي", "من المصعد، اتجه يسار وامشي للآخر", "الصيدلية على يمينك — وصلت! 💊"],
    },
    "LOC_F2_ELEVATOR": {
        "DEST_ICU":          ["أنت في الدور التاني عند المصاعد", "اتجه يسار وامشي على طول الممر", "العناية المركزة في آخره — وصلت! ❤️"],
        "DEST_SURGERY":      ["اتجه يمين من المصاعد", "الجراحة في آخر الممر على اليسار — وصلت! 🔪"],
        "DEST_EMERGENCY":    ["خد المصعد للدور الأرضي", "اتجه يمين من المصعد", "الطوارئ على اليمين — وصلت! 🚨"],
        "DEST_RADIOLOGY":    ["خد المصعد للدور الأول", "اتجه يسار من المصعد وامشي على طول", "قسم الأشعة على يمينك — وصلت! 🩻"],
    },
    "LOC_GF_RECEPTION_A": {
        "DEST_EMERGENCY":    ["من الاستعلامات A، اتجه يمين", "امشي لحد اللافتة الحمرا — وصلت للطوارئ! 🚨"],
        "DEST_PHARMACY":     ["من الاستعلامات A، اتجه يسار", "امشي للآخر — الصيدلية على يمينك! 💊"],
        "DEST_LAB":          ["من الاستعلامات A، امشي على طول", "التحاليل أول باب على اليسار — وصلت! 🧪"],
    },
    "LOC_GF_RECEPTION_B": {
        "DEST_RADIOLOGY":    ["من الاستعلامات B، امشي للمصاعد في آخر الممر", "خد المصعد للدور الأول", "اتجه يسار — الأشعة على يمينك — وصلت! 🩻"],
        "DEST_EMERGENCY":    ["من الاستعلامات B، ارجع للممر الرئيسي واتجه يمين", "اتبع اللافتة الحمرا — وصلت! 🚨"],
    },
}

# ================================================================
#  KEYWORD DETECTION
# ================================================================
KEYWORD_MAP = {
    "DEST_EMERGENCY":    ["طوارئ", "اسعاف", "إسعاف", "طارئ"],
    "DEST_PHARMACY":     ["صيدلية", "دوا", "دواء", "دوايا"],
    "DEST_LAB":          ["تحاليل", "معمل", "مختبر", "دم", "عينة"],
    "DEST_RADIOLOGY":    ["أشعة", "اشعة", "راديولوجي", "سونار"],
    "DEST_OUTPATIENT":   ["عيادة", "عيادات", "خارجية", "كشف", "دكتور"],
    "DEST_ICU":          ["عناية", "مركزة", "انعاش"],
    "DEST_SURGERY":      ["جراحة", "عملية"],
    "DEST_INTERNAL_MED": ["باطنة", "باطنية"],
    "DEST_RECEPTION":    ["استعلامات", "إدارة", "ادارة", "معلومات"],
    "DEST_BATHROOM":     ["حمام", "تواليت", "مياه"],
    "DEST_CAFETERIA":    ["كافيتيريا", "اكل", "أكل", "قهوة"],
    "DEST_PARKING":      ["موقف", "سيارة", "عربية"],
}

# ================================================================
#  HELPERS
# ================================================================

async def send_voice(update: Update, text: str):
    try:
        tts = gTTS(text=text, lang="ar")
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            tts.save(f.name)
            fname = f.name
        with open(fname, "rb") as audio:
            await update.effective_message.reply_voice(voice=audio)
        os.unlink(fname)
    except Exception as e:
        logging.warning(f"Voice error: {e}")


def build_destination_keyboard():
    keyboard = []
    items = list(DESTINATIONS.items())
    for i in range(0, len(items), 2):
        row = [InlineKeyboardButton(name, callback_data=dest_id)
               for dest_id, name in items[i:i+2]]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def build_next_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("الخطوة الجاية ➡️", callback_data="NEXT_STEP"),
        InlineKeyboardButton("🔄 وجهة جديدة",    callback_data="NEW_DEST"),
    ]])


def detect_dest(text: str):
    text = text.lower()
    for dest_id, keywords in KEYWORD_MAP.items():
        if any(kw in text for kw in keywords):
            return dest_id
    return None


async def begin_route(update: Update, context: ContextTypes.DEFAULT_TYPE, dest_id: str):
    current_loc = context.user_data.get("current_location", "LOC_GF_ENTRANCE_MAIN")
    dest_name   = DESTINATIONS.get(dest_id, "وجهتك")
    route       = ROUTES.get(current_loc, {}).get(dest_id)

    if route:
        context.user_data.update({"destination": dest_id, "route": route, "step": 0})
        step_text = route[0]
        msg = f"تمام! هوديك على {dest_name} 🗺️\n\nالخطوة (1/{len(route)}):\n➡️ {step_text}"
        await update.effective_message.reply_text(msg)
        await send_voice(update, step_text)
        if len(route) > 1:
            await update.effective_message.reply_text(
                "لما تعمل اللي قلتك، اضغط الخطوة الجاية ⬇️\nأو امسح أي كود QR في طريقك:",
                reply_markup=build_next_keyboard()
            )
        else:
            await update.effective_message.reply_text(f"🎉 وصلت لـ {dest_name}! بالسلامة 😊")
    else:
        await update.effective_message.reply_text(
            f"🔍 عايز توصل لـ {dest_name}.\n"
            "امسح أقرب كود QR عشان أعرف موقعك بالظبط، أو اسأل الاستعلامات.\n\n"
            "اختار وجهة تانية:",
            reply_markup=build_destination_keyboard()
        )

# ================================================================
#  HANDLERS
# ================================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args        = context.args or []
    location_id = args[0] if args else None

    if location_id and location_id in LOCATIONS:
        prev_loc = context.user_data.get("current_location")
        context.user_data["current_location"] = location_id
        loc = LOCATIONS[location_id]

        if prev_loc and prev_loc != location_id and context.user_data.get("destination"):
            dest_id   = context.user_data["destination"]
            dest_name = DESTINATIONS.get(dest_id, "وجهتك")
            await update.effective_message.reply_text(
                f"✅ موقعك اتحدث!\n📍 أنت دلوقتي: {loc['name']}\n"
                f"🎯 بتتجه لـ: {dest_name}\n\nبحسب موقعك الجديد:"
            )
            await begin_route(update, context, dest_id)
        else:
            greeting = (
                f"أهلاً وسهلاً! 😊\n"
                f"📍 {loc['name']} — {loc['floor']}\n"
                f"{loc['description']}\n\nعايز تروح فين؟"
            )
            await update.effective_message.reply_text(greeting)
            await send_voice(update, loc["description"] + " — عايز تروح فين؟")
            await update.effective_message.reply_text("اختار وجهتك:", reply_markup=build_destination_keyboard())
    else:
        context.user_data["current_location"] = "LOC_GF_ENTRANCE_MAIN"
        welcome = (
            "أهلاً وسهلاً في مستشفانا! 😊\n\n"
            "أنا دليلك الذكي — هساعدك توصل لأي قسم بسهولة.\n\n"
            "📱 امسح كود QR الأقرب ليك عشان أعرف موقعك بالظبط\n"
            "أو اختار وجهتك من القائمة:"
        )
        await update.effective_message.reply_text(welcome)
        await send_voice(update, "أهلاً وسهلاً! اختار وجهتك وأنا هوديك.")
        await update.effective_message.reply_text("عايز تروح فين؟", reply_markup=build_destination_keyboard())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "إزاي تستخدم البوت:\n\n"
        "1 — امسح كود QR الأقرب ليك\n"
        "2 — اختار وجهتك من القائمة\n"
        "3 — اتبع الخطوات واحدة واحدة\n"
        "4 — امسح أي كود QR في طريقك لتحديث الطريق\n\n"
        "أو اكتب اسم القسم بالعربي وأنا هفهمك",
        reply_markup=build_destination_keyboard()
    )


async def cb_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await begin_route(update, context, query.data)


async def cb_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    route = context.user_data.get("route", [])
    step  = context.user_data.get("step", 0) + 1
    context.user_data["step"] = step

    if step < len(route):
        step_text = route[step]
        progress  = f"({step + 1}/{len(route)})"
        await query.message.reply_text(f"الخطوة {progress}:\n➡️ {step_text}")
        await send_voice(update, step_text)
        if step < len(route) - 1:
            await query.message.reply_text("جاهز؟", reply_markup=build_next_keyboard())
        else:
            dest_name = DESTINATIONS.get(context.user_data.get("destination", ""), "وجهتك")
            await query.message.reply_text(f"🎉 وصلت لـ {dest_name}! بالسلامة وسلامتك 😊")
            await send_voice(update, f"مبروك، وصلت لـ {dest_name}!")
            await query.message.reply_text("لو محتاج حاجة تانية:", reply_markup=build_destination_keyboard())
    else:
        dest_name = DESTINATIONS.get(context.user_data.get("destination", ""), "وجهتك")
        await query.message.reply_text(f"🎉 وصلت لـ {dest_name}! بالسلامة 😊")


async def cb_new_dest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("اختار وجهتك الجديدة:", reply_markup=build_destination_keyboard())


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dest_id = detect_dest(update.message.text)
    if dest_id:
        await begin_route(update, context, dest_id)
    else:
        await update.message.reply_text(
            "مش فاهم قصدك — اختار من القائمة:",
            reply_markup=build_destination_keyboard()
        )


async def handle_voice_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سمعتك! اختار وجهتك من القائمة:",
        reply_markup=build_destination_keyboard()
    )

# ================================================================
#  MAIN
# ================================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CallbackQueryHandler(cb_dest,     pattern=r"^DEST_"))
    app.add_handler(CallbackQueryHandler(cb_next,     pattern=r"^NEXT_STEP$"))
    app.add_handler(CallbackQueryHandler(cb_new_dest, pattern=r"^NEW_DEST$"))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_msg))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("البوت شغال — اضغط Ctrl+C لوقفه")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
