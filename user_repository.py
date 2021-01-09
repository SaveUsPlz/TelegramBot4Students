from db_conn import DBConnection
from group import Group
from student import Student
from teacher import Teacher
from user import User
from sqlite3 import Error


class UserRepository:
    def __init__(self, conn: DBConnection) -> None:
        self.conn = conn

    def find_user(self, userid) -> User:
        c = self.conn.conn().cursor()
        c.execute("select id, name, user_type from user where id = :id", {"id": userid})
        results = c.fetchone()
        # print(results)
        c.close()
        if results is None:
            return None
        user = User(results[0])
        user.name = results[1]
        user.type = results[2]
        return user

    def create_student(self, user: User, groupid: str):
        c = self.conn.conn().cursor()
        c.execute("insert into user(id, name, user_type) values(:id, :name, :type)",
                  {"id": user.id, "name": user.name, "type": "STUDENT"})
        c.close()
        c = self.conn.conn().cursor()
        c.execute("insert into student(user_id, group_id) values(:id, :groupid)",
                  {"id": user.id, "groupid": groupid})
        c.close()
        self.conn.conn().commit()

    def create_teacher(self, user: User, confirmed: bool, confirm_code: str):
        c = self.conn.conn().cursor()
        c.execute("insert into user(id, name, user_type) values(:id, :name, :type)",
                  {"id": user.id, "name": user.name, "type": "TEACHER"})
        c.close()
        c = self.conn.conn().cursor()
        c.execute("insert into teacher(user_id, confirmed, confirm_code) values(:id, :confirmed, :confirm_code)",
                  {"id": user.id, "confirmed": confirmed, "confirm_code": confirm_code})
        c.close()
        self.conn.conn().commit()

    def get_teacher_groups(self, teacherid):
        c = self.conn.conn().cursor()
        c.execute("select g.id, g.name from groups g join teacher_group tg on tg.group_id = g.id where tg.user_id = "
                  ":id order by g.name", {"id": teacherid})
        results = c.fetchall()
        groups = []
        for i in results:
            groups.append(Group(i[0], i[1]))
        c.close()
        return groups

    def add_teacher_group(self, teacherid, groupid):
        c = self.conn.conn().cursor()
        try:
            c.execute("insert into teacher_group(user_id, group_id) values(:tid, :gid)",
                      {"gid": groupid, "tid": teacherid})
        except Error as e:
            print(f"The error '{e}' occurred")
        c.close()
        self.conn.conn().commit()

    def remove_teacher_group(self, teacherid, groupid):
        c = self.conn.conn().cursor()
        try:
            c.execute("delete from where user_id = :tid and group_id = :gid)",
                      {"gid": groupid, "tid": teacherid})
        except Error as e:
            print(f"The error '{e}' occurred")
        c.close()
        self.conn.conn().commit()

    def get_student(self, userid: str) -> Student:
        c = self.conn.conn().cursor()
        c.execute("select group_id from student where user_id = :id", {"id": userid})
        results = c.fetchone()
        c.close()
        if results is None:
            return None
        student = Student(userid, results[0])
        return student

    def get_teacher(self, userid: str) -> Teacher:
        c = self.conn.conn().cursor()
        c.execute("select confirmed, confirm_code from teacher where user_id = :id", {"id": userid})
        results = c.fetchone()
        c.close()
        if results is None:
            return None
        teacher = Teacher(userid)
        teacher.confirmed = results[0]
        teacher.confirm_code = results[1]
        teacher.groups = self.get_teacher_groups(userid)
        return teacher

    def confirm_teacher(self, confirm_code: str) -> Teacher:
        c = self.conn.conn().cursor()
        c.execute("select user_id from teacher where confirm_code = :confirm_code", {"confirm_code": confirm_code})
        results = c.fetchone()
        c.close()
        if results is None:
            return None
        user_id = results[0]
        c = self.conn.conn().cursor()
        c.execute("update teacher set confirm_code = null, confirmed = true where user_id = :id", {"id": user_id})
        c = self.conn.conn().commit();
        return self.get_teacher(user_id)

    def get_availible_teacher_groups(self, user_id: str):
        c = self.conn.conn().cursor()
        c.execute("select g.id, g.name from groups g left join teacher_group tg on tg.group_id = g.id and tg.user_id = :id where "
                  "  tg.group_id is null order by g.name", {"id": user_id})
        results = c.fetchall()
        groups = []
        for i in results:
            groups.append(Group(i[0], i[1]))
        c.close()
        return groups

