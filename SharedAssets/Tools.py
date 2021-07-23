# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Some tools and helpers that currently dont have a home
# ======================================================================================================================
import datetime
import os.path
import time


# ======================================================================================================================
# =============================== Format Print =========================================================================
# ======================================================================================================================

# get date and time in string format
def date_time():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y %H:%M:%S')


# print outputs in formatted state with date-time and optionally another name in front of text
def format_print(s: str, opt=""):
    if opt == "":
        print(f"{date_time()}> {s}")
    else:
        print(f"{date_time()}> ({opt}) {s}")


# ======================================================================================================================
# =============================== Directory ============================================================================
# ======================================================================================================================

# if file does not exist, make one
def is_file_mk(s: str):
    if os.path.isfile(s):
        return True
    format_print(f"File does not exist, making {s}")
    with open(s, 'w+') as f:
        f.write("")
        f.close()

# if folder does not exist make one
def is_dir_mk(s: str):
    if os.path.isdir(s):
        return True
    format_print(f"Directory does not exist, making {s}")
    os.mkdir(s)
    return os.path.isdir(s)


# ======================================================================================================================
# =============================== Counter ==============================================================================
# ======================================================================================================================

# increments a counter and returns the value or get current value
class Counter:

    def __init__(self, start=0):
        self.i = start

    def add(self):
        self.i += 1
        return self.i

    def same(self):
        return self.i


# ======================================================================================================================
# =================================== Time =============================================================================
# ======================================================================================================================

# gets difference between times and give an approximate string in response
def approximate_time_difference(other_time):
    now = time.time()
    if isinstance(other_time, str) and not other_time == "":
        then = float(other_time)
        diff = now - then
    elif isinstance(other_time, float):
        diff = now - other_time
    else:
        return "unknown"
    if diff < 55:
        return "a few seconds"
    elif diff < 110:
        return "a minute"
    elif diff < 600:
        return "minutes"
    elif diff < 1350:
        return "fifteen min"
    elif diff < 2700:
        return "half an hour"
    else:
        hrs = round(diff / 3600)
        return f"{hrs} hours"

