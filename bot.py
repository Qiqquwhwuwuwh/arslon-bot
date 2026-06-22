import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from groq import Groq

# === SOZLAMALAR ===
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8852971651:AAH_MuVcsKxsCZ7bW-CD2-PKFyTJZPu0IqA")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_client = Groq(api_key=GROQ_API_KEY)

# === ANIQ JAVOBLAR (AI ga bormaydi) ===
FIXED_REPLIES = {
    # Salomlashish
    "assalomu alaykum": "Vaalaykum assalom! 😊",
    "salom": "Vaalaykum assalom! 😊",
    "vaalaykum assalom": "Assalomu alaykum! 😊",
    "hey": "Salom! 😊 Qanday yordam bera olaman?",

    # Ahvol
    "yaxshimisiz": "Yaxshi, rahmat! Siz-chi? 😊",
    "qalaysiz": "Yaxshi, rahmat! Siz-chi? 😊",
    "tinchlikmisiz": "Tinchlik, rahmat! 😊",

    # Kurs to'lovi
    "kurs to'lovi qancha": "📚 Kurs to'lovi: *500 000 so'm* (oyiga)\n\nTo'liq ma'lumot uchun yozing!",
    "kurs narxi qancha": "📚 Kurs to'lovi: *500 000 so'm* (oyiga)",
    "narxi qancha": "📚 Kurs to'lovi: *500 000 so'm* (oyiga)",
    "qancha turadi": "📚 Kurs to'lovi: *500 000 so'm* (oyiga)",
    "to'lov qancha": "📚 Kurs to'lovi: *500 000 so'm* (oyiga)",

    # Karta raqam
    "karta raqam tashlang": "💳 To'lov kartasi:\n\n`9860 1201 3266 9876`\n👤 Arslonbek Turdibekov\n\nTo'lov qilgach, chek rasmini yuboring! 📸",
    "karta raqam": "💳 To'lov kartasi:\n\n`9860 1201 3266 9876`\n👤 Arslonbek Turdibekov",
    "karta raqamingiz": "💳 To'lov kartasi:\n\n`9860 1201 3266 9876`\n👤 Arslonbek Turdibekov",
    "to'lov qilaman": "💳 To'lov kartasi:\n\n`9860 1201 3266 9876`\n👤 Arslonbek Turdibekov\n\nTo'lov qilgach, chek rasmini yuboring! 📸",
    "to'lovni qanday qilaman": "💳 To'lov kartasi:\n\n`9860 1201 3266 9876`\n👤 Arslonbek Turdibekov\n\nPul o'tkazgach, chek rasmini yuboring! 📸",

    # Kurs haqida
    "kurs haqida": "🇩🇪 *Nemis tili kursi*\n\n📌 Daraja: A1-A2\n⏰ Dars vaqti: kelishiladi\n💰 Narxi: 500 000 so'm/oy\n\nQo'shimcha savollar uchun yozing!",
    "kurs haqida ma'lumot": "🇩🇪 *Nemis tili kursi*\n\n📌 Daraja: A1-A2\n⏰ Dars vaqti: kelishiladi\n💰 Narxi: 500 000 so'm/oy\n\nQo'shimcha savollar uchun yozing!",
    "dars vaqtlari": "⏰ Dars jadvali individual kelishiladi.\nQulaylikni birgalikda tanlaymiz! 😊",
    "darslar qachon": "⏰ Dars jadvali individual kelishiladi.\nQulaylikni birgalikda tanlaymiz! 😊",

    # Ro'yxatdan o'tish
    "ro'yxatdan o'tmoqchiman": "✅ Zo'r! Ismingiz va qulay dars vaqtingizni yozing, tez orada bog'lanamiz! 😊",
    "kursga yozilmoqchiman": "✅ Zo'r! Ismingiz va qulay dars vaqtingizni yozing, tez orada bog'lanamiz! 😊",
    "qanday yozilaman": "✅ Ismingiz va telefon raqamingizni yuboring, bog'lanamiz! 😊",

    # Xayr
    "xayr": "Xayr! Savollar bo'lsa yozing! 😊🇩🇪",
    "ko'rishguncha": "Ko'rishguncha! 😊",
    "rahmat": "Arzimaydi! Boshqa savollar bo'lsa yozing 😊",
}

# === KALIT SO'Z TEKSHIRISH ===
def get_fixed_reply(text: str):
    text_lower = text.lower().strip()

    # To'liq moslik
    if text_lower in FIXED_REPLIES:
        return FIXED_REPLIES[text_lower]

    # Qisman moslik
    for key, value in FIXED_REPLIES.items():
        if key in text_lower:
            return value

    return None

# === AI JAVOB (Groq) ===
def get_ai_reply(user_message: str) -> str:
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """Sen Arslonbek Turdibekovning nemis tili kursi uchun yordamchi botsan.
                    
Qoidalar:
- Faqat o'zbek tilida javob ber
- Qisqa va aniq javob ber
- Doim do'stona va professional bo'l
- Nemis tili grammatikasi haqida savollar bo'lsa — tushuntir
- Kurs to'lovi: 500 000 so'm
- Karta: 9860 1201 3266 9876 (Arslonbek Turdibekov)
- Boshqa mavzularda: "Bu haqida o'qituvchimizga murojaat qiling" de"""
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq xatosi: {e}")
        return "Kechirasiz, hozir texnik muammo. Biroz kutib qayta yozing! 🙏"

# === XABAR QAYTA ISHLASH ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_text = update.message.text
    user_name = update.message.from_user.first_name or "Foydalanuvchi"

    logger.info(f"{user_name}: {user_text}")

    # Avval aniq javoblar tekshiriladi
    fixed = get_fixed_reply(user_text)

    if fixed:
        await update.message.reply_text(fixed, parse_mode="Markdown")
    else:
        # AI ga yuboriladi
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        ai_reply = get_ai_reply(user_text)
        await update.message.reply_text(ai_reply)

# === START KOMANDASI ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 👋🇩🇪\n\n"
        "Men *Nemis tili kursi* yordamchi botiman.\n\n"
        "Savol bering — javob beraman! 😊",
        parse_mode="Markdown"
    )

# === BOT ISHGA TUSHIRISH ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    from telegram.ext import CommandHandler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot ishga tushdi! ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
