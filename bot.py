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
    "ℹ️ О канале\n\n"
    "Natural Sense — обзоры косметики, брендов и новинок."
)

COLLAB_TEXT = (
    "🤝 Сотрудничество\n\n"
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
    tg_username = CONTACT_TG.replace("@", "").strip()
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Написать на Email", url=f"mailto:{CONTACT_EMAIL}")],
        [InlineKeyboardButton("💬 Написать в Telegram", url=f"https://t.me/{tg_username}")],
        [InlineKeyboardButton("⬅ Назад", callback_data="back")],
    ])

# =========================
# РЕДАКТОР ОДНОГО И ТОГО ЖЕ СООБЩЕНИЯ (фото)
# =========================
async def edit_menu_caption(context: ContextTypes.DEFAULT_TYPE, *, chat_id: int, message_id: int,
                            caption: str, reply_markup: InlineKeyboardMarkup | None):
    # Редактируем ИМЕННО caption у фото (без отправки новых сообщений)
    await context.bot.edit_message_caption(
        chat_id=chat_id,
        message_id=message_id,
        caption=caption,
        reply_markup=reply_markup,
    )

# =========================
# /start -> отправляем ОДНО сообщение с фото и запоминаем его ID
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    context.user_data["menu_chat_id"] = msg.chat_id
    context.user_data["menu_message_id"] = msg.message_id

# =========================
# CALLBACK КНОПКИ (ТОЛЬКО редактируем caption, НЕ шлём новые сообщения)
# =========================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = context.user_data.get("menu_chat_id")
    message_id = context.user_data.get("menu_message_id")

    # если по какой-то причине ID не сохранены — просим /start (без создания лишних сообщений в нормальном сценарии)
    if not chat_id or not message_id:
        try:
            await query.answer("Нажми /start", show_alert=True)
        except Exception:
            pass
        return

    if query.data == "back":
        await edit_menu_caption(
            context,
            chat_id=chat_id,
            message_id=message_id,
            caption=MAIN_CAPTION,
            reply_markup=main_keyboard(),
        )
        return

    if query.data == "about":
        await edit_menu_caption(
            context,
            chat_id=chat_id,
            message_id=message_id,
            caption=ABOUT_TEXT,
            reply_markup=back_keyboard(),
        )
        return

    if query.data == "collab":
        await edit_menu_caption(
            context,
            chat_id=chat_id,
            message_id=message_id,
            caption=COLLAB_TEXT,
            reply_markup=collab_keyboard(),
        )
        return

    if query.data == "exit":
        # НЕ превращаем в текстовое сообщение. Просто меняем caption и убираем кнопки.
        await edit_menu_caption(
            context,
            chat_id=chat_id,
            message_id=message_id,
            caption="❌ Вы вышли из меню.\n\nНажми /start чтобы открыть снова.",
            reply_markup=None,
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
