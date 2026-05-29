import os
from dotenv import load_dotenv
import telebot
from telebot import types
import random

load_dotenv()

api_key = os.getenv("TOKEN")

# Замените на токен вашего бота от @BotFather
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

# Имитация Базы Данных (Требование 4)
# В будущем эти данные стартап сможет легко перенести в SQLite/PostgreSQL
PROFESSIONS_DB = {
    "teen": {
        "it": {"title": "Разработчик игр", "desc": "Создает миры и логику видеоигр. Подходит, если ты любишь математику, логику и гейминг."},
        "design": {"title": "2D/3D Художник", "desc": "Рисует персонажей и локации для игр и анимации. Нужен навык рисования и графический планшет."}
    },
    "adult": {
        "it": {"title": "Специалист по Кибербезопасности", "desc": "Защищает данные компаний от хакеров. Огромный спрос на рынке, высокая оплата."},
        "design": {"title": "UX/UI Дизайнер", "desc": "Проектирует удобные интерфейсы сайтов и приложений. Ценится прошлый жизненный опыт."}
    }
}

# Временное хранилище ответов пользователей в памяти (для адаптивности)
user_states = {}

# --- Команда /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Создаем главное меню (обычные кнопки под полем ввода)
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

# --- Обработка выбора аудитории (Требование 1) ---
@bot.message_handler(func=lambda message: message.text in ["Я подросток / студент", "Хочу сменить профессию"])
def handle_audience(message):
    chat_id = message.chat.id
    # Сохраняем тип пользователя
    user_states[chat_id] = {
        "audience": "teen" if "подросток" in message.text else "adult"
    }
    
    # Создаем Инлайн-кнопки для выбора сферы (Требование 2)
    markup = types.InlineKeyboardMarkup()
    btn_it = types.InlineKeyboardButton("Технологии и IT", callback_data="category_it")
    btn_design = types.InlineKeyboardButton("Творчество и Дизайн", callback_data="category_design")
    markup.add(btn_it, btn_design)
    
    bot.send_message(chat_id, "Какая сфера тебе ближе?", reply_markup=markup)

# --- Обработка нажатий на инлайн-кнопки (Требование 2 и 3) ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def handle_category(call):
    chat_id = call.message.chat.id
    category_selected = call.data.split("_")[1] # 'it' или 'design'
    
    # Проверяем, есть ли сохраненный профиль пользователя
    if chat_id not in user_states:
        bot.send_message(chat_id, "Пожалуйста, начни сначала, введя команду /start")
        return
        
    audience = user_states[chat_id]["audience"]
    
    # Достаем подходящую профессию из нашей "БД" (Персонализация)
    prof_data = PROFESSIONS_DB[audience][category_selected]
    
    # Легковоспринимаемый формат вывода (Требование 3)
    response_text = (
        f"**Твоя рекомендация:**\n\n"
        f"**{prof_data['title']}**\n\n"
        f"*Описание:* {prof_data['desc']}\n\n"
        f"Желаешь посмотреть другие варианты? Жми /start"
    )
    
    # Убираем часы загрузки на инлайн-кнопке и отправляем ответ
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, response_text, parse_mode="Markdown")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()



