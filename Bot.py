import random
from config import TOKEN
from config import DB_FILE
import logging
from aiogram import Bot, Dispatcher, executor, types
from db_conn import DBConnection
from user_repository import UserRepository
from user import User
from group import Group
from grouprepository import GroupRepository
import uuid

from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
# уровень логов
logging.basicConfig( level=logging.INFO )

bot = Bot( token=TOKEN )
dp = Dispatcher( bot )

dbconn = DBConnection( DB_FILE )
userRepo = UserRepository( dbconn )
groupRepo = GroupRepository( dbconn )


def generateTeacherGuardCode():
    return random.randrange(1000, 9999, 1)








imUser_kb = types.InlineKeyboardButton(text="Я ученик", callback_data="step1.1:student")
imTeacher_kb = types.InlineKeyboardButton(text="Я учитель", callback_data="step1.1:teacher")
keyboard_Ident = types.InlineKeyboardMarkup().add(imUser_kb).add(imTeacher_kb)


# /start
@dp.message_handler(commands=['start'])
# @dp.message_handler(commands=['start', 'help'])
async def procces_start_command(message: types.Message):
    user = userRepo.find_user ( message.chat.id )
    if user is None:
        await message.reply("Привет! Укажи, кто ты.", reply_markup=keyboard_Ident)
    else:
        await message.reply("Привет! А я тебя знаю " + user.name)

@dp.callback_query_handler()
async def inline_kb_ident_answer(query: types.CallbackQuery):
    answer_data = query.data
    chat_id = query.message.chat.id
    user = userRepo.find_user(chat_id)
    if answer_data == "step1.1:student":
        await process_student_step11( chat_id, query, user )

    if answer_data =="step1.1:teacher":
        user = await process_teacher_step11( chat_id, query, user )

    if answer_data.startswith("step2.group:"):
        await process_user_step2( answer_data, chat_id, query, user )


async def process_user_step2(answer_data, chat_id, query, user):
    if user is None:
        groupId = answer_data[len( "step2.group:" ):]
        user = User( chat_id )
        user.name = query.message.from_user.full_name
        #В БД создаем запись об ученике
        userRepo.create_student( user, groupId )
        print( "student created" )
        await bot.send_message( chat_id, text="Ок, вы зарегистрированы" )
    else:
        await bot.send_message( chat_id, text="Вы уже определены" )


async def process_teacher_step11(chat_id, query, user):
    code = str( generateTeacherGuardCode() )
    user = User( chat_id )
    #получаем юзернейм пользователя
    user.name = query.from_user.full_name
    #В БД создаем запись об учителе
    userRepo.create_teacher( user, False, code )
    await bot.send_message( chat_id, text="Обратитесь к администратору, чтобы он подтвердил, что вы - учитель, ваш код :" + code )
    return user


async def process_student_step11(chat_id, query, user):
    keyboard_choose_group = types.InlineKeyboardMarkup()
    groups = groupRepo.list_group()
    for g in groups:
        group1_button = types.InlineKeyboardButton( text=g.name, callback_data="step2.group:" + g.id )
        keyboard_choose_group.add( group1_button )
    await bot.send_message( chat_id, text="Укажите группу, к которой Вы относитесь",
                            reply_markup=keyboard_choose_group )


@dp.callback_query_handler()
async def inline_kb_choose_group_answer(query: types.CallbackQuery):
    answer_data = query.data





# Запуск лонг поллинга

if __name__ == '__main__':
    executor.start_polling( dp, skip_updates=True )
