import uuid
from datetime import date, datetime

from db_conn import DBConnection
from task import Task


class TaskRepository:
    def __init__(self, conn: DBConnection) -> None:
        self.conn = conn

    def add_task(self, task: Task):
        c = self.conn.conn().cursor()
        c.execute("insert into task(id, user_id,group_id,subject,due_date,task_text) "
                  "values(:id, :user_id, :group_id, :subject, :due_date, :task_text)",
                  {"id": task.id, "user_id": task.user_id, "group_id": task.group_id, "subject": task.subject,
                   "due_date": self.date_to_int(task.due_date), "task_text": task.text})
        c.close()
        self.conn.conn().commit()

    def list_user_tasks(self, user_id: str):
        c = self.conn.conn().cursor()
        dd = self.date_to_int(datetime.date(datetime.now()))
        c.execute("select t.id, t.user_id, t.group_id, t.subject, t.due_date, t.task_text"
                  " from task t join student s on s.group_id = t.group_id "
                  " left join done_task dt on dt.user_id = :id and dt.task_id = t.id "
                  "where dt.id is null and t.due_date >= :date "
                  "order by t.due_date, t.subject", {"id": user_id, "date": dd})

        results = c.fetchall()
        tasks = []
        for i in results:
            tasks.append(Task(task_id=i[0],
                              due_date=datetime.date(datetime.now()),
                              user_id=i[1],
                              group_id=i[2],
                              subject=i[3],
                              text=i[5]))
        c.close()
        return tasks

    def mark_task_done(self, user_id: str, task_id: str):
        c = self.conn.conn().cursor()
        c.execute("select id from done_task dt where dt.user_id = :id and dt.task_id = :tid"
                  , {"id": user_id, "tid": task_id})

        results = c.fetchone()
        c.close()
        if results is None:
            c = self.conn.conn().cursor()
            c.execute("insert into done_task(id, user_id, task_id, done_date) "
                      "values(:id, :user_id, :task_id, :done_date)",
                      {"id": str(uuid.uuid4()), "user_id": user_id, "task_id": task_id, "done_date": 0})
            c.close()
            self.conn.conn().commit()

    @staticmethod
    def date_to_int(adate: date):
        return adate.year * 10000 + adate.month * 100 + adate.day
