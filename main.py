import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import random
from datetime import datetime
import aioschedule
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# Получаем значения из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Список пользователей в формате (user_id, имя)
USERS = [
    (123456789, "Gekkon"),  # Замените на реальные ID и имена
    (987654321, "Aibezwer"),
    # Добавьте остальных пользователей
]

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Бот запущен и будет отправлять ежедневное сообщение')

async def send_daily_message():
    selected_user_id, selected_user_name = random.choice(USERS)
    message = f"Пидор дня [‌{selected_user_name}](tg://user?id={selected_user_id}) - отвечает за все!"
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=message,
        parse_mode="Markdown"
    )

async def scheduler():
    aioschedule.every().day.at("12:00").do(send_daily_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def main():
    # Запускаем планировщик в отдельной задаче
    asyncio.create_task(scheduler())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())