import openai
import time
import os
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ChatActions
from config import bot, dp, OPENAI_API_KEY
from openai.error import InvalidRequestError
import asyncio

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Глобальные переменные
messages = {}
request_limit = 15
request_count = {}

# Системный промпт для бота
SYSTEM_PROMPT = {
    "role": "system",
    "content": "Ты чат-бот способный активно участвовать в дискуссиях и генерировать соответствующие ответы на запросы, как человек. При приветствии и в диалоге, ты должен упоминать пользователя по имени, не используя юзернейм."
}

async def check_and_update_requests(user_id, username):
    """Проверяет и обновляет количество оставшихся запросов"""
    if username not in request_count:
        request_count[username] = 0
    
    remaining_requests = request_limit - request_count[username]
    
    if remaining_requests <= 0:
        await bot.send_message(user_id, "Вы достигли лимита запросов. Счетчик сбросится через 24 часа.")
        # Запускаем сброс счетчика в фоновом режиме
        asyncio.create_task(reset_counter_after_delay(user_id, username))
        return False
    
    if remaining_requests % 5 == 0:
        await bot.send_message(user_id, f"Осталось {remaining_requests} запросов.")
    
    return True

async def reset_counter_after_delay(user_id, username):
    """Сбрасывает счетчик запросов после задержки"""
    await asyncio.sleep(24 * 3600)  # 24 часа
    request_count[username] = 0
    await bot.send_message(user_id, "Счетчик запросов сброшен. Вы можете отправлять запросы снова.")

def initialize_user_context(user_id):
    """Инициализирует контекст для нового пользователя"""
    messages[user_id] = [SYSTEM_PROMPT]

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    initialize_user_context(user_id)
    
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await bot.send_message(
        user_id,
        text=f"Привет, <b>{message.from_user.first_name}</b>!\n\n"
             f"Чат бот—<b>ПОМОЩНИК</b> рад приветствовать Вас! "
             f"Я разработан на основе мощной языковой модели и готов помочь вам.\n\n"
             f"<b>Задайте любой вопрос!</b>",
        parse_mode="html"
    )

@dp.message_handler()
async def send(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or str(user_id)  # Используем ID если нет username
    user_message = message.text

    # Инициализация контекста для нового пользователя
    if user_id not in messages:
        initialize_user_context(user_id)

    if not await check_and_update_requests(user_id, username):
        return

    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)

    try:
        # Добавляем сообщение пользователя в контекст
        messages[user_id].append({
            "role": "user",
            "content": f"{message.from_user.first_name}: {user_message}"
        })

        # Ограничиваем контекст последними 10 сообщениями + системный промпт
        if len(messages[user_id]) > 11:
            messages[user_id] = [messages[user_id][0]] + messages[user_id][-10:]

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages[user_id],
            temperature=0.7,  # Немного уменьшаем случайность для более стабильных ответов
            max_tokens=2000,  # Ограничиваем длину ответа
            user=username
        )

        response_text = response['choices'][0]['message']['content']
        
        # Сохраняем ответ бота в контекст
        messages[user_id].append({
            "role": "assistant",
            "content": response_text
        })
        
        request_count[username] = request_count.get(username, 0) + 1
        await message.answer(response_text)

    except Exception as e:
        logging.error(f"Error processing message from {username}: {str(e)}")
        error_message = "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже."
        await message.answer(error_message)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    executor.start_polling(dp, skip_updates=True)
