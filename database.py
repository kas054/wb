import sqlite3

connection = sqlite3.connect("database.db")

def get_db() -> sqlite3.Connection:
    db = sqlite3.connect("database.db",  check_same_thread=False)
    try:
        yield db
    finally:
        db.close()


def create_db_and_tables():
    create_table_users = """create table if not exists users (
                                    id integer primary key AUTOINCREMENT, 
                                    name text not NULL,
                                    password text NOT NULL
                                );"""
    create_table_chocolate = """create table if not exists chocolate (
                                    id integer Primary key AUTOINCREMENT, 
                                    name text not NULL,
                                    available boolean NOT NULL,
                                    image text NOT NULL
                                 );"""
    create_table_comments = """create table if not exists comments (
                                    user_id integer NOT NULL,
                                    choco_id integer NOT NULL,
                                    comment text,
                                    FOREIGN KEY (user_id) REFERENCES users(id),
                                    FOREIGN KEY (choco_id) REFERENCES chocolate(id),
                                    PRIMARY KEY (user_id, choco_id)
                                );"""

    connection = sqlite3.connect("database.db", check_same_thread=False)
    cursor = connection.cursor()
    cursor.execute(create_table_users)
    cursor.execute(create_table_chocolate)
    cursor.execute(create_table_comments)
    connection.close()



