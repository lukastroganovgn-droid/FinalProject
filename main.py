import os
from dotenv import load_dotenv
import sqlite3
import telebot
from telebot import types

load_dotenv()

api_key = os.getenv("TOKEN")

bot = telebot.TeleBot(api_key)

DB_NAME = "career_bot.db"

# --- Инициализация Базы Данных ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Таблица профессий (Требование 4)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            audience TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    
    # 2. Таблица состояний пользователей (для адаптации)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_states (
            user_id INTEGER PRIMARY KEY,
            audience TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    
    # Заполняем базу начальными данными, если она пустая
    cursor.execute("SELECT COUNT(*) FROM professions")
    if cursor.fetchone()[0] == 0:
        demo_data = [
            ("Разработчик игр", "it", "teen", "Создает миры и логику видеоигр. Подходит, если ты любишь математику, логику и гейминг."),
            ("2D/3D Художник", "design", "teen", "Рисует персонажей и локации для игр и анимации. Нужен навык рисования."),
            ("Специалист по Кибербезопасности", "it", "adult", "Защищает данные компаний от хакеров. Огромный спрос на рынке, высокая оплата."),
            ("UX/UI Дизайнер", "design", "adult", "Проектирует удобные интерфейсы сайтов и приложений. Ценится прошлый жизненный опыт.")
        ]
        cursor.executemany(
            "INSERT INTO professions (title, category, audience, description) VALUES (?, ?, ?, ?)", 
            demo_data
        )
        conn.commit()
        print("База данных успешно инициализирована и заполнена демо-данными!")
        
    conn.close()

# --- Вспомогательные функции для работы с БД ---
def save_user_audience(user_id, audience):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # INSERT OR REPLACE обновляет запись, если пользователь проходит тест заново
    cursor.execute(
        "INSERT OR REPLACE INTO user_states (user_id, audience) VALUES (?, ?)", 
        (user_id, audience)
    )
    conn.commit()
    conn.close()

def get_user_audience(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT audience FROM user_states WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_profession(audience, category):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, description FROM professions WHERE audience = ? AND category = ? LIMIT 1", 
        (audience, category)
    )
    result = cursor.fetchone()
    conn.close()
    return result # Возвращает кортеж (title, description) или None

# --- Обработчики Telegram ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_teen = types.KeyboardButton("Я подросток / студент")
    btn_adult = types.KeyboardButton("Хочу сменить профессию")
    markup.add(btn_teen, btn_adult)
    
    welcome_text = (
        "Привет! Я твой карьерный консультант.\n\n"
        "Помогу определиться с направлением и найти интересные пути развития. "
        "Для начала ответь: **кто ты?**"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Я подросток / студент", "Хочу сменить профессию"])
def handle_audience(message):
    chat_id = message.chat.id
    audience = "teen" if "подросток" in message.text else "adult"
    
    # Сохраняем выбор в БД SQLite
    save_user_audience(chat_id, audience)
    
    markup = types.InlineKeyboardMarkup()
    btn_it = types.InlineKeyboardButton("Технологии и IT", callback_data="category_it")
    btn_design = types.InlineKeyboardButton("Творчество и Дизайн", callback_data="category_design")
    markup.add(btn_it, btn_design)
    
    bot.send_message(chat_id, "Какая сфера тебе ближе?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def handle_category(call):
    chat_id = call.message.chat.id
    category_selected = call.data.split("_")[1] # 'it' или 'design'
    
    # Получаем целевую аудиторию пользователя из БД SQLite
    audience = get_user_audience(chat_id)
    
    if not audience:
        bot.send_message(chat_id, "Пожалуйста, начни сначала, введя команду /start")
        bot.answer_callback_query(call.id)
        return
        
    # Делаем SQL-запрос для поиска нужной профессии
    prof_data = get_profession(audience, category_selected)
    
    if prof_data:
        title, description = prof_data
        response_text = (
            f"**Твоя рекомендация:**\n\n"
            f"**{title}**\n\n"
            f"*Описание:* {description}\n\n"
            f"Желаешь посмотреть другие варианты? Жми /start"
        )
    else:
        response_text = "К сожалению, подходящая профессия не найдена в базе данных. Попробуй заново: /start"
    
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, response_text, parse_mode="Markdown")

if __name__ == "__main__":
    # Инициализируем БД перед запуском бота
    init_db()
    print("Бот успешно запущен")
    bot.infinity_polling()
