import sqlite3 as sq
import hash_table_functions as ht
from cryptography.fernet import Fernet
from misc_functions import *
import datetime as dt


def _get_fernet_object():
    with open("key.key", "rb") as key_file:
        fernet = Fernet(key_file.read())
    return fernet


# SELECT functions
def login_valid(username, entered_password):
    fernet = _get_fernet_object()
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT Password FROM Account WHERE Username = ?""", (username,)
    )
    stored_password = cur.fetchall()
    cur.close()
    conn.close()
    if stored_password:
        if entered_password == fernet.decrypt(stored_password[0][0]).decode():
            return True
    return False


def active(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT Active FROM Account WHERE Username = ?""", (username,)
    )
    active = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return bool(active)


def admin(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Admin FROM Account WHERE Username = ?""", (username,))
    admin = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return bool(admin)


def deadline_present(task_id):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Deadline FROM Task WHERE TaskID = ?""", (task_id,))
    deadline = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    if deadline == "0-0-0":
        return False
    return True


def account_info_string(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Team FROM Account WHERE Username = ?""", (username,))
    account_info = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    if account_info == "operational":
        return f"{get_name(username)} | Operational"
    elif account_info == "development":
        return f"{get_name(username)} | Development"
    elif account_info == "both":
        return f"{get_name(username)} | Operational & Development"


def stats_string(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT COUNT(Task.TaskID)
           FROM Task, Assignment, Account
           WHERE Task.TaskID = Assignment.TaskID
             AND Assignment.Username = Account.Username
             AND Account.Username = ? 
             AND Task.State = 'doing'""",
        (username,),
    )
    doing = cur.fetchall()[0][0]
    cur.execute(
        """SELECT COUNT(Task.TaskID) 
           FROM Task, Assignment, Account 
           WHERE Task.TaskID = Assignment.TaskID 
             AND Assignment.Username = Account.Username 
             AND Account.Username = ? 
             AND Task.State = 'done'""",
        (username,),
    )
    done = cur.fetchall()[0][0]
    cur.execute(
        """SELECT COUNT(Event.EventID) 
           FROM Event, Attendance, Account 
           WHERE Event.EventID = Attendance.EventID 
             AND Attendance.Username = Account.Username 
             AND Account.Username = ?""",
        (username,),
    )
    events = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return f"""You have {doing+done} tasks assigned to you, {done} of which are completed.\nYou have {events} events in your calendar."""


def team(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Team FROM Account WHERE Username = ?""", (username,))
    team = cur.fetchall()[0][0]
    cur.close()
    conn.close()
    return team


def get_name(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT FirstName, LastName FROM Account WHERE Username = ?""",
        (username,),
    )
    name = cur.fetchall()[0]
    cur.close()
    conn.close()
    return f"{name[0]} {name[1]}"


def get_tasks(team, column):
    if team == "both":
        team1 = "operational"
        team2 = "development"
    else:
        team1 = team2 = team

    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    if column == 0:
        cur.execute(
            """SELECT * FROM Task 
               WHERE (Team = ? OR Team = ? OR Team = 'both') 
                 AND State = 'backlog'""",
            (team1, team2),
        )
    elif column == 1:
        cur.execute(
            """SELECT * FROM Task 
               WHERE (Team = ? OR Team = ? OR Team = 'both') 
                 AND State = 'to do'""",
            (team1, team2),
        )
    elif column == 2:
        cur.execute(
            """SELECT * FROM Task 
               WHERE (Team = ? OR Team = ? OR Team = 'both') 
                 AND State = 'doing'""",
            (team1, team2),
        )
    elif column == 3:
        cur.execute(
            """SELECT * FROM Task 
               WHERE (Team = ? OR Team = ? OR Team = 'both') 
                 AND State = 'done'""",
            (team1, team2),
        )
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return merge_sort(tasks, key=lambda task: importance(task[4], task[5]))[
        ::-1
    ]


def get_task(task_id):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT * FROM Task WHERE TaskID = ?""", (task_id,))
    task = cur.fetchall()[0]
    cur.close()
    conn.close()
    return task


def get_task_bg(task_id, username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT * FROM Assignment 
           WHERE TaskID = ? AND Username = ?""",
        (task_id, username),
    )
    assigned = cur.fetchall()
    cur.close()
    conn.close()
    return "lightblue" if bool(assigned) else "SystemButtonFace"


def get_usernames_from_team(team):
    if team == "both":
        conn = sq.connect("team_tracker.db")
        cur = conn.cursor()
        cur.execute("""SELECT Username FROM Account""")
        usernames = cur.fetchall()
        cur.close()
        conn.close()
    else:
        conn = sq.connect("team_tracker.db")
        cur = conn.cursor()
        cur.execute(
            """SELECT Username FROM Account 
               WHERE Team = ? OR Team = 'both' 
               ORDER BY Username""",
            (team,),
        )
        usernames = cur.fetchall()
        cur.close()
        conn.close()
    return [i[0] for i in usernames]


