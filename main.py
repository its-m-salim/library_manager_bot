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

async def main():
    print("Bot started")
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    