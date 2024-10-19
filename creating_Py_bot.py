import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

# Это читаем файл
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"users": {}, "teams": {}}  # Если файла нет, создаём пустую базу данных для пользователей и команд

# Это записываем файл
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция для добавления в БД информации про новых юзеров
def update_user_data(user_id, username, team, wishes, filename, money_group="bazadannih.json"):
    data = load_data(filename)  # Загружаем существующие данные
    data['users'][str(user_id)] = {  # Обновляем данные пользователя
        'username': username,
        'team': team,
        'wishes': wishes,
        'money_group': money_group,
    }
    save_data(filename, data)  # Сохраняем изменения

# Начальная функция
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    username = update.message.from_user.username  # Получаем имя пользователя
    update_user_data(user_id, username, team='Не указана', wishes='Не указаны')  # Обновляем базу данных пользователя

    update.message.reply_text(f"Приветствую тебя, {username}, Дорогой Санта! Я твой помощник - Вельф.")

    # Кнопочки
    keyboard = [
        [InlineKeyboardButton("У меня есть команда", callback_data='join_team')],
        [InlineKeyboardButton("Создать свою команду", callback_data='create_team')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)  # Инициализация reply_markup

    update.message.reply_text("У тебя уже есть команда или ты хочешь создать свою?", reply_markup=reply_markup)

    )

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    # Смотрим, какую кнопочку жмякнули
    if query.data == 'set_team':
        query.edit_message_text(text="Пожалуйста, укажи свою команду с помощью команды /setteam.")
    elif query.data == 'set_wishes':
        query.edit_message_text(text="Пожалуйста, укажи свои желания с помощью команды /setwishes.")
    elif query.data == 'start_game':
        query.edit_message_text(text="Игра начинается!")
        # Здесь можно добавить логику игры
    elif query.data == 'help':
        query.edit_message_text(text="Я помогу тебе с чем смогу! Напиши /start, чтобы начать.")

# Создаем функцию для определения команды
def set_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if len(context.args) > 0:  # Проверяем, чтобы название команды не было пустым
        team = ' '.join(context.args)
        update_user_data(user_id, username, team, wishes='Не указаны')
        update.message.reply_text(f'Команда {team} установлена')
    else:
        update.message.reply_text("Пожалуйста, укажите команду после команды /setteam.")

# Функция для помощи
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Я помогу тебе с чем смогу! Напиши /start, чтобы начать.')

def main():
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'

    # Создаем объект Updater и передаем токен
    updater = Updater(TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("setteam", set_team))
    dispatcher.add_handler(CallbackQueryHandler(button))  # Добавляем обработчик кнопок

    # Запуск бота
    updater.start_polling()

    # Работать, пока не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
