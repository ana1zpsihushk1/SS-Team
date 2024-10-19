import json
import os
from shlex import join
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

#обработка выбора команды
def team_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query #получает данные о кнопке
    query.answer #отвечаем на запрос

    if query.data == "join_team": #хочет присоедениться команды
        query.message.reply_text("Пожалуйста, укажи название команды.")
    elif query.data == "create_team": # создает свою команду
        query.message.reply_text("Придумай название для своей команды и задай ценовые категории.")


#присоединяемся к команде
def join_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id #получаем id
    team_name = update.message.text.strip()  # Получаем название команды

    data = load_data('bazadannih.json')  # Загружаем базу данных
    if team_name in data['teams']: #если уже существует такая команда
        context.user_data['team'] = team_name
        update.message.reply_text("Теперь выбери свою ценовую категорию.", reply_markup=create_price_buttons())# Отправляем пользователю сообщение с выбором ценовой категории
    else:
        update.message.reply_text("Команда с таким именем не найдена.")  # Если команда не найдена

#создаем команду
def create_team(update: Update, context: CallbackContext) -> None:
    team_name = update.message.text.strip()  # Получаем название команды
    data = load_data('bazadannih.json')  # Загружаем базу данных
    if team_name in data['teams']:  # Если команда с таким названием уже существует
        update.message.reply_text("Команда с таким именем уже существует, выбери другое.")
    else:
        data['teams'][team_name] = {'categories': [], 'members': []}  # Создаём новую команду в базе
        save_data('bazadannih.json', data)  # Сохраняем изменения
        update.message.reply_text("Команда создана. Теперь укажи ценовые категории.")




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
