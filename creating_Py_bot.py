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
        query.message.reply_text("Этот бот поможет вам участвовать в игре Тайный Санта. "
                                  "Вы можете создать свою команду или присоединиться к существующей. "
                                  "Пожалуйста, пишите пожелания и ценовые категории. После этого руководитель команды запустит рандомизацию подарков!")

# Присоединение к команде
# Присоединение к команде
def join_team(update: Update, context: CallbackContext, team_name: str) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    team_name = update.message.text.strip()

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
        
        # Переводим пользователя в режим ввода пожеланий
        context.user_data['action'] = 'write_wishes'
        
        # Спрашиваем пожелания
        update.message.reply_text("Ты присоединился к команде! Пожалуйста, напиши свои пожелания.")
        
        # Сбрасываем действие пользователя и переводим его в режим ввода пожеланий
        context.user_data['action'] = 'write_wishes'
    else:
        update.message.reply_text("Команда с таким именем не найдена.")



# Создание команды
def create_team(update: Update, context: CallbackContext, team_name: str) -> None:                 
    user_id = update.message.from_user.id
    team_name = update.message.text.strip()
    data = load_data('bazadannih.json')

    if team_name in data['teams']:
        update.message.reply_text("Команда с таким именем уже существует, выбери другое.")
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

# Кнопки для ценовой категории
#def price_buttons():
 #   keyboard = [
  #      [InlineKeyboardButton("До 500 руб.", callback_data='price_500')],
   #     [InlineKeyboardButton("500 - 1000 руб.", callback_data='price_500_1000')],
    #    [InlineKeyboardButton("Больше 1000 руб.", callback_data='price_1000')]
   # ]
    #return InlineKeyboardMarkup(keyboard)

# Обработка выбора ценовой категории
#def price_selection(update: Update, context: CallbackContext) -> None:
 #   query = update.callback_query
  #  query.answer()
  #
    #user_id = query.from_user.id
   # category = query.data
   # team = context.user_data.get('team')
#
 #  data = load_data('bazadannih.json')
 #
   # if team and data['teams'][team]['creator'] == user_id:
    #    data['teams'][team]['categories'].append(category)
     #   save_data('bazadannih.json', data)
      #  query.message.reply_text(f"Ценовая категория '{category}' установлена.")
    #else:
     #   query.message.reply_text("Только создатель команды может установить ценовую категорию.")


# Обработка текстовых сообщений
def write_wishes(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_action = context.user_data.get('action')  # Проверяем текущее действие пользователя

    if user_action == 'create_team':  # Если пользователь создаёт команду
        team_name = update.message.text.strip()
        create_team(update, context, team_name)  # Вызываем функцию для создания команды
    elif user_action == 'join_team':  # Если пользователь присоединяется к команде
        team_name = update.message.text.strip()
        join_team(update, context, team_name)  # Вызываем функцию для присоединения к команде
    elif user_action == 'write_wishes':  # Если пользователь пишет пожелания
        wishes = update.message.text.strip()
        
        # Проверяем длину пожеланий
        if len(wishes) < 10:
            update.message.reply_text("Пожалуйста, напишите более развернутые пожелания.")
            return

        # Загружаем данные
        data = load_data('bazadannih.json')
        
        # Проверяем, состоит ли пользователь в команде
        if str(user_id) not in data['users'] or data['users'][str(user_id)]['team'] == 'Не указана':
            update.message.reply_text("Пожалуйста, присоединитесь к команде или создайте её, прежде чем писать пожелания.")
            return
        
        # Сохраняем пожелания в БД
        data['users'][str(user_id)]['wishes'] = wishes

        # Сохраняем обновленные данные
        save_data('bazadannih.json', data)

        update.message.reply_text("Твои пожелания записаны! Теперь подожди, когда создатель команды запустит рандомизацию.")
        
        show_action_buttons(update, context)  # Показываем кнопки действий

    # После ввода текста, сбрасываем действие
    context.user_data['action'] = None





# Функция для отображения кнопок действия
def show_action_buttons(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    team = context.user_data.get('team')
    data = load_data('bazadannih.json')

    if team and data['teams'][team]['creator'] == user_id:
        keyboard = [
            [InlineKeyboardButton("Запустить распределение подарков", callback_data='distribute')],
            [InlineKeyboardButton("Написать пожелание", callback_data='write_wish')]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("Написать пожелание", callback_data='write_wish')]
        ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.message.chat_id, text="Выберите действие:", reply_markup=reply_markup)

# Функция распределения подарков
def distribute(update: Update, context: CallbackContext) -> None:
    user_id = update.callback_query.from_user.id
    team_name = context.user_data.get('team')
    data = load_data('bazadannih.json')

    if team_name not in data['teams'] or len(data['teams'][team_name]['members']) < 2:
        update.callback_query.message.reply_text("Недостаточно участников для игры.")
        return

    # Получаем распределение участников
    assignment = secret_santa(data['teams'][team_name]['members'])

    # Отправляем каждому участнику его получателя
    for giver in assignment:
        receiver = assignment[giver]
        wishes = data['users'][str(receiver)]['wishes']
        username = data['users'][str(receiver)]['username']
        
        context.bot.send_message(
            chat_id=giver,
            text=f"Ты даришь подарок {username} \nПро себя он написал так: {wishes}"
        )

    context.bot.send_message(
        chat_id=user_id,
        text="Распределение завершено! Каждый участник знает, кому он дарит подарок.\n"
             "Когда сделаешь подарок, напиши кодовое слово 'ГОТОВО'."
    )

    # Отправка поздравления с НГ
    context.bot.send_message(chat_id=user_id, text="С Новым Годом! Спасибо, что используешь нашего бота. 🎉")

# Функция рандомизации
def secret_santa(members):
    shuffled = members[:]
    random.shuffle(shuffled)
    return {members[i]: shuffled[i] for i in range(len(members))}

# Основная функция
def main() -> None:
    TOKEN = '7449709461:AAE1M2zp-Z_E6a_5yetifIzPqCH_E-Lb7tE'

    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(team_selection))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_wishes))
    dispatcher.add_handler(CallbackQueryHandler(show_action_buttons))
   # dispatcher.add_handler(CallbackQueryHandler(price_selection, pattern='^price_.*$'))
    dispatcher.add_handler(CallbackQueryHandler(distribute, pattern='^distribute$'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()