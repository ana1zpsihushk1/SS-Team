import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

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
def update_user_data(user_id, username, team, wishes, filename='bazadannih.json', money_group="bazadannih.json"):   
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
    update_user_data(user_id, username, team='Не указана', wishes='Не указаны', filename='bazadannih.json')  # Обновляем базу данных пользователя

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
    query.answer() #отвечаем на запрос

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
        update.message.reply_text("Теперь выбери свою ценовую категорию.", reply_markup=price_buttons())# Отправляем пользователю сообщение с выбором ценовой категории
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
#кнопки для ценновой категории
def price_buttons():
    keyboard = [
        [InlineKeyboardButton("До 500 руб.", callback_data='price_500')],
        [InlineKeyboardButton("500 - 1000 руб.", callback_data='price_500_1000')],
        [InlineKeyboardButton("Больше 1000 руб.", callback_data='price_1000')]   
    ]
    return InlineKeyboardMarkup(keyboard)  # Возвращаем клавиатуру с кнопками

# Обработка выбора ценовой категории
def price_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Получаем данные о нажатой кнопке
    query.answer()

    user_id = query.from_user.id  # Получаем ID пользователя
    category = query.data  # Получаем выбранную категорию

    data = load_data('bazadannih.json')  # Загружаем базу данных
    team = context.user_data.get('team')  # Получаем команду пользователя

    if team:
        # Добавляем пользователя в команду с выбранной категорией
        data['teams'][team]['members'].append({'user_id': user_id, 'category': category})
        save_data('bazadannih.json', data)  # Сохраняем изменения
        query.message.reply_text("Ты успешно присоединился к команде.")
    else:
        query.message.reply_text("Ошибка. Не удалось найти команду.")


def write_whishes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    wishes = update.message.text  # Получаем текст пожеланий

    # Обновляем пожелания в базе данных
    data = load_data('bazadannih.json')
    data['users'][str(user_id)]['wishes'] = wishes
    save_data('bazadannih.json', data)

    update.message.reply_text("Твои пожелания записаны!")  # Подтверждаем пользователю


def main():
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'

    # Создаем объект Updater и передаем токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(team_selection, pattern='join_team|create_team'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, join_team))
    dispatcher.add_handler(CallbackQueryHandler(price_selection, pattern='price_500|price_500_1000|price_1000'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_whishes))

    # Запуск бота
    updater.start_polling()

    # Работать, пока не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
