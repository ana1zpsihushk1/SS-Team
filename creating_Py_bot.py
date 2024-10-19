import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# это читаем файл
def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {"users": {}}  # если файл не найден, возвращаем пустую структуру

# это записываем файл
def save_data(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# функция для добавления в БД информации про новых юзеров
def update_user_data(user_id, username, team, wishes, filename, money_group="bazadannih.json"):
    data = load_data(filename)

    data['users'][str(user_id)] = {
        'username': username,
        'team': team,
        'wishes': wishes,
        'money_group': money_group,
    }

    save_data(filename, data)

# начальная функция
async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    update_user_data(user_id, username, team='Не указана', wishes='Не указаны')

    await update.message.reply_text(f"Приветствую тебя, {username}, Дорогой Санта! Я твой помощник - Вельф.")
    await update.message.reply_text("У тебя уже есть команда? Или ты хочешь создать собственную?")

# создаем функцию для определения команды
async def set_team(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    if len(context.args) > 0:  # проверяем, чтобы название команды не было пустым
        team = ' '.join(context.args)
        update_user_data(user_id, username, team, wishes='Не указаны')
        await update.message.reply_text(f'Команда {team} установлена.')
    else:
        await update.message.reply_text("Пожалуйста, укажите команду после команды /setteam.")

# команда помощи
async def help_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Я помогу тебе с чем смогу! Напиши /start, чтобы начать.')

# основная функция
def main():
    TOKEN = os.getenv('TELEGRAM_TOKEN')  # Загружаем токен из переменной окружения

    # Создаем приложение и передаем токен
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("setteam", set_team))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
