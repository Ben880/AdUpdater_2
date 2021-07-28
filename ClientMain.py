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
import hashlib
import json
import socket
import psutil
import subprocess
import os.path
import time
from SharedAssets import Tools
import os
import sys
from SharedAssets.Config import Config as Config
# ======================================================================================================================
# =============================== create vars ==========================================================================
# ======================================================================================================================
cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
pid = str(os.getpid())
# ======================================================================================================================
# =============================== load cfg vars ========================================================================
# ======================================================================================================================
cfg = Config(configFile="clientcfg.json", fileDir=os.path.join(dir_path, "Config"))
cfg.load()
projectName = cfg.getVal("project_name")
powerPoint = cfg.getVal("power_point")
shortcutFile = cfg.getVal("power_point_shortcut")
verificationFile = cfg.getVal("verification_file")
printKeepAlive = cfg.getVal("print_keep_alive")
updateTimer = cfg.getVal("update_timer")
process_name = cfg.getVal("process_name")
localPowerpoints = os.path.join(cwd, cfg.getVal("local_powerpoints"))
path_to_powerpoint = os.path.join(cwd, cfg.getVal("local_powerpoints"), powerPoint)
pidFile = cfg.getVal("pid_file")
respect_pid = cfg.getVal("respect_pid")
client_name = cfg.getVal("client_name")

file_name_buffer = ""
file_data_buffer = bytes()
file_checksum_buffer = ""
file_size_buffer = 0
packet_is_bytes = False
# ======================================================================================================================
# =============================== functions ============================================================================
# ======================================================================================================================

# get all pid with target_name
def get_pids_with_name(target_name):
    pid = list()
    for proc in psutil.process_iter():
        if target_name in proc.name():
            pid.append(proc.pid)
    return pid


# get stats of all pid from a list that is passed in
def get_pid_stats(pid_list: list):
    stats = list()
    for i in pid_list:
        p = psutil.Process(i)
        s = p.status()
        stats.append((i, s))
    return stats


# stop found processes with name of target_name
def stop_shows(target_name):
    pids = get_pids_with_name(target_name)
    if len(pids) > 0:
        Tools.format_print(f"found {len(pids)} power points to end")
    else:
        Tools.format_print("No power point process exists to end")
    for p in pids:
        Tools.format_print(f"Ending power point with PID:{p}")
        subprocess.call(f'taskkill /PID {p} /f', shell=True)


def delete_powerpoint():
    if os.path.isfile(localPowerpoints + powerPoint):
        Tools.format_print("Removing old power point")
        while os.path.isfile(localPowerpoints + powerPoint):
            try:
                os.remove(localPowerpoints + powerPoint)
            except PermissionError:
                Tools.format_print("Cannot remove old file, trying again in 50ms.")
                time.sleep(.005)
    else:
        Tools.format_print(f"No such file {powerPoint}")


def fetch_file():
    Tools.format_print("Fetching new power point")
    stop_shows(process_name)
    delete_powerpoint()
    # grab remote file and start power point then verify update
    # TODO: grab remote file
    start_show()
    Tools.format_print("Fetch file complete")


# start the power point if it exists
def start_show():
    Tools.format_print("Starting the power point")
    power_point_dir = os.path.join(localPowerpoints, powerPoint)
    if os.path.isfile(power_point_dir):
        os.system(f'cmd /c "start {power_point_dir}"')
    else:
        Tools.format_print("No show to start")


# send a packet to the server
def send_packet(server, rpc: str, data: str):
    packet = {"rpc": rpc, "data": data}
    server.sendall(bytes(json.dumps(packet), "utf-8"))
    Tools.format_print(f"sent rpc: {rpc}")


# decode packet
def decode_packet(packet, server):
    global file_name_buffer, file_data_buffer, file_checksum_buffer, file_size_buffer, packet_is_bytes
    if not packet_is_bytes:
        handle_packet(packet, server)
    else:
        """Tools.format_print(f"Receiving show data {len(file_data_buffer)}/{file_size_buffer}")
        file_data_buffer += packet
        if len(file_data_buffer) == file_size_buffer:
            packet_is_bytes = False"""

