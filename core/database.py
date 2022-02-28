import sqlite3
from functools import wraps


def tasks(func):
    @wraps(func)
    def inner(db, *args, **kwargs):
        """
        Decorator to do important tasks to use database like open, commit or rollback db
        """
        # Try to open db and execute function
        try:
            db.open()
            func(db, *args, **kwargs)
            pass
        # If an error was occured, print error and rollback db
        except Exception as e:
            print(f"An error was occured with database: {e}")
            db.connection.rollback()
        # Close db
        finally:
            db.close()
    return inner

class Database:
    """sqlite3 database class that holds testers jobs"""
    DB_LOCATION = "db.sqlite3"

    def __init__(self):
        pass

    def open(self):
        """Create database connection"""
        self.connection = sqlite3.connect(Database.DB_LOCATION)
        self.cur = self.connection.cursor()

    def close(self):
        """close sqlite3 connection"""
        self.connection.close()

    @tasks
    def execute(self, sql:str, args:list=[]) -> None:
        """execute a row of data to current cursor"""
        self.cur.execute(sql, args)
        self.connection.commit()
    
    @tasks
    def fetchone(self, sql:str, args:list=[]):
        """fetchone data from current cursor"""
        self.cur.execute(sql, args)
        return self.cur.fetchone()
    
    @tasks
    def fetchall(self, sql:str, args:list=[]):
        """fetchall data from current cursor"""
        self.cur.execute(sql, args)
        return self.cur.fetchall()

    @tasks
    def create_table(self) -> None:
        """create a database table if it does not exist already"""
        self.cur.execute('''CREATE TABLE IF NOT EXISTS "infractions" (
                            "infraction_id"	INTEGER NOT NULL UNIQUE,
                            "member_id"	INTEGER NOT NULL,
                            "moderator_id"	INTEGER NOT NULL,
                            "action"	TEXT NOT NULL,
                            "timestamp"	INTEGER NOT NULL,
                            "end_timestamp"	INTEGER NOT NULL,
                            "reason"	TEXT,
                            PRIMARY KEY("infraction_id" AUTOINCREMENT)
                        );''')

    def commit(self):
        """commit changes to database"""
        self.connection.commit()