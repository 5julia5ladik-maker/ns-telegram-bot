# bot.py
import os
import logging
from pathlib import Path

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================
# НАСТРОЙКИ (Railway Variables / .env / локально)
# =========================
TOKEN = os.getenv("BOT_TOKEN", "").strip()

# По твоему требованию: именно так
INVITE_LINK = os.getenv("INVITE_LINK", "https://t.me/NaturalSense").strip()

# Контакты (кнопками)
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "naturalsense.pr@gmail.com").strip()
CONTACT_TG = os.getenv("CONTACT_TG", "https://t.me/NScollab").strip()

# (опционально) твой Telegram ID, чтобы бот писал "Запущен ✅"
# Если не нужно — просто не задавай переменную ADMIN_ID
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "").strip()
ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW.isdigit() else None

# Картинка обложки рядом с bot.py
COVER_PATH = Path(__file__).with_name("cover.jpg")

# =========================
# ТЕКСТЫ
# =========================
TITLE = "✨ NS • Natural Sense ✨"
MAIN_TEXT = (
    f"{TITLE}\n\n"
    "Распаковки • Бренды • Обзоры\n"
    "Сравнения • Новости\n\n"
    "🔒 Закрытый доступ"
)

ABOUT_TEXT = (
    "ℹ️ *О канале*\n\n"
    "Natural Sense — обзоры косметики, брендов и новинок."
)

COLLAB_TEXT = (
    "🤝 *Сотрудничество*\n\n"
    "Свяжитесь с нами напрямую:"
)

# =========================
# КНОПКИ
# =========================
def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ])

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅ Назад", callback_data="back")]
    ])

def collab_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=f"mailto:{CONTACT_EMAIL}")],
        [InlineKeyboardButton("💬 Написать в Telegram", url=CONTACT_TG)],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# ЛОГИ
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
log = logging.getLogger("ns_bot")

# =========================
# ХЕЛПЕРЫ
# =========================
async def send_cover(update: Update, caption: str, reply_markup: InlineKeyboardMarkup):
    """Отправляет главное сообщение с картинкой (как на твоём примере)."""
    chat = update.effective_chat
    if not chat:
        return

    if not COVER_PATH.exists():
        # Если cover.jpg забыли — просто текстом, чтобы бот не падал
        await update.message.reply_text(caption, reply_markup=reply_markup)
        return

    with COVER_PATH.open("rb") as f:
        await chat.send_photo(
            photo=f,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )

async def edit_caption(update: Update, caption: str, reply_markup: InlineKeyboardMarkup):
    """Меняет caption у текущего сообщения (чтобы всегда было красиво и в одном посте)."""
    query = update.callback_query
    if not query or not query.message:
        return
    await query.edit_message_caption(
        caption=caption,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
    )

# =========================
# ХЕНДЛЕРЫ
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /start -> отправляем картинку + кнопки (как на последнем скрине)
    if not TOKEN:
        await update.message.reply_text("❌ BOT_TOKEN не задан в переменных.")
        return

    await send_cover(update, MAIN_TEXT, main_keyboard())

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return

    await query.answer()

    data = query.data

    if data == "about":
        await edit_caption(update, ABOUT_TEXT, back_keyboard())

    elif data == "collab":
        await edit_caption(update, COLLAB_TEXT, collab_keyboard())

    elif data == "back":
        await edit_caption(update, MAIN_TEXT, main_keyboard())

    elif data == "exit":
        # Закрываем меню (убираем кнопки)
        await query.edit_message_caption(
            caption="Ок. До связи 👌",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=None,
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.exception("Unhandled error: %s", context.error)

async def post_init(app: Application):
    # Сообщение админу "бот запущен" (если ADMIN_ID задан)
    if ADMIN_ID:
        try:
            await app.bot.send_message(chat_id=ADMIN_ID, text="✅ NS Bot запущен и работает 24/7.")
        except Exception:
            log.exception("Не смог отправить сообщение админу (ADMIN_ID).")

def main():
    if not TOKEN:
        raise ValueError("❌ Задай переменную BOT_TOKEN (токен от @BotFather).")

    app = Application.builder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_error_handler(error_handler)

    log.info("Bot started.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
