import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Чтение файла
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"users": {}, "teams": {}}  # Если файла нет, создаем пустую базу данных для пользователей и команд

# Запись файла
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Обновление данных пользователя
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

    update.message.reply_text(f"Приветствую тебя, {username}, Дорогой Санта!")

    # Кнопочки
    keyboard = [
        [InlineKeyboardButton("У меня есть команда", callback_data='join_team')],
        [InlineKeyboardButton("Создать свою команду", callback_data='create_team')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)  # Инициализация reply_markup

    update.message.reply_text("У тебя уже есть команда или ты хочешь создать свою?", reply_markup=reply_markup)

# Обработка выбора команды
def team_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query  # Получаем данные о кнопке
    query.answer()  # Отвечаем на запрос

    if query.data == "join_team":  # Пользователь хочет присоединиться к команде
        query.message.reply_text("Пожалуйста, укажи название команды.")
        context.user_data['action'] = 'join_team'  # Сохраняем действие в пользовательских данных
    elif query.data == "create_team":  # Пользователь хочет создать свою команду
        query.message.reply_text("Придумай название для своей команды и задай ценовые категории.")
        context.user_data['action'] = 'create_team'  # Сохраняем действие в пользовательских данных

# Присоединение к команде
def join_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    team_name = update.message.text.strip()  # Получаем название команды

    data = load_data('bazadannih.json')  # Загружаем базу данных
    if team_name in data['teams']:  # Если команда существует
        context.user_data['team'] = team_name
        update_user_data(user_id, context.user_data['username'], team=team_name, wishes='Не указаны')  # Обновляем данные пользователя
        update.message.reply_text("Теперь выбери свою ценовую категорию.", reply_markup=price_buttons())  # Отправляем выбор ценовой категории
    else:
        update.message.reply_text("Команда с таким именем не найдена.")  # Если команда не найдена

# Создание команды
def create_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id  # Получаем ID пользователя
    team_name = update.message.text.strip()  # Получаем название команды
    data = load_data('bazadannih.json')  # Загружаем базу данных

    if team_name in data['teams']:  # Если команда с таким названием уже существует
        update.message.reply_text("Команда с таким именем уже существует, выбери другое.")
    else:
        data['teams'][team_name] = {'categories': [], 'members': []}  # Создаем новую команду в базе
        save_data('bazadannih.json', data)  # Сохраняем изменения
        update_user_data(user_id, context.user_data['username'], team=team_name, wishes='Не указаны')  # Обновляем данные пользователя
        update.message.reply_text("Команда создана. Теперь укажи ценовые категории.")
        context.user_data['team'] = team_name  # Сохраняем команду пользователя
        context.user_data['action'] = 'set_price_category'  # Указываем действие

# Кнопки для ценовой категории
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

# Запись пожеланий
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
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: join_team(update, context) if context.user_data.get('action') == 'join_team' else create_team(update, context)))
    dispatcher.add_handler(CallbackQueryHandler(price_selection, pattern='price_500|price_500_1000|price_1000'))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, write_whishes))

    # Запуск бота
    updater.start_polling()

    # Работать, пока не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
