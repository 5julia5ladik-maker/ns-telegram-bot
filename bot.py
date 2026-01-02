import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"

INVITE_LINK = "https://t.me/NaturalSense"
CONTACT_EMAIL = "naturalsense.pr@gmail.com"
CONTACT_TG = "@NScollab"

COVER_PATH = "cover.jpg"

# =========================
# ТЕКСТЫ
# =========================
TITLE = "✨ NS · Natural Sense"
SUBTITLE = "Распаковки · Бренды · Обзоры\nСравнения · Новости"
STATUS = "🔒 Закрытый доступ"
MAIN_CAPTION = f"{TITLE}\n\n{SUBTITLE}\n\n{STATUS}"

ABOUT_TEXT = (
    "ℹ️ *О канале*\n\n"
    "Natural Sense — обзоры косметики, брендов и новинок."
)

COLLAB_TEXT = (
    "🤝 *Сотрудничество*\n\n"
    "Выберите удобный способ связи:"
)

# =========================
# КНОПКИ
# =========================
def main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Назад", callback_data="back")]
    ])

def collab_keyboard():
    # ВАЖНО: Telegram часто не принимает mailto: в inline кнопках -> Button_url_invalid
    # Поэтому делаем email через web compose (Gmail). Работает стабильно.
    tg_username = CONTACT_TG.replace("@", "").strip()
    email_url = f"https://mail.google.com/mail/?view=cm&to={CONTACT_EMAIL}"
    tg_url = f"https://t.me/{tg_username}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=email_url)],
        [InlineKeyboardButton("💬 Написать в Telegram", url=tg_url)],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# /start -> одно сообщение с фото
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(COVER_PATH):
        await update.message.reply_text(
            "❗ Не найден файл cover.jpg рядом с bot.py. Положи cover.jpg в папку с bot.py и перезапусти."
        )
        return

    with open(COVER_PATH, "rb") as f:
        await update.message.reply_photo(
            photo=InputFile(f),
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )

# =========================
# CALLBACK КНОПКИ (редактируем ТО ЖЕ сообщение)
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    msg = query.message
    if not msg:
        return

    if query.data == "back":
        await msg.edit_caption(
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )
        return

    if query.data == "about":
        await msg.edit_caption(
            caption=ABOUT_TEXT,
            parse_mode="Markdown",
            reply_markup=back_keyboard(),
        )
        return

    if query.data == "collab":
        await msg.edit_caption(
            caption=COLLAB_TEXT,
            parse_mode="Markdown",
            reply_markup=collab_keyboard(),
        )
        return

    if query.data == "exit":
        # НЕ edit_message_text — чтобы не ломать фото-сообщение
        await msg.edit_caption(
            caption="❌ Вы вышли из меню.\n\nНажми /start чтобы открыть снова.",
            reply_markup=None,
        )
        return

# =========================
# ERROR HANDLER (чтобы видеть реальные ошибки в логах)
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.exception("ERROR:", exc_info=context.error)

# =========================
# MAIN
# =========================
def main():
    print("✅ BOT STARTED")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
