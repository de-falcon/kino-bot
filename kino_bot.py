from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import os  # Fayl boshiga qo‘shilsin

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# Movie nomlari: file_id yoki forward qilish uchun kanal post ID
MOVIES = {
    "10": {
        "file_id": "BAACAgEAAxkBAANLaFghxWWSW6TJw64Z0bi9PaOKjCwAAmoBAAJK4iBHMRAJDIlHyzI2BA",
        "title": "🎬Kino:O'liklar Armiyasi,Tarjima: O'zbek tilida,⚔️Janr: Jangari, ujas"
    },
    "22": (CHANNEL_USERNAME, 22)  # Forward qilish uchun misol
}

# Foydalanuvchi obuna bo‘lganligini tekshiradi
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'creator', 'administrator']:
            return True
        else:
            await update.message.reply_text(f"Iltimos, avval {CHANNEL_USERNAME} kanaliga obuna bo‘ling.")
            return False
    except:
        await update.message.reply_text(f"Iltimos, avval {CHANNEL_USERNAME} kanaliga obuna bo‘ling.")
        return False

# /start buyrug‘i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_subscription(update, context):
        await update.message.reply_text("Salom! Kinoning nomini yozing.")

# Kino yuborish
async def send_movie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        return

    movie_name = update.message.text.lower().strip()
    movie_info = MOVIES.get(movie_name)

    if movie_info:
        if isinstance(movie_info, tuple):
            # Forward qilish (kanaldan)
            channel, post_id = movie_info
            await context.bot.forward_message(
                chat_id=update.effective_chat.id,
                from_chat_id=channel,
                message_id=post_id
            )
        else:
            # Video yuborish (file_id bilan)
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📣 Kanal: Forever Cinema Uz", url="https://t.me/forever_cinemauz")]
            ])
            caption = f"{movie_info['title']} filmi\nKanal: @forever_cinemauz"
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=movie_info["file_id"],
                caption=caption,
                reply_markup=keyboard
            )
    else:
        await update.message.reply_text("Kechirasiz, bunday kino topilmadi. Iltimos, kinoning aniq nomini kiriting.")

# File ID olish (adminlar uchun foydali)
async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"File ID: `{file_id}`", parse_mode='Markdown')

# Botni ishga tushirish
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_movie))
app.add_handler(MessageHandler(filters.VIDEO, get_file_id))

print("Bot ishga tushdi...")

app.run_polling()