def get_deadlines(date, username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    userteam = team(username)
    if userteam == "both":
        cur.execute(
            """SELECT Task.Title, Task.BaseImportance 
               FROM Task, Assignment 
               WHERE Task.Deadline = ? 
                 AND ((Task.State = 'backlog' OR Task.State = 'to do') 
                   OR (Task.TaskID = Assignment.TaskID 
                     AND Assignment.Username = ?)) 
               ORDER BY Task.Title""",
            (date, username),
        )
    else:
        cur.execute(
            """SELECT Task.Title, Task.BaseImportance 
               FROM Task, Assignment 
               WHERE Task.Deadline = ? 
                 AND (((Task.State = 'backlog' OR Task.State = 'to do') 
                     AND Task.Team = ?) 
                   OR (Task.TaskID = Assignment.TaskID 
                     AND Assignment.Username = ?)) 
               ORDER BY Task.Title""",
            (date, userteam, username),
        )
    data = cur.fetchall()
    cur.close()
    conn.close()
    deadlines = []
    for i in data:
        if i[0] not in [j[0] for j in deadlines]:
            deadlines.append(i)
    return deadlines


def get_events(date, username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """SELECT Event.Title 
           FROM Event, Attendance 
           WHERE Event.EventID = Attendance.EventID 
             AND Event.Date = ? 
             AND Attendance.Username = ? 
           ORDER BY Event.Title""",
        (date, username),
    )
    events = cur.fetchall()
    cur.close()
    conn.close()
    return [i[0] for i in events]


def get_all_usernames():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Username FROM Account ORDER BY Username""")
    usernames = cur.fetchall()
    cur.close()
    conn.close()
    return [i[0] for i in usernames]


def get_all_events():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT Title FROM Event ORDER BY Title""")
    events = cur.fetchall()
    cur.close()
    conn.close()
    return list(dict.fromkeys([i[0] for i in events]))


# UPDATE functions
def set_new_password(username, new_password):
    fernet = _get_fernet_object()
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Account 
           SET Password = ?, Active = 1 
           WHERE Username = ?""",
        (fernet.encrypt(new_password.encode()), username),
    )
    conn.commit()
    cur.close()
    conn.close()


def update_state(task_id, new_state):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Task SET State = ? WHERE TaskID = ?""", (new_state, task_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def update_deadline(task_id, new_deadline):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Task SET Deadline = ? WHERE TaskID = ?""",
        (new_deadline, task_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def update_importance(task_id, new_importance):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Task SET BaseImportance = ? WHERE TaskID = ?""",
        (new_importance, task_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def edit_task(task_id, team, description, deadline, baseimportance):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Task 
           SET Description = ?, Deadline = ?, 
               BaseImportance = ?, Team = ? 
           WHERE TaskID = ?""",
        (description, deadline, baseimportance, team, task_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def save_changes(username, team, active, admin):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """UPDATE Account 
           SET Team = ?, Active = ?, Admin = ? 
           WHERE Username = ?""",
        (team, active, admin, username),
    )
    conn.commit()
    cur.close()
    conn.close()


# DELETE functions
def delete_task(task_id):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""DELETE FROM Assignment WHERE TaskID = ?""", (task_id,))
    cur.execute("""DELETE FROM Task WHERE TaskID = ?""", (task_id,))
    conn.commit()
    cur.close()
    conn.close()


def delete_event(title):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """DELETE FROM Attendance 
           WHERE EventID IN (SELECT EventID FROM Event WHERE Title = ?)""",
        (title,),
    )
    cur.execute("""DELETE FROM Event WHERE Title = ?""", (title,))
    conn.commit()
    cur.close()
    conn.close()


def delete_account(username):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""DELETE FROM Assignment WHERE Username = ?""", (username,))
    cur.execute("""DELETE FROM Attendance WHERE Username = ?""", (username,))
    cur.execute("""DELETE FROM Account WHERE Username = ?""", (username,))
    conn.commit()
    cur.close()
    conn.close()
    ht.delete(username)


def clear_done():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT TaskID FROM Task WHERE State = 'done'""")
    for task_id in cur.fetchall():
        delete_task(task_id[0])
    conn.commit()
    cur.close()
    conn.close()


def clear_past_events():
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute("""SELECT EventID, Date FROM Event""")

    for event_id, date_str in cur.fetchall():
        event_date = dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        if event_date < dt.datetime.now().date():
            cur.execute(
                """DELETE FROM Attendance WHERE EventID = ?""", (event_id,)
            )
            cur.execute("""DELETE FROM Event WHERE EventID = ?""", (event_id,))

    conn.commit()
    cur.close()
    conn.close()


# INSERT functions
def add_task(title, description, state, deadline, baseimportance, team):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Task 
           (Title, Description, State, Deadline, BaseImportance, Team) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (title, description, state, deadline, baseimportance, team),
    )
    conn.commit()
    cur.close()
    conn.close()


def add_assignment(username, task_id):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Assignment (Username, TaskID) VALUES (?, ?)""",
        (username, task_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def add_event(title, date, attendees):
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Event (Title, Date) VALUES (?, ?)""", (title, date)
    )
    event_id = cur.lastrowid
    for attendee in attendees:
        cur.execute(
            """INSERT INTO Attendance (Username, EventID) VALUES (?, ?)""",
            (attendee, event_id),
        )
    conn.commit()
    cur.close()
    conn.close()


def add_account(username, firstname, lastname, password, team, admin):
    fernet = _get_fernet_object()
    conn = sq.connect("team_tracker.db")
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO Account 
           (Username, FirstName, LastName, Password, Team, Admin, Active) 
           VALUES (?, ?, ?, ?, ?, ?, 0)""",
        (
            username,
            firstname,
            lastname,
            fernet.encrypt(password.encode()),
            team,
            admin,
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
