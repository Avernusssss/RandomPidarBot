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
    (637476473, "Никита Калинин"),
    (944818724, "Андрей Белозерцев"),
    (2012379285, "Семён Варзин"),
    (795615948, "Дмитрий Круглов"),
    (1303275983, "Валерия Песьякова"),
    (5623885884, "Виталий Баймурзаев"),
    (775411734, "Егор Копосов"),
    (1164588090, "Кирилл Поспелов"),  
    (685317770, "Артём Лапин"),
    (5606121328, "Артемий Исаков"),
    (7026933741, "Илья Сулоев"),
    (402356989, "Дмитрий Попов"),
    (850750045, "Максим Малов"),
]

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Теперь я буду искать пидоров')

async def send_daily_message():
    selected_user_id, selected_user_name = random.choice(USERS)
    message = f"Пидор дня [‌{selected_user_name}](tg://user?id={selected_user_id}) - отвечает за все!"
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=message,
        parse_mode="Markdown"
    )

async def scheduler():
    aioschedule.every().day.at("20:20").do(send_daily_message)
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
