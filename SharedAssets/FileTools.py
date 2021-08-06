import os
import datetime as dt
from SharedAssets import Tools

module_name = "FileTools"


def get_most_recent(dir: str, file_type: str) -> str:
    largest = (0, "")
    if os.path.isdir(dir):
        filenames = next(os.walk(dir), (None, None, []))[2]  # [] if no file
        for fname in filenames:
            slp_ex = fname.split(".")
            if slp_ex[1] == file_type:
                spl_t = slp_ex[0].split("-")
                time = dt.datetime(int(spl_t[0]),int(spl_t[1]),int(spl_t[2]),int(spl_t[3]),int(spl_t[4])).timestamp()
                if time > largest[0]:
                    largest = (time, fname)
        Tools.format_print(f"Fount most recent file: {largest[1]}", module_name)
    else:
        Tools.format_print(f"Directory does not exist: {dir}", module_name)
    return largest[1]
