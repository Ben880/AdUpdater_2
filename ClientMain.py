# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Handles client power points and communication with master server
# ======================================================================================================================

# ======================================================================================================================
# =============================== imports ==============================================================================
# ======================================================================================================================
import socket
import psutil
import subprocess
import os.path
import time
import shutil
import datetime
import os
import sys
from SharedAssets.Config import Config as Config
# ======================================================================================================================
# =============================== create vars ==========================================================================
# ======================================================================================================================
cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
cfg = Config(configFile="clientcfg.json", fileDir=os.path.join(dir_path, "config"))
cfg.load()
# ======================================================================================================================
# =============================== load cfg vars ========================================================================
# ======================================================================================================================
powerPoint = cfg.getVal("power_point")
shortcutFile = cfg.getVal("power_point_shortcut")
verificationFile = cfg.getVal("verification_file")
printKeepAlive = cfg.getVal("print_keep_alive")
updateTimer = cfg.getVal("update_timer")
process_name = cfg.getVal("process_name")
localFolder = cfg.getVal("local_folder")
pidfile = cfg.getVal("pid_file")
# ======================================================================================================================
# =============================== functions ============================================================================
# ======================================================================================================================
def getPID():
    pid = list()
    for proc in psutil.process_iter():
        if process_name in proc.name():
            pid.append(proc.pid)
    return pid


def getPIDStats(pid: list):
    stats = list()
    for i in pid:
        p = psutil.Process(i)
        s = p.status()
        stats.append((i, s))
    return stats

def fetch_file():
    # kill running power point
    subprocess.call('taskkill /IM PPTVIEW.EXE /f', shell=True)
    # while local file exists try delete local file
    while os.path.isfile(localFolder + powerPoint):
        try:
            os.remove(localFolder + powerPoint)
        except PermissionError:
            printF("Cannot remove old file, trying again in 100ms.")
            time.sleep(.01)
    # grab remote file and start power point then verify update
    shutil.copy(remoteFolder + powerPoint, localFolder + powerPoint)
    subprocess.call("start " + localFolder + startFile, shell=True)
    updateVerification()


def printF(s):
    global printCheckForUpdates
    print(dt() + "> " + s)
    printCheckForUpdates = True


def dt():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%m-%d-%Y %H:%M:%S')


def updateVerification():
    f = open(localFolder + verificationFile, "w")
    f.write(dt())
    f.close()
    # TODO: logic for updating main server

def oldcode():
    PID = getPID()
    sts = getPIDStats(PID)
    for e in sts:
        print(e)

def MAINLOOP():
    EXIT_STATUS = -1
    while EXIT_STATUS == 1:
        # ========== File Check ================
        # If no local file or remote is newer fetch from remote
        if os.path.isfile(remoteFolder + powerPoint):
            if (not os.path.isfile(localFolder + powerPoint)) or os.path.getmtime(localFolder + powerPoint) <= os.path.getmtime(remoteFolder + powerPoint):
                printF("fetching file")
                fetch_file()
        else:
            printF("Error: remote path invalid")
        # ========== Loop Notifier ================
        # If other notifications were printed re-print looping
        if printCheckForUpdates:
            printF("checking for updates every " + str(updateTimer) + " minutes")
            printCheckForUpdates = False
        time.sleep(updateTimer*60)
    print(f"Main loop finished with exit code: {EXIT_STATUS}")
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432        # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)

    print('Received', repr(data))


# ======================================================================================================================
# =============================== main logic ===========================================================================
# ======================================================================================================================
pid = str(os.getpid())
if os.path.isfile(pidfile):
    print("pid file already exists, exiting")
    time.sleep(cfg.getVal("exit_timer"))
    sys.exit()
else:
    print(f"creating pid file: {pidfile}")
    open(pidfile, 'w').write(pid)
try:
    projectName = cfg.getVal("project_name")
    print(f"Running {projectName}- Client")
    MAINLOOP()
finally:
    print(f"EOF, removing pid file: {pidfile}")
    os.unlink(os.path.join(dir_path, pidfile))
    print(f"exiting")
    time.sleep(cfg.getVal("exit_timer"))












