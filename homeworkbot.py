from datetime import datetime, timedelta
import random
import uuid
from datetime import date

from db_conn import DBConnection
from grouprepository import GroupRepository
from stage import Stage
from stagerepository import StageRepository
from task import Task
from taskrepository import TaskRepository
from user import User
from user_repository import UserRepository
from aiogram import Bot, types


class HomeworkBot:

    def __init__(self, bot: Bot, dbfile: str, admin_id: str) -> None:
        self.dbconn = DBConnection(dbfile)
        self.bot = bot
        self.admin_id = admin_id
        self.userRepo = UserRepository(self.dbconn)
        self.groupRepo = GroupRepository(self.dbconn)
        self.stageRepo = StageRepository(self.dbconn)
        self.taskRepo = TaskRepository(self.dbconn)

    async def handle_text(self, message: types.Message):
        user_id = message.from_user.id
        print("Message from " + str(user_id))
        if user_id == self.admin_id:
            code = message.text
            teacher = self.userRepo.confirm_teacher(code)
            if teacher is None:
                await self.bot.send_message(message.chat.id, text="Такой код не найден!")
            else:
                await self.bot.send_message(message.chat.id, text="Учитель " + teacher.id + " подтвержден")
                await self.bot.send_message(teacher.id, text="Вас подтвердили")
                # вставить прцедуру для отображения учителю его меню
                await self.show_main_user_menu(teacher.id, self.userRepo.find_user(teacher.id))
            return

        user = self.userRepo.find_user(message.chat.id)
        if user is not None:
            stage = self.stageRepo.get_stage(user.id)
            if stage is not None:
                await self.process_stage(message.text, user, stage)
                return
            await self.show_main_user_menu(message.chat.id, user)
        else:
            await self.handle_start_command(message)

    async def handle_start_command(self, message: types.Message):
        user = self.userRepo.find_user(message.chat.id)
        if user is None:
            imUser_kb = types.InlineKeyboardButton(text="Я ученик", callback_data="step1.1:student")
            imTeacher_kb = types.InlineKeyboardButton(text="Я учитель", callback_data="step1.1:teacher")
            keyboard_Ident = types.InlineKeyboardMarkup().add(imUser_kb).add(imTeacher_kb)
            #            await message.edit_reply_markup(message)
            await message.reply("Привет! Укажи, кто ты.", reply_markup=keyboard_Ident)
        else:
            self.stageRepo.delete_stage(user.id)
            await message.reply("Привет, " + user.name + " !")
            await self.show_main_user_menu(message.chat.id, user)

    async def show_main_user_menu(self, chat_id: str, user: User):
        if user is None:
            return

        if user.type == "STUDENT":
            student_menu = types.InlineKeyboardMarkup()\
                .add(types.InlineKeyboardButton(text="Просмотр заданий", callback_data="student_show_tasks"))
            await self.bot.send_message(chat_id=chat_id, text="Выберите действие", reply_markup=student_menu)

        if user.type == "TEACHER":
            teacher = self.userRepo.get_teacher(user.id)
            if teacher.confirmed:
                teacher_menu = types.InlineKeyboardMarkup() \
                    .add(types.InlineKeyboardButton(text="Список моих классов", callback_data="teacher_show_groups"))\
                    .add(types.InlineKeyboardButton(text="Добавить класс", callback_data="teacher_add_group"))\
                    .add(types.InlineKeyboardButton(text="Добавить задание", callback_data="teacher_add_task"))
                await self.bot.send_message(chat_id=chat_id, text="Выберите действие:", reply_markup=teacher_menu)
            else:
                await self.bot.send_message(chat_id=chat_id,
                                            text="Ваш статус еще не подтвержден администратором, сообщите ему код " + teacher.confirm_code)

    def close(self):
        self.dbconn.close()

    async def handle_callback(self, query: types.CallbackQuery):
        await query.message.edit_reply_markup()
        answer_data = query.data
        chat_id = query.message.chat.id
        user = self.userRepo.find_user(chat_id)

        if answer_data == "step1.1:student":
            if user is not None:
                await query.message.reply("Вы уже зарегистрированы как " + user.type)
                return
            await self.process_student_step11(chat_id, query)
            return

        if answer_data == "step1.1:teacher":
            if user is not None:
                await query.message.reply("Вы уже зарегистрированы как " + user.type)
                return
            user = await self.process_teacher_step11(chat_id, query)
            return

        if answer_data.startswith("step2.group:"):
            if user is not None:
                await query.message.reply("Вы уже зарегистрированы как " + user.type)
                return
            await self.process_user_step2(answer_data, chat_id, query)
            return

        if answer_data == "teacher_add_group":
            groups = self.userRepo.get_availible_teacher_groups(user.id)
            if groups is None or len(groups) == 0:
                await self.bot.send_message(chat_id=chat_id, text="Нет доступных классов")
                return

            add_groups_kb = types.InlineKeyboardMarkup()
            for g in groups:
                button = types.InlineKeyboardButton(text=g.name, callback_data="teacher:add_group:" + g.id)
                add_groups_kb.add(button)
            await self.bot.send_message(chat_id=chat_id, text="Выберите класс для добавления",
                                        reply_markup=add_groups_kb)
            return

        if answer_data.startswith("teacher:add_group:"):
            group_id = answer_data[len("teacher:add_group:"):]
            self.userRepo.add_teacher_group(user.id, group_id)
            await self.bot.send_message(chat_id=chat_id, text="Класс добавлен")
            await self.show_main_user_menu(chat_id, user)
            return

        if answer_data == "teacher_show_groups":
            groups = self.userRepo.get_teacher_groups(user.id)
            text = "Ваши классы:"
            if groups is None or len(groups) == 0:
                text = text + " нет классов"
            else:
                for g in groups:
                    text = text + " " + g.name
            await self.bot.send_message(chat_id=chat_id, text=text)
            await self.show_main_user_menu(chat_id, user)
            return

        if answer_data == "teacher_add_task":
            groups = self.userRepo.get_teacher_groups(user.id)
            if groups is None or len(groups) == 0:
                await self.bot.send_message(chat_id=chat_id, text="Нет доступных классов")
                return

            add_task_kb = types.InlineKeyboardMarkup()
            for g in groups:
                button = types.InlineKeyboardButton(text=g.name, callback_data="teacher:add_task:" + g.id)
                add_task_kb.add(button)
            await self.bot.send_message(chat_id=chat_id, text="Выберите класс для добавления задания",
                                        reply_markup=add_task_kb)
            return

        if answer_data.startswith("teacher:add_task:"):
            group_id = answer_data[len("teacher:add_task:"):]
            self.stageRepo.set_stage_data(user.id, "add_task_1", {"group_id": group_id})
            await self.bot.send_message(chat_id=chat_id, text="Введите название предмета:")
            return

        if answer_data == "student_show_tasks":
            tasks = self.taskRepo.list_user_tasks(user.id)
            if tasks is None or len(tasks) == 0:
                await self.bot.send_message(chat_id=chat_id, text="Нет невыполненных заданий !")
                return
            text = "Задания:\r\n"
            cnt = 1
            for t in tasks:
                text = text + str(cnt) + ". " + t.subject + ": " + t.text + "\r\n"
                cnt = cnt + 1
            await self.bot.send_message(chat_id=chat_id, text=text)
            return

        if user is not None:
            await self.show_main_user_menu(chat_id, user)

    async def process_student_step11(self, chat_id, query: types.CallbackQuery):
        keyboard_choose_group = types.InlineKeyboardMarkup()
        groups = self.groupRepo.list_group()
        for g in groups:
            group1_button = types.InlineKeyboardButton(text=g.name, callback_data="step2.group:" + g.id)
            keyboard_choose_group.add(group1_button)
        await self.bot.send_message(chat_id, text="Укажите группу, к которой Вы относитесь",
                                    reply_markup=keyboard_choose_group)

    async def process_user_step2(self, answer_data: str, chat_id: str, query: types.CallbackQuery):
        group_id = answer_data[len("step2.group:"):]
        user = User(chat_id)
        user.name = query.from_user.full_name
        group = self.groupRepo.find_group(group_id)
        # В БД создаем запись об ученике
        self.userRepo.create_student(user, group_id)
        print("student created")
        await self.bot.send_message(chat_id, text="Поздравляю, Вы зарегистрированы как ученик в " + group.name)

    async def process_teacher_step11(self, chat_id: str, query: types.CallbackQuery):
        code = str(self.generate_code())
        user = User(chat_id)
        # получаем юзернейм пользователя
        user.name = query.from_user.full_name
        # В БД создаем запись об учителе
        self.userRepo.create_teacher(user, False, code)
        await self.bot.send_message(chat_id,
                               text="Обратитесь к администратору, чтобы он подтвердил, что вы - учитель, ваш код :" + code)
        return user

    @staticmethod
    def generate_code():
        return random.randrange(1000, 9999, 1)

    async def process_stage(self, text: str, user: User, stage: Stage):
        if stage.step == "add_task_1":
            stage.step = "add_task_2"
            stage.params['subject'] = text
            self.stageRepo.set_stage(stage)
            await self.bot.send_message(user.id,
                               text="Введите текст задания:")
            return
        if stage.step == "add_task_2":
            stage.step = "add_task_3"
            stage.params['task'] = text
            self.stageRepo.set_stage(stage)
            await self.bot.send_message(user.id,
                               text="Через сколько дней необходимо сдать задание ?")
            return
        if stage.step == "add_task_3":
            self.stageRepo.delete_stage(user.id)
            task = Task(task_id=str(uuid.uuid4()),
                        due_date=datetime.date(datetime.now() + timedelta(days=int(text))),
                        user_id=user.id,
                        group_id=stage.params['group_id'],
                        subject=stage.params['subject'],
                        text=stage.params['task'])
            self.taskRepo.add_task(task)
            await self.bot.send_message(user.id,
                               text="Задание по предмету " + stage.params['subject'] + " добавлено классу " + stage.params['group_id'])
            return

