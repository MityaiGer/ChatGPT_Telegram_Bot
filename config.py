from aiogram.types import LabeledPrice
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем значения из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Проверка наличия необходимых переменных окружения
if not BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Пожалуйста, установите BOT_TOKEN и OPENAI_API_KEY в файле .env")

CHANNELS = [
    ["NAME_CHANNEL", "-1000000000000", "https://t.me/name_channel"],
]

NOT_SUB_MESSAGE = "Для доступа к боту, необходимо подписаться на канал"

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)
