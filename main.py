import os
import logging
import asyncio
import sys
import json
from typing import Any

import aiohttp
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import KeyboardBuilder
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
from utils import get_bot, get_openai_endpoint
from models import TelegramUser, SystemPrompt, Chat, DirectionChoices

load_dotenv()
bot: Bot = get_bot()
dispatcher: Dispatcher = Dispatcher()
main_router = Router(name=__name__)
logger = logging.getLogger(__name__)
dispatcher.include_router(main_router)


class SystemPromptCallback(CallbackData, prefix="system_prompt"):
    prompt_id: int


async def fetch_completion(system_prompt: SystemPrompt, input_message: str) -> dict:
    messages = [
        {
            "role": "system",
            "content": system_prompt.prompt
        },
        {
            "role": "user",
            "content": input_message
        }
    ]
    endpoint = get_openai_endpoint()
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': messages,
    }
    data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, data=data) as response:
            return await response.json()


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user, created = TelegramUser.get_or_create(
        telegram_id=message.from_user.id,
        defaults={
            'username': message.from_user.username
        }
    )
    prompts = SystemPrompt.select()
    builder = KeyboardBuilder(button_type=InlineKeyboardButton)
    for prompt in prompts:
        builder.button(text=prompt.name, callback_data=SystemPromptCallback(prompt_id=prompt.id).pack())
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=builder.as_markup())


@main_router.callback_query(SystemPromptCallback.filter())
async def callback_query_handler(callback_query: types.CallbackQuery, callback_data: SystemPromptCallback) -> Any:
    user = TelegramUser.get(
        telegram_id=callback_query.from_user.id,
    )
    prompt = SystemPrompt.get(id=callback_data.prompt_id)
    user.system_prompt = prompt
    user.save()
    await callback_query.message.answer(f'Выбран {prompt.name}. Напишите теперь сообщение.')


@main_router.message()
async def message_handler(message: types.Message) -> None:
    user = TelegramUser.get(
        telegram_id=message.from_user.id,
    )
    if user.system_prompt is None:
        await message.answer('Выберите персонажа.')
    if message.text.strip() == '':
        await message.answer('Странное пустое сообщение.')
    Chat.create(
        telegram_user=user,
        direction='from',
        message_text=message.text
    )
    try:
        answer: dict = await fetch_completion(user.system_prompt, message.text)
        answer_text: str = answer['choices'][0]['message']['content']
    except TypeError:
        await message.answer("Nice try!")
    except IndexError:
        await message.answer("что-то сломалось.")
    except Exception:
        await message.answer('что-то сломалось.')
    Chat.create(
        telegram_user=user,
        direction='to',
        message_text=answer_text
    )
    await message.answer(answer_text)


async def main() -> None:
    await dispatcher.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
