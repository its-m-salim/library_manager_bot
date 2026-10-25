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
👋 Добро пожаловать, {user.full_name}!\n\n📚 Здесь ты можешь просматривать каталог книг, брать книги и следить за своими выдачами.
""", reply_markup=main_keyboard)    
        await create_user(user.username, user.full_name, user.id)
    else:
        await message.answer(f"""
✨ С возвращением, {user.full_name}!\n\nРады видеть тебя снова в библиотеке 📚
""", reply_markup=main_keyboard)
    



@dp.message(Command("add_book"))
async def add_book(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("""
📚 Чтобы добавить книгу, укажи её название и автора.
Формат: /add_book Название книги/Имя автора
""")
        return

    data = command.args.split("/")

    if not 1< len(data) < 3:
        await message.answer("""
⚠️ Неверный формат команды. 
Используйте /help чтобы увидеть примеры
""")
        return

    if await add_books(data[0], data[1]):
        await message.answer(f"""
✅ Книга «{data[0]}» — автор {data[1]} — успешно добавлена в библиотеку!
📚 Открой /books, чтобы посмотреть каталог доступных книг.
""")
    else:
        message.answer("""
Книга не добавлено!
Проверьте правильность ввода
""")



@dp.message(F.text == "📚 Доступные книги")
@dp.message(Command("books"))
async def books(message: Message):


    unvailable_b, all_books = await active_books()
    if unvailable_b["count"] > 0 and not all_books:
        await message.answer("""
Все существуюшие книги находится в руках у других ползователей 
пока ждете можете добавить свою книгу в /add_book!
""")
        return
    if not all_books:
        await message.answer("""
Каталог книг пока пуста
Попробуйте добавить свою книгу с помощью /add_book
""")
        return
    text = """
📚 Доступные книги:

"""
    best = await bestsellers()

    for book in all_books:
        date_frm = format_date(book["added_at"])
        bestseller = "🏆 БЕСТСЕЛЛЕР\n" if best is not None and best["id"] == book["id"]  else ""
        text += f"""{bestseller}🆔 ID: {book["id"]}
📖 Название: {book["title"]}
✍️ Автор: {book["author"]}
🕒 Добавлена: {date_frm}

"""

    if unvailable_b["count"] > 0:
        text += f"\nВсего {unvailable_b["count"]} книг находится у руках ползователей"
    await message.answer(text)



@dp.message(Command("borrow"))
async def bb(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("""
📌 Укажи ID книги, которую хочешь взять.
Пример: /borrow 12
""")
        return

    data = command.args.split("/")
    if  len(data) > 1:
        await message.answer("""
⚠️ Неверный формат команды. 
Пример: /borrow 12
    """)
        return

    if not data[0].isdigit():
        await message.answer("""
⚠️ ID книги должен быть числом.
""")
        return
    status = await is_active(data[0])
    if not status:
        await message.answer("🔎 Книга с таким ID не найдена.")
        return
    br = await get_borrowed(data[0], message.from_user.id)
    if br == "other_user":
        await message.answer("""
книга находится в руке другого пользователя!
дождитнсь пока книга станет доступной!
""")
        return
    if br == "ok":
        await message.answer("""
📖 Эта книга уже у тебя. Посмотреть свои книги можно командой /my_borrows.
""")
        return
    if await borrow_book(data[0], message.from_user.id):
        await message.answer("""
✅ Книга успешно выдана тебе!\n\nПосмотреть свои книги можно командой /my_borrows.
""")
    else:
        await message.answer("""
❌ Не удалось выдать книгу. Возможно, её уже взял другой читатель.
""")


@dp.message(F.text == "📖 Мои книги")
@dp.message(Command("my_borrows"))
async def get_books(message: Message):
    all_books = await my_books(message.from_user.id)

    if not all_books:
        await message.answer("📚 У тебя пока нет выданных книг.")
        return

    text = "Вот ваши книги:\n"
    
    for b in all_books:
        date_frm = format_date(b["bat"])
        text += f"""
🆔 ID: {b["id"]}
📚 Название: {b["title"]}
✍️ Автор: {b["author"]}
🕒 Получена: {date_frm}
"""
    await message.answer(text)
    



@dp.message(Command("return_book"))
async def rb(message: Message, command:CommandObject):
    if not command.args:
        await message.answer("""
📌 Укажи ID книги, которую хочешь вернуть.
Пример: /return_book 12
""")
        return

    data = command.args.split("/")
    if  len(data) > 1:
        await message.answer("""
⚠️ Неверный формат команды. 
Пример: /return_book 12
    """)
        return

    if not data[0].isdigit():
        await message.answer("""
⚠️ ID книги должен быть числом.
""")
        return
    status = await is_active(data[0])
    if not status:
        await message.answer("🔎 Книга с таким ID не найдена.")
        return
    br = await get_borrowed(data[0], message.from_user.id)
    if br == "free":
        await message.answer("📚 Эта книга уже доступна в каталоге /books — возвращать её не нужно.")
        return
    elif br == "other_user":
        await message.answer("📕 Эту книгу сейчас читает другой пользователь. Ты не можешь вернуть её за него.")
        return
    elif br == "ok":
        if await return_book(data[0], message.from_user.id):
            user = await profile(message.from_user.id)
            if user["total_books"] == 1:
                await message.answer("""
🎉 Поздравляем с первой прочитанной книгой!

📖 Это только начало твоего читательского пути.

✨ Продолжай читать и пополнять свою коллекцию знаний!
""")
                return
            await message.answer("""
✅ Книга успешно возвращена!
Спасибо, что вернул её в библиотеку 📚
""")
    else:
        await message.answer("""
❌ Не удалось вернуть книгу. Проверь ID и попробуй ещё раз.
""")





async def main():
    print("Bot started")
    await create_tables()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
    