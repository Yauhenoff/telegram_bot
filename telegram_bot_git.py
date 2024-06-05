import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, CommandHandler
import schedule
import time
import json
from threading import Thread

# Настройка логирования
logging.basicConfig(filename='bot_log.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)



def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {}

def save_user_data(user_data):
    try:
        with open('user_data.json', 'w') as file:
            json.dump(user_data, file)
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

def forward_to_target(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        logger.info("No message received")
        return

    from_chat_id = message.chat_id
    user_name = message.from_user.full_name or message.from_user.username
    username = message.from_user.username or "No username"

    # Обновляем данные пользователя
    existing_user_data = load_user_data()
    existing_user_data[str(from_chat_id)] = {'name': user_name, 'username': username}
    save_user_data(existing_user_data)
    logger.info(f"User data updated for {from_chat_id}")

    # Отправляем сообщение TARGET_CHAT_ID с информацией о пользователе
    reply_text = f"Message from {user_name} (ID: {from_chat_id}, username: @{username}):\n{message.text}"
    context.bot.send_message(chat_id=TARGET_CHAT_ID, text=reply_text)
    logger.info(f"Message from {from_chat_id} forwarded to TARGET_CHAT_ID")

def show_reply_buttons(update: Update, context: CallbackContext):
    user_data = load_user_data()
    keyboard = [
        [InlineKeyboardButton(f"Reply to {data['name']} (@{data['username']})", callback_data=chat_id)]
        for chat_id, data in user_data.items()
    ]
    # Добавляем кнопку "Отправить всем сообщение" в конец списка
    keyboard.append([InlineKeyboardButton("Отправить всем сообщение", callback_data='send_to_all')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=TARGET_CHAT_ID, text="Choose a user to reply or send a message to all:", reply_markup=reply_markup)
    logger.info("Reply buttons displayed for all users in user_data.json and the option to send a message to all")

def handle_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == 'send_to_all':
        context.user_data['send_to_all'] = True
        query.edit_message_text(text="You have chosen to send a message to all users.")
    else:
        context.user_data['selected_user'] = query.data
        context.user_data['send_to_all'] = False
        query.edit_message_text(text=f"Selected user {query.data} for reply.")
    logger.info(f"Selection made for {query.data}")

def send_reply_to_selected_user(update: Update, context: CallbackContext):
    message = update.message
    if 'send_to_all' in context.user_data and context.user_data['send_to_all']:
        user_data = load_user_data()
        for chat_id in user_data.keys():
            context.bot.send_message(chat_id=int(chat_id), text=message.text)
        logger.info("Message sent to all users.")
    elif 'selected_user' in context.user_data:
        selected_user = context.user_data.get('selected_user')
        context.bot.send_message(chat_id=int(selected_user), text=message.text)
        logger.info(f"Reply sent to user {selected_user}.")
    context.user_data.clear()  # Clearing the selection after sending the message

def command_show_users(update: Update, context: CallbackContext):
    show_reply_buttons(update, context)

def scheduled_task(message_text, chat_id=None):
    if chat_id:
        # Send to a specific user
        try:
            updater.bot.send_message(chat_id=int(chat_id), text=message_text)
            logger.info(f"Scheduled message sent to user {chat_id}.")
        except Exception as e:
            logger.error(f"Error sending scheduled message to user {chat_id}: {e}")
    else:
        # Send to all users
        user_data = load_user_data()
        for user_chat_id in user_data.keys():
            try:
                updater.bot.send_message(chat_id=int(user_chat_id), text=message_text)
                logger.info("Scheduled message sent to all users.")
            except Exception as e:
                logger.error(f"Error sending scheduled message to user {user_chat_id}: {e}")

if __name__ == '__main__':


    dp = updater.dispatcher
    dp.add_handler(CommandHandler("u", command_show_users))
    dp.add_handler(MessageHandler(Filters.text & Filters.chat(TARGET_CHAT_ID), send_reply_to_selected_user))
    dp.add_handler(CallbackQueryHandler(handle_callback_query))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, forward_to_target))

    Schedule tasks for sending messages
    schedule.every().day.at("20:55:10").do(scheduled_task, message_text='Привет, ровно через 10 секунд вам......')
    schedule.every().day.at("20:55:12").do(scheduled_task, message_text='1')
    schedule.every().day.at("20:55:14").do(scheduled_task, message_text='2')
    schedule.every().day.at("20:55:16").do(scheduled_task, message_text='3')
    schedule.every().day.at("20:55:18").do(scheduled_task, message_text='4')
    schedule.every().day.at("20:55:20").do(scheduled_task, message_text='5')
    schedule.every().day.at("20:55:22").do(scheduled_task, message_text='6')
    schedule.every().day.at("20:55:24").do(scheduled_task, message_text='7')
    schedule.every().day.at("20:55:26").do(scheduled_task, message_text='8')
    schedule.every().day.at("20:55:28").do(scheduled_task, message_text='9')
    schedule.every().day.at("20:59:30").do(scheduled_task, message_text='Извиняюсь, я просто прохожу тестирование!')

    Добавление задачи по расписанию для отправки сообщения конкретному пользователю
    specific_user_chat_id = '578714257'  # Замените на реальный chat_id пользователя
    schedule.every().day.at("20:05:25").do(scheduled_task, message_text='Ну как вам бот???',
                                           chat_id=specific_user_chat_id)

    Thread for running scheduled tasks
    def job_thread():
        while True:
            schedule.run_pending()
            time.sleep(1)

    thread = Thread(target=job_thread)
    thread.start()

    updater.start_polling()
    updater.idle()
