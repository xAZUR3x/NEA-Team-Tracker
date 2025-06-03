import datetime as dt
import hash_table_functions as ht


# strength check
def strong(password):
    if len(password) < 8:
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+" for char in password):
        return False
    return True


# importance functions
def deadline_missed(datestr):
    return dt.datetime.strptime(datestr, "%Y-%m-%d").date() < dt.date.today()


def deadline_approaching(datestr):
    return dt.datetime.strptime(datestr, "%Y-%m-%d").date() in [
        dt.date.today(),
        dt.date.today() + dt.timedelta(1),
    ]


def importance(datestr, baseimportance):
    if baseimportance == 0:
        return 6
    if datestr == "0-0-0":
        return baseimportance
    if deadline_missed(datestr):
        return 5
    if deadline_approaching(datestr):
        return baseimportance + 1
    return baseimportance


# create username
def create_username(firstname, lastname):
    i = 1
    while True:
        username = f"{firstname[0].lower()}{lastname.lower()}{i}"
        if not ht.search(username):
            ht.insert(username)
            return username
        i += 1


# date validity check
def date_valid(day, month, year):
    if not (day.isdigit() and month.isdigit() and year.isdigit()):
        return False
    day = int(day)
    month = int(month)
    year = int(year)
    if month > 12 or month < 1:
        return False
    if day > 31 or day < 1:
        return False
    if month in [4, 6, 9, 11] and day > 30:
        return False
    if month == 2:
        if (year % 400 == 0) or (year % 100 != 0 and year % 4 == 0):
            max_days = 29
        else:
            max_days = 28
        if day > max_days:
            return False
    if year > 9999:
        return False
    if dt.date(year, month, day) < dt.date.today():
        return False
    return True


# calendar cell functions
def get_cell_day(i):
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    date = dt.date.today() + dt.timedelta(days=i - dt.date.today().weekday())
    return (
        (months[date.month - 1] + " " + str(date.day))
        if date.day == 1
        else date.day
    )


def get_cell_date_string(i):
    cell_day = dt.date.today() + dt.timedelta(
        days=i - dt.date.today().weekday()
    )
    return f"{cell_day.year}-{cell_day.month}-{cell_day.day}"


def get_cell_bg(i):
    cell_day = dt.date.today() + dt.timedelta(
        days=i - dt.date.today().weekday()
    )
    if cell_day < dt.date.today():
        return "darkgrey"
    if cell_day == dt.date.today():
        return "lightblue"
    if cell_day.weekday() in [5, 6]:
        return "lightgrey"
    return "white"


# sort
def merge_sort(data, key=lambda x: x):
    if len(data) <= 1:
        return data
    mid = len(data) // 2
    left = merge_sort(data[:mid], key)
    right = merge_sort(data[mid:], key)
    return _merge(left, right, key)


def _merge(left, right, key):
    # underscore signals the subroutine is for use internally
    result = []
    i = j = 0
    # i is left index, j is right index

    while i < len(left) and j < len(right):
        if key(left[i]) < key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    while i < len(left):
        result.append(left[i])
        i += 1
    while j < len(right):
        result.append(right[j])
        j += 1

    return result
