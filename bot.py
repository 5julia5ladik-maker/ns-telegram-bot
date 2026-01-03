import os
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime

from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes,
    ConversationHandler, MessageHandler, filters
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# =========================
# CONFIG
# =========================
@dataclass(frozen=True)
class Cfg:
    TOKEN: str = "8367905898:AAEimA-3iLi-JqP9r4cJPnOzYE-L4eYsk-U"
    ADMIN_CHAT_ID: int = 5443870760

    INVITE_LINK: str = "https://t.me/NaturalSense"
    CONTACT_EMAIL: str = "naturalsense.pr@gmail.com"
    CONTACT_TG: str = "@NScollab"
    COVER_PATH: str = "cover.jpg"

    TITLE: str = "✨ NS · Natural Sense"
    SUBTITLE: str = "Распаковки · Бренды · Обзоры\nСравнения · Новости"
    STATUS: str = "🔒 Закрытый доступ"


CFG = Cfg()

MAIN_CAPTION = f"{CFG.TITLE}\n\n{CFG.SUBTITLE}\n\n{CFG.STATUS}"

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

SUCCESS_CAPTION = (
    f"{CFG.TITLE}\n\n"
    "✅ Заявка отправлена.\n"
    "Мы свяжемся с вами по указанному контакту.\n\n"
    f"{CFG.STATUS}"
)

# =========================
# FORM (масштабируется одной таблицей)
# =========================
FORM_FIELDS = [
    ("brand",  "1) 🏷 Название бренда / компании?"),
    ("product","2) 📦 Что продвигаем? (продукт/линейка/ссылка)"),
    ("budget", "3) 💰 Бюджет / условия? (сумма, бартер, % и т.д.)"),
    ("contact","4) 📞 Контакт для связи (email или Telegram @username)"),
    ("extra",  "5) 📝 Доп. детали (необязательно). Если нет — напиши: -"),
]
FORM_STATES = list(range(len(FORM_FIELDS)))  # 0..N-1


# =========================
# HELPERS
# =========================
def tg_link(username: str) -> str:
    return f"https://t.me/{username.replace('@', '').strip()}"

def gmail_compose(email: str) -> str:
    return f"https://mail.google.com/mail/?view=cm&to={email}"

def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Войти в канал", url=CFG.INVITE_LINK)],
        [InlineKeyboardButton("ℹ️ О канале", callback_data="about")],
        [InlineKeyboardButton("🤝 Сотрудничество", callback_data="collab")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")],
    ])

def kb_back() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Назад", callback_data="back")]])

