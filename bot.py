import logging
import os
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram.error import BadRequest

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Создаем Flask веб-сервер для keep-alive
app = Flask(__name__)

# Имя канала для проверки подписки
CHANNEL_USERNAME = "@konovalov_main"  # Заменить на твой канал
CLOSED_CHANNEL_LINK = "https://t.me/+WXhlETLjSKAxMWEy"  # Ссылка на закрытый канал

@app.route('/')
def index():
    return "Bot is running!"

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    try:
        # Проверяем подписку
        member = update.bot.get_chat_member(CHANNEL_USERNAME, user_id)

        if member.status in ['member', 'administrator', 'creator']:
            # Если подписан, отправляем ссылку на закрытый канал
            update.message.reply_text(f'Вы подписаны на канал! Вот ссылка на закрытый канал: {CLOSED_CHANNEL_LINK}')
        else:
            # Если не подписан, просим подписаться и даем кнопку для повторной проверки
            keyboard = [
                [InlineKeyboardButton("Я подписался! Проверить снова", callback_data='check_subscription')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(f'Для доступа необходимо подписаться на канал {CHANNEL_USERNAME}.\n\n'
                                      f'После подписки нажмите на кнопку ниже для повторной проверки подписки.',
                                      reply_markup=reply_markup)

    except BadRequest:
        update.message.reply_text('Не могу проверить вашу подписку. Попробуйте еще раз.')

def check_subscription(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    try:
        # Проверяем подписку
        member = update.bot.get_chat_member(CHANNEL_USERNAME, user_id)

        if member.status in ['member', 'administrator', 'creator']:
            # Если подписан, отправляем ссылку на закрытый канал
            update.callback_query.answer()
            update.callback_query.message.reply_text(f'Вы подписаны на канал! Вот ссылка на закрытый канал: {CLOSED_CHANNEL_LINK}')
        else:
            # Если не подписан, просим подписаться и даем кнопку для повторной проверки
            update.callback_query.answer()
            keyboard = [
                [InlineKeyboardButton("Я подписался! Проверить снова", callback_data='check_subscription')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.callback_query.message.reply_text(f'Для доступа необходимо подписаться на канал {CHANNEL_USERNAME}.\n\n'
                                                    f'После подписки нажмите на кнопку ниже для повторной проверки подписки.',
                                                    reply_markup=reply_markup)

    except BadRequest:
        update.callback_query.answer()
        update.callback_query.message.reply_text('Не могу проверить вашу подписку. Попробуйте еще раз.')

def main():
    TOKEN = os.getenv("BOT_TOKEN")
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(check_subscription, pattern='check_subscription'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    # Запуск Flask сервера для keep-alive
    from threading import Thread
    def run():
        app.run(host="0.0.0.0", port=8080)
    
    t = Thread(target=run)
    t.start()

    main()
