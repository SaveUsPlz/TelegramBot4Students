from datetime import date


class Task:
    def __init__(self, task_id: str, user_id: str, group_id: str, due_date: date, subject: str, text: str) -> None:
        self.id = task_id
        self.user_id = user_id
        self.group_id = group_id
        self.due_date = due_date
        self.subject = subject
        self.text = text
