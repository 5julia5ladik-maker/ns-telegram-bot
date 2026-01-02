import os
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ===== ENV =====
TOKEN = os.getenv("8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U")
INVITE_LINK = os.getenv("5443870760")
CONTACT_EMAIL = os.getenv("naturalsense.pr@gmail.com")
CONTACT_TG = os.getenv("@NScollab")

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔒 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ]

    caption = (
        "✨ **NS • Natural Sense** ✨\n\n"
        "Распаковки • Бренды • Обзоры\n"
        "Сравнения • Новости\n\n"
        "🔒 Закрытый доступ"
    )

    await update.message.reply_photo(
        photo=InputFile("cover.jpg"),
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

# ===== BUTTONS =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        await query.edit_message_caption(
            caption=(
                "✨ **NS • Natural Sense** ✨\n\n"
                "Премиальный канал о косметике:\n"
                "• честные обзоры\n"
                "• сравнения брендов\n"
                "• новинки индустрии\n\n"
                "🔒 Доступ по приглашению"
            ),
            reply_markup=query.message.reply_markup,
            parse_mode="Markdown",
        )

    elif query.data == "collab":
        await query.edit_message_caption(
            caption=(
                "🤝 **Сотрудничество**\n\n"
                f"📧 Email: `{CONTACT_EMAIL}`\n"
                f"💬 Telegram: {CONTACT_TG}"
            ),
            reply_markup=query.message.reply_markup,
            parse_mode="Markdown",
        )

    elif query.data == "exit":
        await query.edit_message_caption(
            caption="❌ Вы вышли. Чтобы вернуться — напишите /start"
        )

# ===== MAIN =====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
