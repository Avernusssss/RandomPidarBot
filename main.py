import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import random
from datetime import datetime
from dotenv import load_dotenv
import aioschedule
import os
import pytz

# Загружаем переменные из .env файла
load_dotenv()

# Получаем значения из переменных окружения
TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

# Список пользователей в формате (user_id, имя)
USERS = [
    (637476473, "Гекон"),
    (944818724, "Андроид"),
    (2012379285, "Десептикон"),
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
    moscow_tz = pytz.timezone('Europe/Moscow')
    
    while True:
        now = datetime.now(moscow_tz)
        
        # Вычисляем время до следующих 09:00
        if now.hour >= 9:
            # Если сейчас 9 утра или позже, ждём до завтра
            next_run = now.replace(day=now.day + 1, hour=9, minute=0, second=0, microsecond=0)
        else:
            # Если сейчас раньше 9 утра, ждём до 9 утра сегодня
            next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        # Вычисляем количество секунд до следующего запуска
        delay = (next_run - now).total_seconds()
        
        # Ждём до следующего запуска
        await asyncio.sleep(delay)
        
        # Отправляем сообщение
        await send_daily_message()

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
