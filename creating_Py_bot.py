import json
import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

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
def update_user_data(user_id, username, team, wishes, receiver,filename='bazadannih.json'):
    data = load_data(filename)
    if str(user_id) not in data['users']:
        data['users'][str(user_id)] = {
            'username': username,
            'team': team,
            'wishes': wishes,
            'receiver': receiver
        }
    else:
        # Обновляем данные пользователя
        data['users'][str(user_id)]['username'] = username
        data['users'][str(user_id)]['team'] = team
        data['users'][str(user_id)]['wishes'] = wishes
        data['users'][str(user_id)]['receiver'] = receiver
        
    save_data(filename, data)


# Начальная функция
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    context.user_data['username'] = username

    update_user_data(user_id, username, team='Не указана', wishes='Не указаны', receiver='не указаны')

    update.message.reply_text(f"Приветствую тебя, Дорогой Санта, {username}! 🎅\n"
                              "Я твой помощник - Вельф. Моя задача состоит в том, чтобы помочь тебе найти Санту, которому ты будешь дарить подарок.")

    # Кнопочки
    keyboard = [
        [InlineKeyboardButton("У меня есть команда", callback_data='join_team')],
        [InlineKeyboardButton("Создать свою команду", callback_data='create_team')],
        [InlineKeyboardButton("Как это работает?", callback_data='how_it_works')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("У тебя уже есть команда или ты хочешь создать свою?", reply_markup=reply_markup)

# Обработка выбора команды
def team_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data == "join_team":
        query.message.reply_text("Пожалуйста, укажи название команды.")
        context.user_data['action'] = 'join_team'
    elif query.data == "create_team":
        query.message.reply_text("Придумай название для своей команды.")
        context.user_data['action'] = 'create_team'
    elif query.data == "how_it_works":
        query.message.reply_text("Этот бот поможет тебе поучаствовать в игре Тайный Санта."
                                  "Ты можешь создать свою команду или присоединиться к существующей."
                                  "После этого напиши свои пожелания. А когда вся команда будет в сборе, Главный Санта запустит процесс рандомизации участников.")


# Присоединение к команде
def join_team(update: Update, context: CallbackContext, team_name: str = None) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    team_name = update.message.text.strip() if team_name is None else team_name

    data = load_data('bazadannih.json')

    # Проверяем, не состоит ли пользователь уже в другой команде
    if str(user_id) in data['users'] and data['users'][str(user_id)]['team'] != 'Не указана':
        update.message.reply_text("Ты уже состоишь в команде и не можешь присоединиться к другой.")
        return

    # Проверяем, существует ли команда
    if team_name in data['teams']:
        # Добавляем пользователя в команду
        context.user_data['team'] = team_name
        data['teams'][team_name]['members'].append(user_id)

        # Обновляем данные пользователя в базе данных
        update_user_data(user_id, username, team=team_name, wishes='Не указаны', receiver='Не назначен', filename='bazadannih.json')

        # Сохраняем обновленные данные
        save_data('bazadannih.json', data)

        # Спрашиваем пожелания
        context.user_data['action'] = 'write_wishes'
        update.message.reply_text("Ты присоединился к команде! Пожалуйста, напиши свои пожелания.")

    else:
        update.message.reply_text("Команда с таким именем не найдена.")


# Создание команды
def create_team(update: Update, context: CallbackContext, team_name: str) -> None:                 
    user_id = update.message.from_user.id
    team_name = update.message.text.strip()
    data = load_data('bazadannih.json')

    if team_name in data['teams']:
        update.message.reply_text("Команда с таким именем уже существует, выбери другое название.")
        return

    # Создание новой команды
    data['teams'][team_name] = {
        'categories': [],
        'members': [user_id],
        'creator': user_id
    }
    save_data('bazadannih.json', data)
    
    update_user_data(user_id, context.user_data['username'], team=team_name, wishes='Не указаны', receiver='Не назначен')        
    
    update.message.reply_text("Команда создана.")
    context.user_data['team'] = team_name
    
    # Переводим пользователя в режим ввода пожеланий
    context.user_data['action'] = 'write_wishes'

    # Спрашиваем пожелания
    update.message.reply_text("Пожалуйста, напиши свои пожелания.")


# Обработка текстовых сообщений
def write_wishes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_action = context.user_data.get('action')  # Проверяем текущее действие пользователя
    data = load_data('bazadannih.json')

    # Инициализация team_name
    team_name = None

    # Проверяем, состоит ли пользователь уже в команде
    if str(user_id) in data['users'] and data['users'][str(user_id)]['team'] != 'Не указана':
        team_name = data['users'][str(user_id)]['team']  # Получаем команду из БД

    if user_action == 'create_team':  # Если пользователь создаёт команду
        team_name = update.message.text.strip()
        create_team(update, context, team_name)  # Вызываем функцию для создания команды
    elif user_action == 'join_team' and (team_name == 'Не указана' or not team_name):  # Если пользователь присоединяется к команде и не состоит в ней
        team_name = update.message.text.strip()
        join_team(update, context, team_name)  # Вызываем функцию для присоединения к команде
    elif user_action == 'write_wishes' or (team_name and team_name != 'Не указана'):  # Если пользователь пишет пожелания или уже в команде
        wishes = update.message.text.strip()

        # Проверяем длину пожеланий
        if len(wishes) < 10:
            update.message.reply_text("Пожалуйста, напиши более развернутые пожелания.")
            return

        # Сохраняем пожелания в БД
        data['users'][str(user_id)]['wishes'] = wishes
        save_data('bazadannih.json', data)

        # Отправляем участнику сообщение об ожидании
        update.message.reply_text("Твои пожелания записаны! Теперь подожди, когда создатель команды запустит рандомизацию.")

        # Проверяем, является ли текущий пользователь создателем команды
        creator_id = data['teams'][team_name]['creator']
        if creator_id == user_id:
            # Если это создатель команды, показываем ему кнопку для рандомизации
            show_action_buttons(update, context)
        else:
            context.bot.send_message(
                chat_id=creator_id,
                text="Все участники команды написали свои пожелания! А теперь подожди, пока Главный Санта не запустит рандомизацию.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Запустить распределение подарков", callback_data='distribute')]])
            )

        # Сбрасываем действие после ввода пожеланий
        context.user_data['action'] = None
    else:
        update.message.reply_text("Пожалуйста, сначала присоединись к команде или создай её.")


