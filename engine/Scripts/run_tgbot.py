import asyncio

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest

from .tg_bot.inctance import bot, dp
from .tg_bot.handlers import router


async def main():
    dp.include_router(router)
    try:
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        print("остановлено пользователем")
    except Exception as e:
        print(f"Ошибка в main: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
