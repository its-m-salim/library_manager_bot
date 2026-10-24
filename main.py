from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv
import asyncio
import os
from service import *
from connection import*

load_dotenv()


token = os.getenv("BOT_TOKEN")
bot = Bot(token=token)
dp = Dispatcher()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Доступные книги"), KeyboardButton(text="📖 Мои книги")],
],
        resize_keyboard=True
)


@dp.message(CommandStart())
async def start_bot(message: Message):
    user = message.from_user
    if not await profile(user.id):
        await message.answer(f"""
Привет, {user.full_name}
""", reply_markup=main_keyboard)    
        await create_user(user.username, user.full_name, user.id)
    else:
        await message.answer(f"""
С возвращением, {user.full_name}!
""", reply_markup=main_keyboard)
    



@dp.message(Command("add_book"))
async def add_book(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("""
Для добавления книги введите имя и имя автора!
""")
        return

    data = command.args.split("/")

    if not 1< len(data) < 3:
        await message.answer("""
Неверный формат ввода! 
Используйте /help чтобы увидеть примеры
""")
        return

    if await add_books(data[0], data[1]):
        await message.answer(f"""
Книга {data[0]} от автора {data[1]}
успешно добавлено в список книг!
Посмотреть можно в /books если оно доступно
""")
    else:
        message.answer("""
Книга не добавлено!
Проверьте правильность ввода
""")



@dp.message(F.text == "📚 Доступные книги")
@dp.message(Command("books"))
async def books(message: Message):
    bookss = await active_books()
    if not bookss:
        await message.answer("""
Каталог книг пока пуста
Попробуйте добавить свою книгу с помощью /add_book
""")
        return
    text = "Вот все доступные книги:\n"

    for book in bookss:
        text +=f"""
ID: {book["id"]}
Имя: {book["title"]}
Автор: {book["author"]}
Добавлено в: {book["added_at"]}
"""
    await message.answer(text)



@dp.message(Command("borrow"))
async def bb(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("""
укажите id книги!
""")
        return

    data = command.args.split("/")
    if  len(data) > 1:
        await message.answer("""
    Неверный формат ввода! 
    Используйте /help чтобы увидеть примеры
    """)
        return

    if not data[0].isdigit():
        await message.answer("""
id не может быт словом!
""")
        return
    status = await is_active(data[0])
    if not status:
        await message.answer("книга не существует!")
        return
    else:
        if not status["is_available"]:
            await message.answer("книга занят!")
            return
    if await borrow_book(data[0], message.from_user.id):
        await message.answer("""
книга успешно бран!
""")
    else:
        await message.answer("""
книга либо нет либо занят
""")


@dp.message(F.text == "📖 Мои книги")
@dp.message(Command("my_books"))
async def get_books(message: Message):
    all_books = await my_books(message.from_user.id)

    if not all_books:
        await message.answer("you have not books")
        return

    text = "Вот ваши книги:\n"

    for b in all_books:
        text += f"""
title: {b["title"]}
author: {b["author"]}
borrowed at: {b["bat"]}
"""
    await message.answer(text)
    



@dp.message(Command("return"))
async def rb(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("""
укажите id книги!
""")
        return

    data = command.args.split("/")
    if  len(data) > 1:
        await message.answer("""
    Неверный формат ввода! 
    Используйте /help чтобы увидеть примеры
    """)
        return

    if not data[0].isdigit():
        await message.answer("""
id не может быт словом!
""")
        return
    status = await is_active(data[0])
    if not status:
        await message.answer("книга не существует!")
        return
    else:
        if status["is_available"]:
            await message.answer("Вы не брали эту книгу!")
            return
    if await return_book(data[0], message.from_user.id):
        await message.answer("""
книга успешно выдан!
""")
    else:
        await message.answer("""
не успешная ошибка при выдачи
""")





async def main():
    print("Bot started")
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    