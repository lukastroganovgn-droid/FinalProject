import os
import telebot
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()
api_key = os.getenv("TOKEN")

# Создаем единственный экземпляр бота
bot = telebot.TeleBot(api_key)
