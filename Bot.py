import logging
import uuid

from aiogram import Bot, Dispatcher, executor, types

from config import ADMIN_ID
from config import DB_FILE
from config import TOKEN
from db_conn import DBConnection
from group import Group
from grouprepository import GroupRepository
from homeworkbot import HomeworkBot
from user_repository import UserRepository

# уровень логов
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

dbconn = DBConnection(DB_FILE)
dbconn.initdb()
userRepo = UserRepository(dbconn)
groupRepo = GroupRepository(dbconn)

groups = groupRepo.list_group()
if groups is None or len(groups) == 0:
    for i in range(1, 12, 1):
        groupRepo.create_group(Group(str(uuid.uuid4()), str(i) + " класс"))

dbconn.close()


# /start
@dp.message_handler(commands=['start'])
# @dp.message_handler(commands=['start', 'help'])
async def procces_start_command(message: types.Message):
    homeworkbot = HomeworkBot(bot, DB_FILE, ADMIN_ID)
    await homeworkbot.handle_start_command(message)
    homeworkbot.close()


@dp.callback_query_handler()
async def process_callback_query(query: types.CallbackQuery):
    homeworkbot = HomeworkBot(bot, DB_FILE, ADMIN_ID)
    await homeworkbot.handle_callback(query)
    homeworkbot.close()


@dp.message_handler()
async def process_text_message(message: types.Message):
    homeworkbot = HomeworkBot(bot, DB_FILE, ADMIN_ID)
    await homeworkbot.handle_text(message)
    homeworkbot.close()


# Запуск лонг поллинга

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
