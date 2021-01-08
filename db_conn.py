import sqlite3
from sqlite3 import Error


class DBConnection:
    def __init__(self, path) -> None:
        self.connection = None
        try:
            self.connection = sqlite3.connect(path)
            print("Connection to SQLite DB successful")
            self.initdb()
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


    def exec(self, sql):
        c = self.connection.cursor()
        c.execute(sql)
        c.close()