def handle_file(server):
    global packet_is_bytes
    Tools.format_print("Handling file")
    packet = server.recv(4096).decode()
    Tools.format_print("Receiving packet file")
    filename, filesize = packet.split("<SEPARATOR>")
    filename = os.path.basename(filename)
    filesize = int(filesize)
    Tools.format_print("Opening file")
    total = 0
    with open(filename, 'wb') as f:
        while packet_is_bytes:
            if total == filesize:
                break
            bytes_read = server.recv(40960)
            if not bytes_read:
                packet_is_bytes = False
            # write to the file the bytes we just received
            f.write(bytes_read)
            total += len(bytes_read)
            Tools.format_print(f"recieved ({total}/{filesize})")
    packet_is_bytes = False

# handle an incoming packet
def handle_packet(byte_packet, server):
    global file_name_buffer, file_data_buffer, file_checksum_buffer, file_size_buffer, packet_is_bytes
    packet = str(byte_packet, "utf-8")
    json_data = json.loads(packet)
    rpc_name = json_data["rpc"]
    rpc_data = json_data["data"]
    Tools.format_print(f"Received rpc: {rpc_name}")
    if rpc_name == "CHECK_VERSION":
        ptime = os.path.getmtime(path_to_powerpoint)
        send_packet(server, "CURRENT_VERSION", str(ptime))
    if rpc_name == "START_SHOW":
        start_show()
        stime = time.time()
        send_packet(server, "START_SHOW_TIME", str(stime))
    if rpc_name == "STOP_SHOW":
        stop_shows(process_name)
        stime = time.time()
        send_packet(server, "STOP_SHOW_TIME", str(stime))
    if rpc_name == "CHECK_SHOW_BASIC":
        shows = get_pids_with_name(process_name)
        data = len(get_pid_stats(shows)) > 0
        send_packet(server, "CHECK_SHOW_BASIC_RESPONSE", str(data))
    if rpc_name == "SEND_SHOW_NAME":
        file_name_buffer = rpc_data
    if rpc_name == "SEND_SHOW_SIZE":
        file_size_buffer = rpc_data
        packet_is_bytes = True
        Tools.format_print("Switching to byte mode")
    if rpc_name == "SEND_SHOW_END":
        file_checksum_buffer = rpc_data
        new_file_dir = os.path.join(localPowerpoints, file_name_buffer)
        with open(new_file_dir, 'wb') as f:
            f.write(file_data_buffer)
        f.close()
        if hashlib.md5(new_file_dir).hexdigest() == file_checksum_buffer:
            Tools.format_print("File checksum matches")
        else:
            Tools.format_print("File checksum does not match")



# ======================================================================================================================
# =============================== Main Loop ============================================================================
# ======================================================================================================================

def main_loop():
    if Tools.is_dir_mk(localPowerpoints):
        if not os.path.isfile(localPowerpoints + powerPoint):
            Tools.format_print("Power point does not exist")
    EXIT_STATUS = 1
    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((HOST, PORT))
    send_packet(server, "CONNECT", client_name)
    while EXIT_STATUS == 1:
        if packet_is_bytes:
            handle_file(server)
        else:
            packet = server.recv(1024)
            handle_packet(packet, server)
    Tools.format_print(f"Main loop finished with exit code: {EXIT_STATUS}")
    send_packet(server, "CLOSE_CONNECTION", client_name)
    server.close()


# ======================================================================================================================
# =============================== main logic ===========================================================================
# ======================================================================================================================
if len(sys.argv[1:]) > 0:
    client_name = sys.argv[1:][0]
# if pid file exists print and close
if respect_pid and os.path.isfile(pidFile):
    Tools.format_print("pid file already exists, exiting")
    time.sleep(cfg.getVal("exit_timer"))
    sys.exit()
# else create pid and write pid
else:
    Tools.format_print(f"creating pid file: {pidFile}")
    open(pidFile, 'w').write(pid)
# try main loop and finally remove pid file
try:
    Tools.format_print(f"Running {projectName}:Client")
    main_loop()
finally:
    Tools.format_print("Exiting")
    Tools.format_print(f"Removing pid file: {pidFile}")
    os.unlink(os.path.join(dir_path, pidFile))
    time.sleep(cfg.getVal("exit_timer"))
