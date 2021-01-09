import random
from config import TOKEN
from config import DB_FILE
from config import  ADMIN_ID
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
    if message.from_user.id == ADMIN_ID:
        button_confrim_teacher = InlineKeyboardButton(text="Подтвердить учителя",callback_data="admin:confirm")

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

@dp.callback_query_handler()
async def process_teacher_confirm_by_admin(query: types.CallbackQuery):
    answer_data = query.data
    if answer_data == "admin:confirm":
        await bot.send_message(text="Введите код учителя")


@dp.message_handler()
async def process_get_teacher_id_from_admin(message: types.Message):
    user_id = query.message.from_user.id
    if user_id == ADMIN_ID:
        code = message.text
        teacher = userRepo.confirm_teacher(code)
        if teacher is None:
            await bot.send_message(message.chat.id, text="Такой код не найден!" )
        else:
            await bot.send_message( message.chat.id, text="Учитель " + teacher.id + " подтвержден")
            await bot.send_message( teacher.id, text="Вас подтвердили")
            #вставить прцедуру для отображения учителю его меню




async def process_user_step2(answer_data, chat_id, query, user):
    if user is None:
        groupId = answer_data[len( "step2.group:" ):]
        user = User( chat_id )
        user.name = query.message.from_user.full_name
        #В БД создаем запись об ученике
        userRepo.create_student( user, groupId )
        print( "student created" )
        await bot.send_message( chat_id, text="Ок, вы зарегистрированы",  )
        """
        #homework = user.group.homeworks
        homework_for_user = types.InlineKeyboardMarkup
        for i in homework:
            if homework.deadline<time:
                homework_1 = types.InlineKeyboardButton(text=homework.name, callback_data="step3:groups:"+homework.id)
                homework_for_user.add(homework_1)
        await bot.send_message(chat_id, text="выберите предмет для дальнейших действий", reply_markup=homework_for_user)
        """
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
async def inline_kb_teacher_add_group(query: types.CallbackQuery):
    answer_data = query.data
    teacher = userRepo.get_teacher()
    chat_id = query.message.chat.id
    if answer_data == "teacher:add_group":
        await bot.send_message(text="Выберите группу, учителем которой Вы являетесь", reply_markup=make_kb_teacher_add_group(chat_id, teacher))

@dp.callback_query_handler()
async def process_add_teacher_group(query: types.CallbackQuery):
    answer_data = query.data
    teacher = userRepo.get_teacher()
    group_id = answer_data[len("teacher:add_group"):]
    userRepo.add_teacher_group(teacher.id, group_id)
    await bot.send_message(query.message.chat.id,text="Вы успешно стали учителем еще одной группы")





@dp.callback_query_handler()
async def inline_kb_choose_group_answer(query: types.CallbackQuery):
    answer_data = query.data
    chat_id = query.message.chat.id
    user = userRepo.find_user( chat_id )
    group_id = user.id

async def process_kb_teacher_main_menu(chat_id,teacher):
    main_teacher_kb = InlineKeyboardMarkup()
    add_homework_bttn = InlineKeyboardButton(text="Добавить задание",callback_data="teacher:add_homework")
    add_group_bttn = InlineKeyboardButton(text="Добавить группу",callback_data="teacher:add_group")
    del_group_bttn = InlineKeyboardButton(text="Удалить группу",callback_data="teacher:del_group")

async def make_kb_teacher_add_group(chat_id,teacher,):
    groups = groupRepo.list_group()
    add_groups_kb = InlineKeyboardMarkup()
    for g in groups:
        found = False
        for k in teacher.groups:
            if g == k:
                found = True
        button = InlineKeyboardButton(text=g.name,callback_data="teacher:add_group"+g.id)
        add_groups_kb.add(button)
        return add_groups_kb


async def process_kb_teacher_menu(chat_id,teacher):
    teacher_main_kb = InlineKeyboardMarkup()
    for i in teacher.groups:
        teahcergroups_button = InlineKeyboardButton(text=i.name)






# Запуск лонг поллинга

if __name__ == '__main__':
    executor.start_polling( dp, skip_updates=True )
