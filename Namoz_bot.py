# -*- coding: utf-8 -*-
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

BOT_TOKEN = "8641272823:AAFpTcL-I3zm8Q5Xc6-Dq9AWLp6TGaQPrrU"
UZ_EDITION = "uz.sodik"

SURALAR = {
    "Yasin": 36,
    "Baqara": 2,
    "Fotiha": 1,
    "Ixlos": 112,
    "Falaq": 113,
    "Nos": 114,
    "Mulk": 67,
    "Rahmon": 55,
    "Kahf": 18,
}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

WAITING_CITY = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    matn = (
        "Assalomu alaykum! 🌙\n\n"
        "Men sizga yordam bera olaman:\n"
        "🕌 /namoz — shahringiz bo'yicha namoz vaqtlari\n"
        "📖 /sura — Qur'ondan sura tanlash (Yasin, Baqara va h.k.)\n"
    )
    await update.message.reply_text(matn)


async def namoz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Qaysi shahar uchun namoz vaqtlarini bilmoqchisiz?\n"
        "Masalan: Toshkent, Samarqand, Andijon..."
    )
    return WAITING_CITY


async def namoz_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shahar = update.message.text.strip()
    await update.message.reply_text(f"⏳ {shahar} uchun namoz vaqtlari izlanmoqda...")

    try:
        resp = requests.get(
            "http://api.aladhan.com/v1/timingsByCity",
            params={"city": shahar, "country": "Uzbekistan", "method": 2},
            timeout=10,
        )
        data = resp.json()

        if data.get("code") != 200:
            await update.message.reply_text(
                "❌ Bu shahar topilmadi. Iltimos, shahar nomini to'g'ri yozing "
                "(masalan: Tashkent) yoki boshqa nom bilan urinib ko'ring."
            )
            return ConversationHandler.END

        vaqtlar = data["data"]["timings"]
        sana = data["data"]["date"]["readable"]

        javob = (
            f"📅 {sana} — {shahar}\n\n"
            f"🌅 Bomdod (Fajr): {vaqtlar['Fajr']}\n"
            f"☀️ Quyosh chiqishi: {vaqtlar['Sunrise']}\n"
            f"🕛 Peshin (Dhuhr): {vaqtlar['Dhuhr']}\n"
            f"🕒 Asr: {vaqtlar['Asr']}\n"
            f"🌇 Shom (Maghrib): {vaqtlar['Maghrib']}\n"
            f"🌙 Xufton (Isha): {vaqtlar['Isha']}\n"
        )
        await update.message.reply_text(javob)

    except Exception as e:
        logger.error(f"Namoz vaqtlarini olishda xatolik: {e}")
        await update.message.reply_text("❌ Xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.")

    return ConversationHandler.END


async def namoz_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.")
    return ConversationHandler.END


async def sura_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tugmalar = [
        [InlineKeyboardButton(nom, callback_data=f"sura_{raqam}")]
        for nom, raqam in SURALAR.items()
    ]
    await update.message.reply_text(
        "Qaysi surani o'qimoqchisiz?",
        reply_markup=InlineKeyboardMarkup(tugmalar),
    )


async def sura_tanlandi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    raqam = int(query.data.split("_")[1])
    await query.edit_message_text("⏳ Sura matni yuklanmoqda...")

    try:
        resp = requests.get(
            f"http://api.alquran.cloud/v1/surah/{raqam}/{UZ_EDITION}",
            timeout=10,
        )
        data = resp.json()

        if data.get("code") != 200:
            await query.edit_message_text("❌ Sura matnini olishda xatolik. Keyinroq urinib ko'ring.")
            return

        sura = data["data"]
        nomi = sura["englishName"]
        oyatlar = sura["ayahs"]

        matn = f"📖 {nomi} surasi ({sura['numberOfAyahs']} oyat)\n\n"
        for oyat in oyatlar:
            qator = f"{oyat['numberInSurah']}. {oyat['text']}\n\n"
            if len(matn) + len(qator) > 3800:
                await contex
