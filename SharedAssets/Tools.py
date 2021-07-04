import datetime
import os.path
import time


def date_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y %H:%M:%S')


def format_print(s: str, opt=""):
    if opt == "":
        print(f"{date_time()}> {s}")
    else:
        print(f"{date_time()}> ({opt}) {s}")

def is_file_mk(s: str):
    if os.path.isfile(s):
        return True
    format_print(f"File does not exist, making {s}")
    with open(s, 'w+') as f:
        f.write("")
        f.close()


def is_dir_mk(s: str):
    if os.path.isdir(s):
        return True
    format_print(f"Directory does not exist, making {s}")
    os.mkdir(s)
    return os.path.isdir(s)
