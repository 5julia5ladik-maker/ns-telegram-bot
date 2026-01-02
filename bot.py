import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# 🔴 ДАННЫЕ (ПРЯМО В КОДЕ)
# =========================

TOKEN = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"

INVITE_LINK = "https://t.me/+5443870760"
CONTACT_EMAIL = "naturalsense.pr@gmail.com"
CONTACT_TG = "@NScollab"

# =========================
# ЛОГИ
# =========================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✨ *NS · Natural Sense*\n\n"
        "Распаковки · Бренды · Обзоры\n"
        "Сравнения · Новости\n\n"
        "🔒 *Закрытый доступ*"
    )

    keyboard = [
        [InlineKeyboardButton("🔐 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ]

    await update.message.reply_text(
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# =========================
# КНОПКИ
# =========================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.message.reply_text(
            "ℹ️ *О канале*\n\n"
            "Natural Sense — обзоры косметики, брендов и новинок.",
            parse_mode="Markdown",
        )

    elif query.data == "collab":
        await query.message.reply_text(
            f"🤝 *Сотрудничество*\n\n"
            f"📧 Email: {CONTACT_EMAIL}\n"
            f"💬 Telegram: {CONTACT_TG}",
            parse_mode="Markdown",
        )

    elif query.data == "exit":
        await query.message.reply_text("❌ Вы вышли из меню.")

# =========================
# MAIN
# =========================

def main():
    print("✅ BOT STARTING")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    print("✅ BOT RUNNING")
    app.run_polling()

if __name__ == "__main__":
    main()
