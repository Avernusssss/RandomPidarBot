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
    (637476473, "Никиточка Гекон"),
    (944818724, "Андроид Эндрю"),
    (2012379285, "Десептикон Семён"),
    (795615948, "Лупа Залупа"),
    (1303275983, "Лера Писька"),
    (5623885884, "вЕталЕГ"),
    (775411734, "Егор опять?"),
    (1164588090, "Нефор"),  
    (685317770, "Чурка"),
    (5606121328, "Дед инсайдик"),
    (7026933741, "Главный шиз конфы"),
    (402356989, "ЗАМЗАМЫЧ"),
    (850750045, "МАКСИМСУКА"),
]

# Варианты сообщений
MESSAGES = [
    "Пидор дня {} - поздравляем!",
    "Сегодня пидором объявляется {}",
    "Проверка показала, что {} - пидор",
    "Выбор сделан, пидор дня - {}",
    "Выпал {} - ну ты понел",
    "Рандом выбрал {} - ничего не поделаешь",
    "Сегодня {} - красавчик (пидорского типа)",
    "Пидор обнаружен: {}",
]

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Теперь я буду искать пидоров')

async def send_daily_message():
    selected_user_id, selected_user_name = random.choice(USERS)
    message_template = random.choice(MESSAGES)
    user_mention = f"[‌{selected_user_name}](tg://user?id={selected_user_id})"
    message = message_template.format(user_mention)
    
    await bot.send_message(
        chat_id=CHAT_ID, 
        text=message,
        parse_mode="Markdown"
    )

async def scheduler():
    aioschedule.every().day.at("09:00").do(send_daily_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def main():
    # Отправляем первое сообщение при запуске
    await bot.send_message(chat_id=CHAT_ID, text="Меня ебали, я сосал")
    await asyncio.sleep(5)
    await send_daily_message()
    
    # Запускаем планировщик в отдельной задаче
    asyncio.create_task(scheduler())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
