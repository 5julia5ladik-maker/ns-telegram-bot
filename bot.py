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

COVER_PATH = "cover.jpg"  # файл рядом с bot.py

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
    "Выберите способ связи:"
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

def back_to_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")]
    ])

def collab_keyboard():
    tg_username = CONTACT_TG.replace("@", "").strip()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=f"mailto:{CONTACT_EMAIL}")],
        [InlineKeyboardButton("💬 Написать в Telegram", url=f"https://t.me/{tg_username}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back_to_menu")],
    ])

# =========================
# ОТПРАВКА ГЛАВНОГО МЕНЮ (фото + кнопки)
# =========================
async def send_main_menu(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(COVER_PATH):
        await context.bot.send_message(
            chat_id=chat_id,
            text="❗ Не найден файл cover.jpg рядом с bot.py. Положи cover.jpg в папку с bot.py и перезапусти."
        )
        return

    with open(COVER_PATH, "rb") as f:
        await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(f),
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update.effective_chat.id, context)

# =========================
# CALLBACK BUTTONS
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat_id

    # Выйти
    if query.data == "exit":
        await query.message.reply_text("❌ Вы вышли из меню.")
        return

    # Назад в главное меню (просто снова показываем фото-меню)
    if query.data == "back_to_menu":
        await send_main_menu(chat_id, context)
        return

    # О канале — отправляем отдельным сообщением + кнопка назад
    if query.data == "about":
        await query.message.reply_text(
            text=ABOUT_TEXT,
            parse_mode="Markdown",
            reply_markup=back_to_menu_keyboard(),
        )
        return

    # Сотрудничество — ВОТ ТУТ 100% будут 2 кнопки (email + telegram)
    if query.data == "collab":
        await query.message.reply_text(
            text=COLLAB_TEXT,
            parse_mode="Markdown",
            reply_markup=collab_keyboard(),
        )
        return

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.exception("Exception while handling an update:", exc_info=context.error)

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
