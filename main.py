from telebot import types
from bot import bot
import logic

# Инициализируем базу данных при старте скрипта
logic.init_db()

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
    
    logic.save_user_audience(chat_id, audience)
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_it = types.InlineKeyboardButton("IT и Технологии", callback_data="category_it")
    btn_design = types.InlineKeyboardButton("Дизайн", callback_data="category_design")
    btn_marketing = types.InlineKeyboardButton("Маркетинг", callback_data="category_marketing")
    btn_management = types.InlineKeyboardButton("Менеджмент", callback_data="category_management")
    
    markup.add(btn_it, btn_design, btn_marketing, btn_management)
    
    bot.send_message(chat_id, "Какая сфера тебе ближе?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("category_"))
def handle_category(call):
    chat_id = call.message.chat.id
    category_selected = call.data.split("_")[1]
    
    audience = logic.get_user_audience(chat_id)
    
    if not audience:
        bot.send_message(chat_id, "Пожалуйста, начни сначала, введя команду /start")
        bot.answer_callback_query(call.id)
        return
        
    prof_data = logic.get_profession(audience, category_selected)
    
    if prof_data:
        title, description = prof_data
        response_text = (
            f"**Твоя рекомендация:**\n\n"
            f"**{title}**\n\n"
            f"*Описание:* {description}\n\n"
            f"Желаешь посмотреть другие варианты? Жми /start"
        )
    else:
        response_text = "К сожалению, подходящая профессия не найдена в базе. Попробуй заново: /start"
    
    bot.answer_callback_query(call.id)
    bot.send_message(chat_id, response_text, parse_mode="Markdown")

if __name__ == "__main__":
    print("Бот успешно запущен...")
    bot.infinity_polling()
