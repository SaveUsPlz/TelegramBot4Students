import random
from config import TOKEN
from config import DB_FILE
from config import ADMIN_ID
import logging
from aiogram import Bot, Dispatcher, executor, types
from db_conn import DBConnection
from homeworkbot import HomeworkBot
from user_repository import UserRepository
from user import User
from group import Group
from grouprepository import GroupRepository
import uuid

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton

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
    groupRepo.create_group(Group(str(uuid.uuid4()), "1A класс"))
    groupRepo.create_group(Group(str(uuid.uuid4()), "2A класс"))

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


async def inline_kb_teacher_add_group(query: types.CallbackQuery):
    answer_data = query.data
    teacher = userRepo.get_teacher()
    chat_id = query.message.chat.id
    if answer_data == "teacher:add_group":
        await bot.send_message(text="Выберите группу, учителем которой Вы являетесь",
                               reply_markup=make_kb_teacher_add_group(chat_id, teacher))


async def process_add_teacher_group(query: types.CallbackQuery):
    answer_data = query.data
    teacher = userRepo.get_teacher()
    group_id = answer_data[len("teacher:add_group"):]
    userRepo.add_teacher_group(teacher.id, group_id)
    await bot.send_message(query.message.chat.id, text="Вы успешно стали учителем еще одной группы")


async def inline_kb_choose_group_answer(query: types.CallbackQuery):
    answer_data = query.data
    chat_id = query.message.chat.id
    user = userRepo.find_user(chat_id)
    group_id = user.id


async def process_kb_teacher_main_menu(chat_id, teacher):
    main_teacher_kb = InlineKeyboardMarkup()
    add_homework_bttn = InlineKeyboardButton(text="Добавить задание", callback_data="teacher:add_homework")
    add_group_bttn = InlineKeyboardButton(text="Добавить группу", callback_data="teacher:add_group")
    del_group_bttn = InlineKeyboardButton(text="Удалить группу", callback_data="teacher:del_group")


async def make_kb_teacher_add_group(chat_id, teacher, ):
    groups = groupRepo.list_group()
    add_groups_kb = InlineKeyboardMarkup()
    for g in groups:
        found = False
        for k in teacher.groups:
            if g == k:
                found = True
        button = InlineKeyboardButton(text=g.name, callback_data="teacher:add_group" + g.id)
        add_groups_kb.add(button)
        return add_groups_kb


async def process_kb_teacher_menu(chat_id, teacher):
    teacher_main_kb = InlineKeyboardMarkup()
    for i in teacher.groups:
        teahcergroups_button = InlineKeyboardButton(text=i.name)


# Запуск лонг поллинга

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
