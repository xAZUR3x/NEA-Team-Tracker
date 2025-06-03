FILE_NAME = "username_hash_table.bin"
TABLE_SIZE = 64
RECORD_LENGTH = 32
EMPTY_BYTE = b"\x00"
OCCUPIED_FLAG = b"\x01"
TOMBSTONE_FLAG = b"\x02"


def hash(input):
    output = 0
    pos_multiplier = 31
    for i, char in enumerate(list(input)):
        output += ord(char) * (pos_multiplier**i)
    return output % TABLE_SIZE


def pad(item):
    return OCCUPIED_FLAG + item.encode("utf-8").ljust(
        RECORD_LENGTH - 1, EMPTY_BYTE
    )


def unpad(raw_bytes):
    return raw_bytes[1:].rstrip(EMPTY_BYTE).decode("utf-8")


def insert(item):
    index = hash(item)
    first_tombstone_offset = -1

    for i in range(TABLE_SIZE):
        probe_index = (index + i) % TABLE_SIZE
        offset = probe_index * RECORD_LENGTH

        with open(FILE_NAME, "r+b") as f:
            f.seek(offset)
            raw = f.read(RECORD_LENGTH)
            flag = raw[0:1]
            data = raw[1:]
            existing_item = data.rstrip(EMPTY_BYTE).decode("utf-8")

            if flag == EMPTY_BYTE:
                f.seek(
                    first_tombstone_offset
                    if first_tombstone_offset != -1
                    else offset
                )
                f.write(pad(item))
                return True
            # sets first tombstone offset
            elif flag == TOMBSTONE_FLAG and first_tombstone_offset == -1:
                first_tombstone_offset = offset
            # checks if the item already exists in the table
            elif flag == OCCUPIED_FLAG and existing_item == item:
                return False

    # no empty spaces but a tombstone is available
    if first_tombstone_offset is not None:
        with open(FILE_NAME, "r+b") as f:
            f.seek(first_tombstone_offset)
            f.write(pad(item))
        return True

    return False


def search(item):
    index = hash(item)

    for i in range(TABLE_SIZE):
        probe_index = (index + i) % TABLE_SIZE
        offset = probe_index * RECORD_LENGTH

        with open(FILE_NAME, "rb") as f:
            f.seek(offset)
            raw = f.read(RECORD_LENGTH)
            flag = raw[0:1]

            if flag == EMPTY_BYTE:
                return False
            elif flag == OCCUPIED_FLAG and unpad(raw) == item:
                return True

    return False


def delete(item):
    index = hash(item)

    for i in range(TABLE_SIZE):
        probe_index = (index + i) % TABLE_SIZE
        offset = probe_index * RECORD_LENGTH

        with open(FILE_NAME, "r+b") as f:
            f.seek(offset)
            raw = f.read(RECORD_LENGTH)
            flag = raw[0:1]

            if flag == EMPTY_BYTE:
                return False
            elif flag == OCCUPIED_FLAG and unpad(raw) == item:
                f.seek(offset)
                f.write(TOMBSTONE_FLAG + EMPTY_BYTE * (RECORD_LENGTH - 1))
                return True

    return False
