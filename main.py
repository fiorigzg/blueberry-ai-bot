from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from messages import my_messages_handler, send_generations
import asyncio

from constants import API_TOKEN

# logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

my_messages_handler(dp, bot)

async def on_startup(dp):
	asyncio.create_task(send_generations(bot))

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup)