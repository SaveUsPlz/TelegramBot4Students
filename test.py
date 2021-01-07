from db_conn import DBConnection
from user_repository import UserRepository
from user import User
from group import Group
from grouprepository import GroupRepository
import uuid


# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # connect to db
    dbconn = DBConnection("e:/botdb.sqllite")
    userRepo = UserRepository(dbconn)
    groupRepo = GroupRepository(dbconn)

    groups = groupRepo.list_group()
    print("Groups:", groups)
    if len(groups) == 0:
        g = Group(str(uuid.uuid4()), "11А класс")
        groupRepo.create_group(g)
        g = Group(str(uuid.uuid4()), "11Б класс")
        groupRepo.create_group(g)

    groups = groupRepo.list_group()
    print("Groups2:", groups)

    userid_ = str(uuid.uuid4())
    # search user
    user = userRepo.find_user(userid_)
    print("user:", user)

    if user is None:
        print("Creating user")
        user = User(userid_)
        user.name = "User 1"
        userRepo.create_student(user, groups[0].id)

    user2 = userRepo.find_user(userid_)
    print("user2 :", user2)
    student = userRepo.get_student(user2.id)
    print("user2 group: ", student.groupid)

    teacherid = str(uuid.uuid4())
    teacher = userRepo.find_user(teacherid)
    if teacher is None:
        teacher = User(teacherid)
        teacher.name = "Teacher 1"
        teacher.type = "TEACHER"
        userRepo.create_teacher(teacher, False, "1234")

    confirmedTeacher = userRepo.confirm_teacher("1234")
    print("Confirmed : ", confirmedTeacher)
    userRepo.add_teacher_group(teacher.id, groups[0].id)
    print("teacher groups:", userRepo.get_teacher_groups(teacher.id))
