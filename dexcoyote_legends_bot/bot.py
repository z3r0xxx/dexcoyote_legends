import os
import sys
import json 
import asyncio
import logging
import database
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, html, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandObject, CommandStart
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.deep_linking import create_start_link
from aiogram.types import (
    InlineKeyboardButton, 
    Message, 
    WebAppInfo, 
    FSInputFile
)

load_dotenv()
dp = Dispatcher()

def load_translations(lang):
    with open(f'locale/{lang}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def _(translations, text):
    return translations.get(text, text)

def get_keyboard():    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="⏰ Early registration…", callback_data="early_registration")
    )
    
    return keyboard.as_markup()

def get_refferal_link_keyboard():    
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="👥 To invite a friend", callback_data="invite_friend")
    )
    
    return keyboard.as_markup()

@dp.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandObject):
    if message.from_user.id != message.chat.id: 
        return
    
    args = command.args
    
    if args.isdigit():
        invited_by = int(args)
        if message.from_user.id != invited_by:
            chat = await message.bot.get_chat(chat_id=message.from_user.id)
            username = chat.username
        
        if database.check_user_exists(message.from_user.id) is False:            
            if message.from_user.is_premium:
                database.insert_user(user_id=message.from_user.id, invited_by=int(args), is_premium=1)
                await message.bot.send_message(invited_by, f"🎉 New friend: @{username}")
            else:
                database.insert_user(user_id=message.from_user.id, invited_by=int(args), is_premium=0)
                await message.bot.send_message(invited_by, f"🎉 New friend: @{username}")
    
    translations = load_translations('en')
    image = FSInputFile("images/banner.jpg")
    await message.bot.send_photo(chat_id=message.chat.id, photo=image, caption=_(translations, "welcome_text"), reply_markup=get_keyboard())

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    if database.check_user_exists(message.from_user.id) is False:
        if message.from_user.is_premium:
            database.insert_user(user_id=message.from_user.id, is_premium=1)
        else:
            database.insert_user(user_id=message.from_user.id, is_premium=0)
            
    translations = load_translations('en')
    image = FSInputFile("images/banner.jpg")
    await message.bot.send_photo(chat_id=message.chat.id, photo=image, caption=_(translations, "welcome_text"), reply_markup=get_keyboard())

@dp.callback_query(F.data.startswith("early_registration"))
async def callback_query_handler_lang(callback_query: types.CallbackQuery):   
    await callback_query.answer()
    await callback_query.message.answer("✅ You have successfully registered as an early member! @dexcoyote", reply_markup=get_refferal_link_keyboard())

@dp.callback_query(F.data.startswith("invite_friend"))
async def callback_query_handler_lang(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer(f"↗️ https://t.me/dcl1bot?start={callback_query.from_user.id}")

async def main() -> None:
    bot = Bot(token=os.getenv("TG_BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    