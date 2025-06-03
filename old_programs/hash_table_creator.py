from hash_table_functions import *
from sql_functions import get_all_usernames


def reset_hash_table():
    with open(FILE_NAME, "wb") as f:
        f.write(EMPTY_BYTE * TABLE_SIZE * RECORD_LENGTH)


def refill_hash_table():
    for username in get_all_usernames():
        insert(username)
