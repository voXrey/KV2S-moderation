import sqlite3

class Database(object):
    """sqlite3 database class that holds testers jobs"""
    DB_LOCATION = "data/database.sqlite3"

    def __init__(self):
        """Initialize db class variables"""
        self.connection = sqlite3.connect(Database.DB_LOCATION)
        self.cur = self.connection.cursor()

    def close(self):
        """close sqlite3 connection"""
        self.connection.close()

    def execute(self, sql:str, args:list):
        """execute a row of data to current cursor"""
        self.cur.execute(sql, args)
        self.connection.commit()
    
    def fetchone(self, sql:str, args:list):
        """fetchone data from current cursor"""
        self.cur.execute(sql, args)
        return self.cur.fetchone()

    def fetchall(self, sql:str, args:list):
        """fetchall data from current cursor"""
        self.cur.execute(sql, args)
        return self.cur.fetchall()


    def create_table(self):
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