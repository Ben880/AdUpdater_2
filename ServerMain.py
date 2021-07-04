# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Handles connection with ad clients
# ======================================================================================================================

# ======================================================================================================================
# =============================== imports ==============================================================================
# ======================================================================================================================
import json
import os
import socket
from SharedAssets import Tools
from _thread import *
import threading
from SharedAssets.ClientList import ClientList, ClientInfo
from SharedAssets.Config import Config as Config

# ======================================================================================================================
# =============================== create vars ==========================================================================
# ======================================================================================================================
cwd = os.getcwd()
dir_path = os.path.dirname(os.path.realpath(__file__))
cfg = Config(configFile="servercfg.json", fileDir=os.path.join(dir_path, "Config"))
cfg.load()
# ======================================================================================================================
# =============================== load cfg vars ========================================================================
# ======================================================================================================================
host = cfg.getVal("host")
port = cfg.getVal("port") # Port to listen on (non-privileged ports are > 1023)
projectName = cfg.getVal("project_name")
client_list = ClientList()


# ======================================================================================================================
# =============================== func logic ===========================================================================
# ======================================================================================================================
def client_thread(c):
    name = ""
    try:
        while True:
            # data received from client
            packet = str(c.recv(1024), "utf-8")
            json_data = json.loads(packet)
            rpc_name = json_data["rpc"]
            rpc_data = json_data["data"]
            if rpc_name == "CLOSE_CONNECTION":
                Tools.format_print(f"Closed connection: {rpc_data}", name)
                break
            elif rpc_name == "CONNECT":
                name = rpc_data
                Tools.format_print(f"Client connected", name)
                client_list.add_client(ClientInfo(name, c))

    except ConnectionResetError:
        Tools.format_print(f"ConnectionResetError", name)
    finally:
        client_list.remove_client(c)
        c.close()


# ======================================================================================================================
# =============================== main logic ===========================================================================
# ======================================================================================================================
Tools.format_print(f"Running {projectName}:Client")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
Tools.format_print(f"Socket bound to port: {port}")
s.listen(5)
Tools.format_print(f"Socket is listening on port: {port}")
# start server

while True:
    # establish connection with client
    c, addr = s.accept()
    # lock acquired by client
    Tools.format_print(f"Connected to: {addr[0]}:{addr[1]}")
    # Start a new thread and return its identifier
    start_new_thread(client_thread, (c,))
s.close()

