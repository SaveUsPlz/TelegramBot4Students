from datetime import date

from db_conn import DBConnection
from task import Task


class TaskRepository:
    def __init__(self, conn: DBConnection) -> None:
        self.conn = conn

    def add_task(self, task: Task):
        pass

    def list_user_tasks(self, user_id: str):
        pass

    def mark_task_done(self, user_id: str, task_id: str):
        pass

    @staticmethod
    def date_to_int(adate: date):
        return adate.year * 1000 + adate.month * 100 + adate.day
