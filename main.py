import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
import aioschedule
import os
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3

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

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    
    # Создаем таблицу для статистики
    c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            user_id INTEGER,
            date DATE,
            PRIMARY KEY (user_id, date)
        )
    ''')
    
    # Создаем таблицу для хранения последних сбросов
    c.execute('''
        CREATE TABLE IF NOT EXISTS last_reset (
            period TEXT PRIMARY KEY,
            reset_date DATE
        )
    ''')
    
    conn.commit()
    conn.close()

# Функция для получения статистики за период
def get_stats(start_date, end_date):
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT user_id, COUNT(*) as count 
        FROM stats 
        WHERE date BETWEEN ? AND ?
        GROUP BY user_id
    ''', (start_date, end_date))
    
    results = c.fetchall()
    conn.close()
    
    return {user_id: count for user_id, count in results}

# Функция для проверки и сброса статистики
def check_and_reset_stats():
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    
    # Проверяем последний сброс недельной статистики
    c.execute('SELECT reset_date FROM last_reset WHERE period = "weekly"')
    last_weekly = c.fetchone()
    
    if not last_weekly or datetime.fromisoformat(last_weekly[0]).isocalendar()[1] != now.isocalendar()[1]:
        c.execute('INSERT OR REPLACE INTO last_reset (period, reset_date) VALUES ("weekly", ?)',
                 (now.isoformat(),))
    
    # Проверяем последний сброс месячной статистики
    c.execute('SELECT reset_date FROM last_reset WHERE period = "monthly"')
    last_monthly = c.fetchone()
    
    if not last_monthly or datetime.fromisoformat(last_monthly[0]).month != now.month:
        c.execute('INSERT OR REPLACE INTO last_reset (period, reset_date) VALUES ("monthly", ?)',
                 (now.isoformat(),))
    
    conn.commit()
    conn.close()

async def send_daily_message():
    selected_user_id, selected_user_name = random.choice(USERS)
    message_template = random.choice(MESSAGES)
    user_mention = f"[‌{selected_user_name}](tg://user?id={selected_user_id})"
    message = message_template.format(user_mention)
    
    # Обновляем статистику
    check_and_reset_stats()
    
    # Записываем новое событие в базу
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    c.execute('INSERT INTO stats (user_id, date) VALUES (?, ?)',
             (selected_user_id, now.date().isoformat()))
    conn.commit()
    conn.close()
    
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

def create_leaderboard_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="За неделю", callback_data="leaderboard_weekly"),
            InlineKeyboardButton(text="За месяц", callback_data="leaderboard_monthly")
        ]
    ])
    return keyboard

@dp.message(Command("leaderboard"))
async def cmd_leaderboard(message: types.Message):
    await message.answer(
        "Выберите период для просмотра статистики:",
        reply_markup=create_leaderboard_keyboard()
    )

def format_leaderboard(stats_data):
    # Создаем список кортежей (user_id, count)
    leaderboard = list(stats_data.items())
    # Сортируем по убыванию количества
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    
    # Форматируем текст
    text = "🏆 Топ пидоров:\n\n"
    for i, (user_id, count) in enumerate(leaderboard, 1):
        user_name = next((name for uid, name in USERS if uid == user_id), "Неизвестный")
        text += f"{i}. {user_name}: {count} раз(а)\n"
    
    return text if leaderboard else "Статистика пока пуста 🤷‍♂️"

@dp.callback_query(lambda c: c.data.startswith('leaderboard_'))
async def process_leaderboard_callback(callback_query: types.CallbackQuery):
    now = datetime.now(pytz.timezone('Europe/Moscow'))
    period = callback_query.data.split('_')[1]
    
    if period == 'weekly':
        # Получаем начало текущей недели
        week_start = (now - timedelta(days=now.weekday())).date()
        stats = get_stats(week_start.isoformat(), now.date().isoformat())
        text = "📊 Статистика за текущую неделю:\n" + format_leaderboard(stats)
    else:
        # Получаем начало текущего месяца
        month_start = now.replace(day=1).date()
        stats = get_stats(month_start.isoformat(), now.date().isoformat())
        text = "📊 Статистика за текущий месяц:\n" + format_leaderboard(stats)
    
    await callback_query.message.edit_text(
        text,
        reply_markup=create_leaderboard_keyboard(),
        parse_mode="Markdown"
    )
    await callback_query.answer()

async def main():
    # Инициализируем базу данных при запуске
    init_db()
    
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
