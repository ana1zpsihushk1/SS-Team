import json
import os

from curses.ascii import US
from telegram import File, Update
from telegram import Updater, CommandHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update_Key_But
from telegram import Updater_Key_But, CommandHandler_Key_But, CallbackQueryHandler_Key_But, CallbackContext_Key_But

#from symbol import while_stmt

#это читаем файл
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"users": {}} # если что возвращаем пустоту

#это записываем файл
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# функция для добавление в бд информации про новых юзеров
def update_user_data (user_id, username, team, wishes, filename = "bazadannih.json"):
    data = load_data(filename)

    data['users'][str(user_id)] = {
        'username': username,
        'team': team,
        'wishes': wishes,
    }

    save_data(filename, data)
  
#начальная функция
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id #получаем id пользователя чтобы его запомнит
    username = update.message.from_user.username #получаем имя пользователя которое стоит в тг чтобы дальше обращаться по нему

    update_user_data(user_id, username, team='Не указана', wishes='Не указаны')

    update.message.reply_text(f"Приветствую тебя {username}, Дорогой Санта! Я твой помощник - Вельф. Моя задача состоит в том, чтобы помочь тебе найти Санту, которому ты будешь дарить подарок, а также осчастливить тебя самого, работавшего весь год.")
    update.message.reply_text("Подскажи-ка, у тебя уже есть команда? Или ты хочешь создать собственную?")
    #update.message.reply_text("ВНИМАНИЕ!!! Команду позже нельзя будет сменить!!!") #как я понимаю это нам тоже надо
    

#создаем функцию для определения команды(не совсем понимаю как это должно выглядить пусть пока будет так)
def set_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if len(context.args) > 0: #проверям чтоб название команды не было пустое
        team = ' '.join(context.args)
        update_user_data(user_id, username, team, wishes='Не указаны')
    
        update.message.user.reply_text(f'Команда {team} установлена')
    else:
        update.message.reply_text("Пожалуйста, укажите команду после команды /setteam.") #если название команды пустое



#Начнем с тебя! Скажи-ка мне, что в этом году придавало тебе больше всего сил? Желаешь ли ты чего-то? - запишем потом
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

    # Запуск бота
    updater.start_polling()

    # Работать, пока не будет остановлен
    updater.idle()

if __name__ == '__main__':
    main()
