from telegram import Update
from telegram import Updater, CommandHandler, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update_Key_But
from telegram import Updater_Key_But, CommandHandler_Key_But, CallbackQueryHandler_Key_But, CallbackContext_Key_But

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Приветствую тебя, Дорогой Санта! Я твой помощник - Вельф. Моя задача состоит в том, чтобы помочь тебе найти Санту, которому ты будешь дарить подарок, а также осчастливить тебя самого, работавшего весь год.")
    update.message.reply_text("Подскажи-ка, у тебя уже есть команда? Или ты хочешь создать собственную?")



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