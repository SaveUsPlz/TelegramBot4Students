import sqlite3
from sqlite3 import Error


class DBConnection:
    def __init__(self, path) -> None:
        self.connection = None
        try:
            self.connection = sqlite3.connect(path)
        except Error as e:
            print(f"The error '{e}' occurred")

    def conn(self):
        return self.connection

    def initdb(self):
        self.exec("create table if not exists user(id varchar(255) not null primary key, name varchar(255) not null, "
                  "user_type varchar(255) not null)")
        print("Table user created")
        self.exec("""
                CREATE TABLE if not exists groups (
            id   VARCHAR (255) PRIMARY KEY,
            name VARCHAR (255) NOT NULL
                               UNIQUE
        )
        """)
        print("Table groups created")
        self.exec("""
        CREATE TABLE if not exists teacher_group (
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL,
            group_id VARCHAR (255) REFERENCES groups (id) ON DELETE CASCADE
                                   NOT NULL
        )
        """)
        print("Table teacher_group created")
        self.exec("""
        CREATE UNIQUE INDEX if not exists  idx_tg_uiserid_groupid ON teacher_group (
            user_id,
            group_id
        );
        """)

        self.exec("""
        CREATE TABLE if not exists student (
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL primary key,
            group_id VARCHAR (255) REFERENCES groups (id) ON DELETE CASCADE
                                   NOT NULL
        )
        """)

        self.exec("""
        CREATE TABLE if not exists teacher (
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL primary key,
            confirmed boolean default false,
            confirm_code VARCHAR (255)
        )
        """)
        self.exec("""
        CREATE TABLE if not exists stage (
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL primary key,
            step varchar(255) not null,
            params text
        )
        """)

        self.exec("""
        CREATE TABLE if not exists task (
            id VARCHAR (255) NOT NULL primary key,
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL,
            group_id  VARCHAR (255) REFERENCES groups (id) NOT NULL,
            subject varchar(255) not null,
            due_date integer not null,
            task_text text not null
        )
        """)

        self.exec("""
        CREATE TABLE if not exists done_task (
            id VARCHAR (255) NOT NULL primary key,
            user_id  VARCHAR (255) REFERENCES user (id) ON DELETE CASCADE NOT NULL,
            task_id  VARCHAR (255) REFERENCES task (id) ON DELETE CASCADE NOT NULL,
            done_date integer not null
        )
        """)
        print("DB structure created")

    def exec(self, sql):
        c = self.connection.cursor()
        c.execute(sql)
        c.close()

    def close(self):
        self.connection.close()

