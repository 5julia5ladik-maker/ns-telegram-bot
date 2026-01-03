import os
import logging
import asyncio
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# =========================
# НАСТРОЙКИ
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
    "Выберите удобный способ связи или оставьте заявку:"
)

EXIT_TEXT = "❌ Вы вышли из меню.\n\nНажми /start чтобы открыть снова."

INTEGRATION_INTRO = (
    "📦 *Заявка на интеграцию*\n\n"
    "Отвечайте по шагам. Чтобы отменить — отправьте /cancel."
)

# ✅ "как /start, только с подписью успеха"
SUCCESS_CAPTION = (
    f"{TITLE}\n\n"
    "✅ Заявка отправлена.\n"
    "Мы свяжемся с вами по указанному контакту.\n\n"
    f"{STATUS}"
)

# =========================
# STATES (форма)
# =========================
FORM_BRAND, FORM_PRODUCT, FORM_BUDGET, FORM_CONTACT, FORM_EXTRA = range(5)

# =========================
# УВЕДОМЛЕНИЯ АДМИНУ (plain text)
# =========================
async def notify_admin(bot: Bot, text: str):
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=text)
    except Exception as e:
        logging.exception("Failed to notify admin: %s", e)

async def on_startup(app: Application):
    await notify_admin(app.bot, "✅ BOT STARTED")

async def on_shutdown(app: Application):
    await notify_admin(app.bot, "🛑 BOT STOPPED / RESTARTING")

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
    # Telegram иногда ругается на mailto:, поэтому делаем через web
    email_url = f"https://mail.google.com/mail/?view=cm&to={CONTACT_EMAIL}"
    tg_username = CONTACT_TG.replace("@", "").strip()
    tg_url = f"https://t.me/{tg_username}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=email_url)],
        [InlineKeyboardButton("💬 Написать в Telegram", url=tg_url)],
        [InlineKeyboardButton("📦 Предложить интеграцию", callback_data="integration")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# /start: отправить меню (не плодим дубли)
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

    # если меню уже есть — пробуем отредактировать (чтобы /start не спамил)
    if menu_msg_id and menu_chat_id == chat_id:
        try:
            await context.bot.edit_message_caption(
                chat_id=menu_chat_id,
                message_id=menu_msg_id,
                caption=MAIN_CAPTION,
                reply_markup=main_keyboard(),
            )
            return
        except Exception:
            pass

    # иначе отправим новое меню
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
# КНОПКИ МЕНЮ (не форма)
# =========================
async def menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    msg = query.message
    if not msg:
        return

    # Запоминаем текущее меню-сообщение
    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id

    data = query.data

    if data == "back":
        await msg.edit_caption(caption=MAIN_CAPTION, reply_markup=main_keyboard())
        return

    if data == "about":
        await msg.edit_caption(caption=ABOUT_TEXT, parse_mode="Markdown", reply_markup=back_keyboard())
        return

    if data == "collab":
        await msg.edit_caption(caption=COLLAB_TEXT, parse_mode="Markdown", reply_markup=collab_keyboard())
        return

    if data == "exit":
        await msg.edit_caption(caption=EXIT_TEXT, reply_markup=None)
        return

# =========================
# ФОРМА: старт (кнопка "integration" внутри сотрудничества)
# =========================
async def integration_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # помним меню, с которого стартовали
    if query.message:
        context.user_data["menu_chat_id"] = query.message.chat_id
        context.user_data["menu_message_id"] = query.message.message_id

    context.user_data["integration_form"] = {}

    await query.message.reply_text(
        INTEGRATION_INTRO + "\n\n1) 🏷 Название бренда / компании?",
        parse_mode="Markdown",
    )
    return FORM_BRAND

async def integration_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["integration_form"]["brand"] = update.message.text.strip()
    await update.message.reply_text("2) 📦 Что продвигаем? (продукт/линейка/ссылка)")
    return FORM_PRODUCT

async def integration_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["integration_form"]["product"] = update.message.text.strip()
    await update.message.reply_text("3) 💰 Бюджет / условия? (сумма, бартер, % и т.д.)")
    return FORM_BUDGET

async def integration_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["integration_form"]["budget"] = update.message.text.strip()
    await update.message.reply_text("4) 📞 Контакт для связи (email или Telegram @username)")
    return FORM_CONTACT

async def integration_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["integration_form"]["contact"] = update.message.text.strip()
    await update.message.reply_text("5) 📝 Доп. детали (необязательно). Если нет — напиши: -")
    return FORM_EXTRA

async def integration_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    extra = update.message.text.strip()
    if extra == "-":
        extra = "—"

    form = context.user_data.get("integration_form", {})
    user = update.effective_user
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    # сообщение админу
    admin_text = (
        "📦 Новая заявка на интеграцию\n\n"
        f"🕒 {ts}\n"
        f"👤 User: @{user.username if user.username else '—'} (ID: {user.id})\n\n"
        f"🏷 Бренд: {form.get('brand','—')}\n"
        f"📦 Продукт: {form.get('product','—')}\n"
        f"💰 Бюджет/условия: {form.get('budget','—')}\n"
        f"📞 Контакт: {form.get('contact','—')}\n"
        f"📝 Детали: {extra}\n"
    )
    await notify_admin(context.bot, admin_text)

    # ✅ СТАБИЛЬНО: отправляем НОВОЕ меню (как /start), но с SUCCESS_CAPTION
    if not os.path.exists(COVER_PATH):
        await update.message.reply_text("✅ Заявка отправлена. Мы свяжемся с вами по указанному контакту.")
    else:
        with open(COVER_PATH, "rb") as f:
            msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=InputFile(f),
                caption=SUCCESS_CAPTION,
                reply_markup=main_keyboard(),
            )
        # запоминаем новое меню как активное
        context.user_data["menu_chat_id"] = msg.chat_id
        context.user_data["menu_message_id"] = msg.message_id

    context.user_data.pop("integration_form", None)
    return ConversationHandler.END

async def integration_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("integration_form", None)
    await update.message.reply_text("❌ Заявка отменена. Нажми /start чтобы вернуться в меню.")
    return ConversationHandler.END

# =========================
# ERROR HANDLER
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err_text = str(context.error)

    if "terminated by other getUpdates request" in err_text:
        logging.warning("Conflict: another getUpdates instance is running.")
        return

    logging.exception("ERROR:", exc_info=context.error)
    await notify_admin(context.bot, f"🚨 Bot error:\n{err_text}")

# =========================
# MAIN
# =========================
def main():
    print("✅ BOT STARTED")

    app = Application.builder().token(TOKEN).build()
    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    form_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(integration_start, pattern=r"^integration$")],
        states={
            FORM_BRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, integration_brand)],
            FORM_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, integration_product)],
            FORM_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, integration_budget)],
            FORM_CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, integration_contact)],
            FORM_EXTRA: [MessageHandler(filters.TEXT & ~filters.COMMAND, integration_finish)],
        },
        fallbacks=[CommandHandler("cancel", integration_cancel)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(form_handler)

    # меню-кнопки
    app.add_handler(CallbackQueryHandler(menu_buttons))

    app.add_error_handler(error_handler)

    try:
        app.run_polling()
    except Exception as e:
        logging.exception("FATAL CRASH:", exc_info=e)
        try:
            async def _send():
                bot = Bot(TOKEN)
                await notify_admin(bot, f"💥 Fatal crash:\n{e}")
            asyncio.run(_send())
        except Exception:
            pass
        raise

if __name__ == "__main__":
    main()