def kb_collab() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=gmail_compose(CFG.CONTACT_EMAIL))],
        [InlineKeyboardButton("💬 Написать в Telegram", url=tg_link(CFG.CONTACT_TG))],
        [InlineKeyboardButton("📦 Предложить интеграцию", callback_data="integration")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

async def notify_admin(bot: Bot, text: str):
    try:
        await bot.send_message(chat_id=CFG.ADMIN_CHAT_ID, text=text)  # plain text
    except Exception:
        logging.exception("Admin notify failed")

async def send_menu_photo(context: ContextTypes.DEFAULT_TYPE, chat_id: int, caption: str):
    """Самый надёжный вариант: отправить НОВОЕ меню с фото."""
    if not os.path.exists(CFG.COVER_PATH):
        await context.bot.send_message(chat_id=chat_id, text="❗ cover.jpg не найден рядом с bot.py")
        return None

    with open(CFG.COVER_PATH, "rb") as f:
        msg = await context.bot.send_photo(
            chat_id=chat_id,
            photo=InputFile(f),
            caption=caption,
            reply_markup=kb_main(),
        )
    # запомним последнее меню (на будущее)
    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id
    return msg


# =========================
# LIFECYCLE
# =========================
async def on_startup(app: Application):
    await notify_admin(app.bot, "✅ BOT STARTED")

async def on_shutdown(app: Application):
    await notify_admin(app.bot, "🛑 BOT STOPPED / RESTARTING")


# =========================
# COMMANDS
# =========================
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_menu_photo(context, update.effective_chat.id, MAIN_CAPTION)


# =========================
# MENU CALLBACKS
# =========================
async def cb_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_caption(caption=MAIN_CAPTION, reply_markup=kb_main())

async def cb_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_caption(caption=ABOUT_TEXT, parse_mode="Markdown", reply_markup=kb_back())

async def cb_collab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_caption(caption=COLLAB_TEXT, parse_mode="Markdown", reply_markup=kb_collab())

async def cb_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.message.edit_caption(caption=EXIT_TEXT, reply_markup=None)

MENU_ACTIONS = {
    "back": cb_back,
    "about": cb_about,
    "collab": cb_collab,
    "exit": cb_exit,
}

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    action = MENU_ACTIONS.get(q.data)
    if action:
        await action(update, context)


# =========================
# INTEGRATION FORM
# =========================
async def form_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data["integration_form"] = {}
    context.user_data["form_step"] = 0

    await q.message.reply_text(INTEGRATION_INTRO + "\n\n" + FORM_FIELDS[0][1], parse_mode="Markdown")
    return FORM_STATES[0]

async def form_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = int(context.user_data.get("form_step", 0))
    text = (update.message.text or "").strip()

    key, _prompt = FORM_FIELDS[step]
    if key == "extra" and text == "-":
        text = "—"
    context.user_data["integration_form"][key] = text

    step += 1
    context.user_data["form_step"] = step

    if step < len(FORM_FIELDS):
        await update.message.reply_text(FORM_FIELDS[step][1])
        return FORM_STATES[step]

    # FINISH
    form = context.user_data.get("integration_form", {})
    user = update.effective_user
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    admin_text = (
        "📦 Новая заявка на интеграцию\n\n"
        f"🕒 {ts}\n"
        f"👤 User: @{user.username if user.username else '—'} (ID: {user.id})\n\n"
        f"🏷 Бренд: {form.get('brand','—')}\n"
        f"📦 Продукт: {form.get('product','—')}\n"
        f"💰 Бюджет/условия: {form.get('budget','—')}\n"
        f"📞 Контакт: {form.get('contact','—')}\n"
        f"📝 Детали: {form.get('extra','—')}\n"
    )
    await notify_admin(context.bot, admin_text)

    # ✅ Как /start, но с подписью успеха (НОВОЕ фото-меню)
    await send_menu_photo(context, update.effective_chat.id, SUCCESS_CAPTION)

    context.user_data.pop("integration_form", None)
    context.user_data.pop("form_step", None)
    return ConversationHandler.END

async def form_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("integration_form", None)
    context.user_data.pop("form_step", None)
    await update.message.reply_text("❌ Заявка отменена. Нажми /start чтобы вернуться в меню.")
    return ConversationHandler.END


# =========================
# ERRORS
# =========================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    err = str(context.error)

    # если запущено 2 инстанса — не спамим
    if "terminated by other getUpdates request" in err:
        logging.warning("Conflict: another getUpdates is running.")
        return

    logging.exception("Unhandled error:", exc_info=context.error)
    await notify_admin(context.bot, f"🚨 Bot error:\n{err}")


# =========================
# MAIN
# =========================
def main():
    app = Application.builder().token(CFG.TOKEN).build()
    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    # /start
    app.add_handler(CommandHandler("start", cmd_start))

    # FORM
    form_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(form_start, pattern=r"^integration$")],
        states={st: [MessageHandler(filters.TEXT & ~filters.COMMAND, form_step)] for st in FORM_STATES},
        fallbacks=[CommandHandler("cancel", form_cancel)],
        allow_reentry=True,
    )
    app.add_handler(form_handler)

    # MENU (исключаем integration, его забирает ConversationHandler)
    app.add_handler(CallbackQueryHandler(menu_router, pattern=r"^(back|about|collab|exit)$"))

    app.add_error_handler(error_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
