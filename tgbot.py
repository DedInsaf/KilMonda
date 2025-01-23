from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from sqlalchemy.orm import Session
from database import get_db
from models import User

bot = Bot(token="")
dp = Dispatcher()

# Хранилище сессии создаётся вручную
def get_session() -> Session:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.reply("Введите ваш ключ для входа в аккаунт:")

@dp.message()
async def handle_key(message: Message):
    # Создаём новую сессию
    db = next(get_db())
    try:
        key = message.text.strip()
        user = db.query(User).filter(User.key == key).first()

        if user:
            await message.reply(f"Добро пожаловать, {user.username}!")
        else:
            await message.reply("Неверный ключ. Попробуйте ещё раз.")
    finally:
        db.close()

if __name__ == "__main__":
    dp.run_polling(bot)