# Функция для отображения кнопок действия
def show_action_buttons(update: Update, context: CallbackContext):
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id

    # Кнопка для запуска распределения подарков
    keyboard = [[InlineKeyboardButton("❄️ Запустить распределение подарков ❄️", callback_data='distribute')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text=" ❄️Готовы начать игру Тайный Санта?❄️", reply_markup=reply_markup)


# Функция распределения подарков
def distribute(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    data = load_data('bazadannih.json')

    user_id = query.from_user.id
    team_name = data['users'][str(user_id)]['team']

    if not team_name or team_name == 'Не указана':
        query.message.reply_text("Ты не состоишь в команде.")
        return

    team = data['teams'][team_name]
    members = team['members']

    if len(members) < 2:
        query.message.reply_text("Недостаточно участников для игры.")
        return

    # Рандомизация участников
    shuffled_members = members[:]
    random.shuffle(shuffled_members)

    # Сопоставляем участников
    for i in range(len(shuffled_members)):
        giver = shuffled_members[i]
        receiver = shuffled_members[(i + 1) % len(shuffled_members)]

        # Обновляем данные получателей в БД
        data['users'][str(giver)]['receiver'] = data['users'][str(receiver)]['username']

        # Отправляем сообщение каждому участнику
        context.bot.send_message(giver, f"Ты будешь дарить подарок {data['users'][str(receiver)]['username']}!")
        context.bot.send_message(giver, f"Пожелания: {data['users'][str(receiver)]['wishes']}")

    save_data('bazadannih.json', data)

    # Уведомляем создателя команды
    query.message.reply_text("Распределение подарков завершено!")
    query.message.reply_text(f"Не забудь приготовить подарок вовремя, а то {data['users'][str(receiver)]['username']} останется без него!")
    query.message.reply_text("С Новым годом!")


# Специальный обработчик для distribute
def distribute_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    distribute(update, context)  # Вызываем функцию распределения подарков

# Основная функция
def main() -> None:
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'

    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(team_selection, pattern="^(join_team|create_team|how_it_works)$"))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_wishes))

    # Специальный обработчик для распределения подарков
    dispatcher.add_handler(CallbackQueryHandler(distribute_callback, pattern='^distribute$'))

def show_action_buttons(update: Update, context: CallbackContext) -> None:
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id

    keyboard = [
        [InlineKeyboardButton("Оценить работу Secret Santa", callback_data='rate_secret_santa')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


# Обработчик для оценки работы Secret НSanta
def rate_secret_santa(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.message.reply_text("Пожалуйста, оцените работу Secret Santa, ответив на это сообщение числом от 1 до 10.")

def handle_rating(update: Update, context: CallbackContext) -> None:
    rating = update.message.text.strip()
    if rating.isdigit() and 1 <= int(rating) <= 10:
        update.message.reply_text(f"Спасибо за вашу оценку: {rating}!")
        # Сохраните или обработайте оценку здесь
    else:
        update.message.reply_text("Пожалуйста, введите число от 1 до 10 для оценки.")

def main() -> None:
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(team_selection, pattern="^(join_team|create_team|how_it_works)$"))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_wishes))
    dispatcher.add_handler(CallbackQueryHandler(distribute_callback, pattern='^distribute$'))

    # Обработчик для оценки работы Secret Santa
    dispatcher.add_handler(CallbackQueryHandler(rate_secret_santa, pattern='^rate_secret_santa$'))
    dispatcher.add_handler(MessageHandler(Filters.text & Filters.reply, handle_rating))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

    

