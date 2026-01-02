import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
# УТИЛИТЫ
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

    # Запоминаем ID этого сообщения
    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id

async def safe_edit_caption(query, context, *, caption, reply_markup, parse_mode=None):
    """
    Самая надежная правка:
    1) пробуем через bot.edit_message_caption (по сохраненным id)
    2) если не вышло — пробуем query.edit_message_caption
    3) если и это не вышло — отправляем новое сообщение (чтобы не было "не работает")
    """
    chat_id = context.user_data.get("menu_chat_id")
    message_id = context.user_data.get("menu_message_id")

    # 1) По сохраненным ID
    if chat_id and message_id:
        try:
            await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=caption,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )
            return
        except Exception as e:
            logging.exception("edit_message_caption(by saved ids) failed: %s", e)

    # 2) По callback query
    try:
        await query.edit_message_caption(
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
        # на всякий случай пересохраним ID актуального сообщения
        if query.message:
            context.user_data["menu_chat_id"] = query.message.chat_id
            context.user_data["menu_message_id"] = query.message.message_id
        return
    except Exception as e:
        logging.exception("query.edit_message_caption failed: %s", e)

    # 3) Фолбэк: новое сообщение, чтобы точно сработало
    try:
        msg = await query.message.reply_photo(
            photo=query.message.photo[-1].file_id if query.message and query.message.photo else None,
            caption=caption,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )
        context.user_data["menu_chat_id"] = msg.chat_id
        context.user_data["menu_message_id"] = msg.message_id
    except Exception as e:
        logging.exception("fallback send failed: %s", e)
        await query.message.reply_text("Нажми /start чтобы открыть меню заново.")

async def edit_to_main_menu(query, context: ContextTypes.DEFAULT_TYPE):
    await safe_edit_caption(
        query,
        context,
        caption=MAIN_CAPTION,
        reply_markup=main_keyboard(),
        parse_mode=None
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

    # если вдруг прилетело что-то странное
    if not query:
        return

    logging.info("Callback data: %s", query.data)

    # ВАЖНО: обязательно отвечаем на callback
    await query.answer()

    if query.data == "exit":
        await query.message.edit_text("❌ Вы вышли из меню.")
        return

    if query.data == "back":
        await edit_to_main_menu(query, context)
        return

    if query.data == "about":
        await safe_edit_caption(
            query,
            context,
            caption=ABOUT_TEXT,
            reply_markup=back_keyboard(),
            parse_mode="Markdown"
        )
        return

    if query.data == "collab":
        # чтобы ты прямо видел, что нажатие дошло до бота (мгновенный отклик)
        try:
            await query.answer("Открываю контакты ✅", show_alert=False)
        except Exception:
            pass

        await safe_edit_caption(
            query,
            context,
            caption=COLLAB_TEXT,
            reply_markup=collab_keyboard(),
            parse_mode="Markdown"
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

    # allowed_updates — чтобы точно принимались callback-и
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
