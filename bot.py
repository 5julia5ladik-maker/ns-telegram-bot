import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# =========================
# ДАННЫЕ
# =========================

TOKEN = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"

INVITE_LINK = "https://t.me/+5443870760"
CONTACT_EMAIL = "naturalsense.pr@gmail.com"
CONTACT_TG = "@NScollab"

# =========================
# ЛОГИ
# =========================

logging.basicConfig(level=logging.INFO)

# =========================
# ТЕКСТЫ
# =========================

MAIN_TEXT = (
    "✨ *NS · Natural Sense*\n\n"
    "Распаковки · Бренды · Обзоры\n"
    "Сравнения · Новости\n\n"
    "🔒 *Закрытый доступ*"
)

ABOUT_TEXT = (
    "ℹ️ *О канале*\n\n"
    "Natural Sense — обзоры косметики,\n"
    "брендов и новинок."
)

COLLAB_TEXT = (
    "🤝 *Сотрудничество*\n\n"
    f"📧 Email: `{CONTACT_EMAIL}`\n"
    f"💬 Telegram: {CONTACT_TG}"
)

# =========================
# КЛАВИАТУРА
# =========================

def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ])

# =========================
# /start
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MAIN_TEXT,
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )

# =========================
# ОБРАБОТКА КНОПОК (КЛЮЧ!)
# =========================

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_text(
            ABOUT_TEXT,
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )

    elif query.data == "collab":
        await query.edit_message_text(
            COLLAB_TEXT,
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )

    elif query.data == "exit":
        await query.edit_message_text(
            "❌ Вы вышли из меню.",
        )

# =========================
# MAIN
# =========================

def main():
    print("✅ BOT STARTED")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
