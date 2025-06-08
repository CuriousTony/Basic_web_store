from os import getenv
from dotenv import load_dotenv
import telebot

load_dotenv()

TOKEN = getenv('BOT_TOKEN')
ADMIN_CHAT_ID = getenv('ADMIN_CHAT_ID')
bot = telebot.TeleBot(TOKEN)
