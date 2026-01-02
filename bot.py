import os
import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ====== Railway Variables ======
TOKEN = os.getenv("BOT_TOKEN", "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5443870760"))
INVITE_LINK = os.getenv("INVITE_LINK", "https://t.me/NaturalSense")
CONTACT_TG = os.getenv("CONTACT_TG", "@NScollab")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "naturalsense.pr@gmail.com")

BRAND_TITLE = "NS • Natural Sense ✨"
BRAND_DESC = (
    "Распаковки • Бренды • Обзоры\n"
    "Сравнения • Новости\n\n"
    "🔒 Доступ в канал по кнопке ниже"
)

MENU_TEXT = "Выбери действие:"

logging.basicConfig(level=logging.INFO)

# ====== UI ======
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔓 Войти в канал", url=INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
    ])

def back_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="back")]])

# ====== Handlers ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"{BRAND_TITLE}\n\n{BRAND_DESC}")
    await asyncio.sleep(0.2)
    await update.message.reply_text(MENU_TEXT, reply_markup=main_menu())

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "about":
        text = (
            f"{BRAND_TITLE}\n\n"
            "Премиальная косметика без воды:\n"
            "• распаковки и новинки\n"
            "• честные обзоры\n"
            "• сравнения продуктов\n\n"
            "Нажми «Войти в канал», чтобы открыть ленту."
        )
        await query.edit_message_text(text, reply_markup=back_menu())

    elif query.data == "collab":
        text = (
            "🤝 Сотрудничество\n\n"
            f"Telegram: {CONTACT_TG}\n"
            f"Email: {CONTACT_EMAIL}\n\n"
            "Реклама • бартер • интеграции"
        )
        await query.edit_message_text(text, reply_markup=back_menu())

    elif query.data == "back":
        await query.edit_message_text(MENU_TEXT, reply_markup=main_menu())

# ====== Notify ======
async def notify_startup(app: Application):
    """Runs once after bot starts."""
    if ADMIN_ID:
        try:
            await app.bot.send_message(
                chat_id=ADMIN_ID,
                text="✅ NS Bot запущен и работает (Railway)."
            )
        except Exception as e:
            logging.error("Failed to notify startup: %s", e)

async def notify_crash(app: Application, err: BaseException):
    """Send crash notification."""
    if ADMIN_ID:
        try:
            await app.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🚨 NS Bot упал: {type(err).__name__}: {err}"
            )
        except Exception as e:
            logging.error("Failed to notify crash: %s", e)

def main():
    if not TOKEN:
        raise ValueError("❌ Не задан BOT_TOKEN. Добавь его в Railway → Variables.")
    if not ADMIN_ID:
        print("⚠️ ADMIN_ID не задан. Уведомления в личку не будут приходить.")

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))

    # Start notification
    async def post_init(application: Application):
        await notify_startup(application)

    app.post_init = post_init

    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        # Crash notification (best-effort)
        try:
            asyncio.run(notify_crash(app, e))
        except Exception:
            pass
        raise

if __name__ == "__main__":
    main()
