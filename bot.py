import os
import logging
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# =========================
# НАСТРОЙКИ (v1.0)
# =========================
TOKEN = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"

ADMIN_CHAT_ID = 5443870760

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

EXIT_TEXT = "❌ Вы вышли из меню.\n\nНажми /start чтобы открыть снова."

# =========================
# УВЕДОМЛЕНИЯ АДМИНУ
# =========================
async def notify_admin(bot: Bot, text: str):
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode="Markdown")
    except Exception:
        pass

async def on_startup(app: Application):
    await notify_admin(app.bot, "✅ *Bot started*")

async def on_shutdown(app: Application):
    await notify_admin(app.bot, "🛑 *Bot stopped / restarting*")

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
    # ⚠️ mailto: Telegram может отклонять -> только https://
    email_url = f"https://mail.google.com/mail/?view=cm&to={CONTACT_EMAIL}"
    tg_username = CONTACT_TG.replace("@", "").strip()
    tg_url = f"https://t.me/{tg_username}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=email_url)],
        [InlineKeyboardButton("💬 Написать в Telegram", url=tg_url)],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# ВСПОМОГАТЕЛЬНОЕ: обновить меню (caption + кнопки)
# =========================
async def edit_menu(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int,
                    caption: str, reply_markup: InlineKeyboardMarkup | None,
                    parse_mode: str | None = None):
    await context.bot.edit_message_caption(
        chat_id=chat_id,
        message_id=message_id,
        caption=caption,
        parse_mode=parse_mode,
        reply_markup=reply_markup,
    )

# =========================
# /start: не плодим дубли
# - если меню уже есть -> редактируем его
# - если нет -> создаем одно и сохраняем message_id
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    if not os.path.exists(COVER_PATH):
        await update.message.reply_text(
            "❗ Файл cover.jpg не найден рядом с bot.py. Положи cover.jpg в папку и перезапусти."
        )
        return

    menu_msg_id = context.user_data.get("menu_message_id")
    menu_chat_id = context.user_data.get("menu_chat_id")

    # Если меню уже было создано ранее — пытаемся отредактировать существующее
    if menu_msg_id and menu_chat_id == chat_id:
        try:
            await edit_menu(
                context,
                chat_id=menu_chat_id,
                message_id=menu_msg_id,
                caption=MAIN_CAPTION,
                reply_markup=main_keyboard(),
                parse_mode=None,
            )
            return
        except Exception as e:
            logging.warning("Failed to edit existing menu, will send new. err=%s", e)

    # Иначе — отправляем новое меню и сохраняем ID
    with open(COVER_PATH, "rb") as f:
        msg = await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(f),
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )

    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id

# =========================
# CALLBACK КНОПКИ
# Редактируем ТОЛЬКО одно меню-сообщение (menu_message_id)
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    logging.info(
        "CLICK | user=%s id=%s data=%s",
        query.from_user.username,
        query.from_user.id,
        query.data
    )

    chat_id = context.user_data.get("menu_chat_id")
    message_id = context.user_data.get("menu_message_id")

    # Если меню не найдено (например, после очистки данных) — просим /start
    if not chat_id or not message_id:
        await query.answer("Нажми /start", show_alert=True)
        return

    if query.data == "back":
        await edit_menu(context, chat_id, message_id, MAIN_CAPTION, main_keyboard(), None)
        return

    if query.data == "about":
        await edit_menu(context, chat_id, message_id, ABOUT_TEXT, back_keyboard(), "Markdown")
        return

    if query.data == "collab":
        await edit_menu(context, chat_id, message_id, COLLAB_TEXT, collab_keyboard(), "Markdown")
        return

    if query.data == "exit":
        await edit_menu(context, chat_id, message_id, EXIT_TEXT, None, None)
        return

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err_text = str(context.error)

    # Не спамим админа конфликтами, если вдруг снова запустят 2 инстанса
    if "terminated by other getUpdates request" in err_text:
        logging.warning("Conflict: another getUpdates instance is running.")
        return

    logging.exception("ERROR:", exc_info=context.error)
    await notify_admin(context.bot, f"🚨 *Bot error*\n`{err_text}`")

# =========================
# MAIN
# =========================
def main():
    print("✅ BOT STARTED")

    app = Application.builder().token(TOKEN).build()

    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_error_handler(error_handler)

    try:
        app.run_polling()
    except Exception as e:
        logging.exception("FATAL CRASH:", exc_info=e)

        # Попытка уведомить админа о фатальном креше
        try:
            async def _send():
                bot = Bot(TOKEN)
                await notify_admin(bot, f"💥 *Fatal crash*\n`{e}`")
            asyncio.run(_send())
        except Exception:
            pass

        raise

if __name__ == "__main__":
    main()
