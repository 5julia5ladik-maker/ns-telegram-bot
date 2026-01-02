import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

# =========================
# НАСТРОЙКИ
# =========================
TOKEN = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"

INVITE_LINK = "https://t.me/NaturalSense"   # ✅ как ты сказал
CONTACT_EMAIL = "naturalsense.pr@gmail.com"
CONTACT_TG = "@NScollab"

COVER_PATH = "cover.jpg"  # файл рядом с bot.py

# =========================
# ТЕКСТЫ (как на фото)
# =========================
TITLE = "✨ NS · Natural Sense"
SUBTITLE = "Распаковки · Бренды · Обзоры\nСравнения · Новости"
STATUS = "🔒 Закрытый доступ"

MAIN_CAPTION = f"{TITLE}\n\n{SUBTITLE}\n\n{STATUS}"

ABOUT_TEXT = (
    "ℹ️ *О канале*\n\n"
    "Natural Sense — обзоры косметики, брендов и новинок."
)

# Текст для экрана сотрудничества (контакты теперь будут кнопками)
COLLAB_TEXT = (
    "🤝 *Сотрудничество*\n\n"
    "Для предложений и партнёрств свяжитесь с нами удобным способом:"
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
    tg_username = CONTACT_TG.replace("@", "").strip()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=f"mailto:{CONTACT_EMAIL}")],
        [InlineKeyboardButton("💬 Написать в Telegram", url=f"https://t.me/{tg_username}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# УТИЛИТА: отправить "главное меню" С КАРТИНКОЙ
# =========================
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists(COVER_PATH):
        await update.message.reply_text(
            "❗ Не найден файл cover.jpg рядом с bot.py. Положи cover.jpg в папку с bot.py и перезапусти."
        )
        return

    with open(COVER_PATH, "rb") as f:
        msg = await update.message.reply_photo(
            photo=InputFile(f),
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )

    # Запоминаем ID этого сообщения, чтобы потом его редактировать
    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id

async def edit_to_main_menu(query, context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.user_data.get("menu_chat_id")
    message_id = context.user_data.get("menu_message_id")

    if not chat_id or not message_id:
        await query.edit_message_text("Нажми /start чтобы открыть меню заново.")
        return

    await context.bot.edit_message_caption(
        chat_id=chat_id,
        message_id=message_id,
        caption=MAIN_CAPTION,
        reply_markup=main_keyboard(),
    )

# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update, context)

# =========================
# КНОПКИ
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Выйти
    if query.data == "exit":
        await query.edit_message_text("❌ Вы вышли из меню.")
        return

    # Назад
    if query.data == "back":
        await edit_to_main_menu(query, context)
        return

    # О канале
    if query.data == "about":
        await query.edit_message_caption(
            caption=ABOUT_TEXT,
            parse_mode="Markdown",
            reply_markup=back_keyboard(),
        )
        return

    # Сотрудничество (контакты кнопками)
    if query.data == "collab":
        await query.edit_message_caption(
            caption=COLLAB_TEXT,
            parse_mode="Markdown",
            reply_markup=collab_keyboard(),
        )
        return

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
