import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext
import random

# Читаем файл
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"users": {}, "teams": {}}  # Если файла нет, создаём пустую базу данных для пользователей и команд

# Записываем файл
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция для добавления в БД информации про новых пользователей
def update_user_data(user_id, username, team, wishes, receiver, money_group, filename='bazadannih.json'):
    data = load_data(filename)  # Загружаем существующие данные
    if str(user_id) not in data['users']:  # Если пользователь новый
        data['users'][str(user_id)] = {  # Обновляем данные пользователя
            'username': username,
            'team': team,
            'wishes': wishes,
            'receiver': receiver,
            'money_group': money_group,
        }
    save_data(filename, data)  # Сохраняем изменения

# Начальная функция
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    username = update.message.from_user.username  # Получаем имя пользователя
    context.user_data['username'] = username  # Сохраняем имя пользователя в контексте

    update_user_data(user_id, username, team='Не указана', wishes='Не указаны', receiver='Не назначен', money_group='Не указана')  # Обновляем базу данных пользователя

    update.message.reply_text(f"Приветствую тебя, {username}, Дорогой Санта! Я твой помощник - Вельф. Моя задача состоит в том, чтобы помочь тебе найти Санту, которому ты будешь дарить подарок, а также осчастливить тебя самого, работавшего весь год.")

    # Кнопочки
    keyboard = [
        [InlineKeyboardButton("У меня есть команда", callback_data='join_team')],
        [InlineKeyboardButton("Создать свою команду", callback_data='create_team')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)  # Инициализация reply_markup

    update.message.reply_text("У тебя уже есть команда или ты хочешь создать свою?", reply_markup=reply_markup)

# Обработка выбора команды
def team_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Получает данные о кнопке
    query.answer()  # Отвечаем на запрос

    if query.data == "join_team":  # Хочет присоединиться к команде
        query.message.reply_text("Пожалуйста, укажи название команды.")
        context.user_data['action'] = 'join_team'  # Сохраняем действие
    elif query.data == "create_team":  # Создает свою команду
        query.message.reply_text("Придумай название для своей команды")
        context.user_data['action'] = 'create_team'  # Сохраняем действие

# Присоединение к команде с проверкой
def join_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    team_name = update.message.text.strip()  # Получаем название команды

    data = load_data('bazadannih.json')  # Загружаем базу данных

    if str(user_id) in data['users'] and data['users'][str(user_id)]['team'] != 'Не указана':
        update.message.reply_text("Ты уже состоишь в команде и не можешь присоединиться к другой.")
        return  # Выходим из функции, если пользователь уже состоит в команде

    if team_name in data['teams']:  # Если команда найдена
        context.user_data['team'] = team_name
        update.message.reply_text("Теперь выбери свою ценовую категорию.", reply_markup=price_buttons())  # Отправляем пользователю сообщение с выбором ценовой категории
        data['teams'][team_name]['members'].append(user_id)  # Добавляем пользователя в команду
        save_data('bazadannih.json', data)  # Сохраняем изменения
    else:
        update.message.reply_text("Команда с таким именем не найдена.")  # Если команда не найдена

# Создание команды и назначение создателя
def create_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    team_name = update.message.text.strip()  # Получаем название команды
    data = load_data('bazadannih.json')  # Загружаем базу данных

    if 'teams' not in data:
        data['teams'] = {}

    if team_name in data['teams']:  # Если команда с таким названием уже существует
        update.message.reply_text("Команда с таким именем уже существует, выбери другое.")
    else:
        data['teams'][team_name] = {
            'categories': [],
            'members': [user_id],  # Добавляем создателя как первого члена
            'creator': user_id  # Назначаем создателя команды
        }
        save_data('bazadannih.json', data)  # Сохраняем изменения
        
        # Обновляем данные пользователя
        update_user_data(user_id, context.user_data['username'], team=team_name, wishes='Не указаны', receiver='Не назначен', money_group='Не указана')  # Обновляем данные пользователя
        
        update.message.reply_text("Команда создана. Теперь укажи ценовые категории.", reply_markup=price_buttons())  
        context.user_data['team'] = team_name  # Сохраняем команду пользователя

# Кнопки для ценовой категории
def price_buttons():
    keyboard = [
        [InlineKeyboardButton("До 500 руб.", callback_data='price_500')],
        [InlineKeyboardButton("500 - 1000 руб.", callback_data='price_500_1000')],
        [InlineKeyboardButton("Больше 1000 руб.", callback_data='price_1000')]   
    ]
    return InlineKeyboardMarkup(keyboard)  # Возвращаем клавиатуру с кнопками

# Обработка выбора ценовой категории только для создателя
def price_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Получаем данные о нажатой кнопке
    query.answer()

    user_id = query.from_user.id  # Получаем ID пользователя
    category = query.data  # Получаем выбранную категорию
    team = context.user_data.get('team')  # Получаем команду пользователя

    data = load_data('bazadannih.json')  # Загружаем базу данных

    if team and data['teams'][team]['creator'] == user_id:  # Проверяем, является ли пользователь создателем команды
        data['teams'][team]['categories'].append(category)  # Добавляем ценовую категорию в команду
        save_data('bazadannih.json', data)  # Сохраняем изменения
        query.message.reply_text(f"Ценовая категория '{category}' установлена.")
    else:
        query.message.reply_text("Только создатель команды может установить ценовую категорию.")

# Пишем пожелания
def write_whishes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    wishes = update.message.text  # Получаем текст пожеланий

    # Обновляем пожелания в базе данных
    data = load_data('bazadannih.json')
    data['users'][str(user_id)]['wishes'] = wishes
    save_data('bazadannih.json', data)

    update.message.reply_text("Твои пожелания записаны!")  # Подтверждаем пользователю

# Функция распределения подарков
def distribute(update, context):
    data = load_data('bazadannih.json')  # Загружаем базу данных
    team_name = context.user_data.get('team')  # Получаем название команды из данных пользователя

    if team_name not in data['teams'] or len(data['teams'][team_name]['members']) < 2:
        update.message.reply_text("Недостаточно участников для игры.")
        return

    # Получаем распределение участников (кто кому дарит)
    assignment = secret_santa(data['teams'][team_name]['members'])

    # Отправляем каждому личное сообщение о том, кому он дарит подарок
    for giver_info, receiver_info in assignment.items():
        giver_id = giver_info['user_id']  # ID дарителя
        receiver_id = receiver_info['user_id']  # ID получателя
        receiver_wishes = data['users'][str(receiver_id)]['wishes']  # Желания получателя

        context.bot.send_message(chat_id=giver_id,
                                 text=f"Вы дарите подарок {receiver_info['username']}. Его пожелания: {receiver_wishes}")

    update.message.reply_text("Распределение завершено!")

def secret_santa(members):
    givers = members.copy()
    receivers = members.copy()

    random.shuffle(receivers)

    # Перемешиваем получателей, чтобы никто не дарил самому себе
    while any(giver['user_id'] == receiver['user_id'] for giver, receiver in zip(givers, receivers)):
        random.shuffle(receivers)

    return dict(zip(givers, receivers))

def main():
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'

    # Создаем объект Updater и передаем токен
    updater = Updater(TOKEN, use_context=True)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрация обработчиков команд и сообщений
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(team_selection, pattern='join_team|create_team'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: join_team(update, context) if context.user_data.get('action') == 'join_team' else create_team(update, context)))
    dispatcher.add_handler(CallbackQueryHandler(price_selection, pattern='price_500|price_500_1000|price_1000'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_whishes))

    # Запуск бота
    updater.start_polling()

    # Работать, пока не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
