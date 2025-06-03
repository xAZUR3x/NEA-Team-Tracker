import sqlite3 as sq


def account():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE "Account" (
            "Username"	TEXT,
            "FirstName"	TEXT,
            "LastName"	TEXT,
            "Password"	BLOB,
            "Team"	TEXT,
            "Admin"	INTEGER,
            "Active"	INTEGER,
            PRIMARY KEY("Username")
    )"""
    )
    cur.close()
    conn.close()


def task():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE "Task" (
            "TaskID"	INTEGER,
            "Title"	TEXT,
            "Description"	TEXT,
            "State"	TEXT,
            "Deadline"	TEXT,
            "BaseImportance"	INTEGER,
            "Team"	TEXT,
            PRIMARY KEY("TaskID")
    )"""
    )
    cur.close()
    conn.close()


def event():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE "Event" (
            "EventID"	INTEGER,
            "Title"	TEXT,
            "Date"	TEXT,
            PRIMARY KEY("EventID")
    )"""
    )
    cur.close()
    conn.close()


def assignment():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE "Assignment" (
            "Username"	TEXT,
            "TaskID"	INTEGER,
            PRIMARY KEY("Username","TaskID"),
            FOREIGN KEY("TaskID") REFERENCES "Task"("TaskID"),
            FOREIGN KEY("Username") REFERENCES "Account"("Username")
    )"""
    )
    cur.close()
    conn.close()


def attendance():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE "Attendance" (
            "Username"	TEXT,
            "EventID"	INTEGER,
            PRIMARY KEY("Username","EventID"),
            FOREIGN KEY("EventID") REFERENCES "Event"("EventID"),
            FOREIGN KEY("Username") REFERENCES "Account"("Username")
    )"""
    )
    cur.close()
    conn.close()


def all():
    account()
    task()
    event()
    assignment()
    attendance()
