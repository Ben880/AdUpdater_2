# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Handles connections to clients
# ======================================================================================================================
import json
import os
import socket
import threading

from SharedAssets import Tools
from SharedAssets.ClientList import ClientList
from SharedAssets.Config import Config
from SharedAssets.FileLoader import FileLoader
from SharedAssets import ServerSingletons as Singletons

SEPARATOR = "<SEPARATOR>"


class ClientConnection:

    # client info
    name = "un-def"
    # connection info
    connected = True
    last_contact = ""
    # show info
    last_updated = "NA"
    show_start_time = ""
    show_stop_time = ""
    show_running = False
    file_send_progress = 0

    def __init__(self, connection):
        self.connection = connection
        self.client_list = Singletons.client_list
        self.power_point_dir = Singletons.power_point_dir
        self.file_loader = FileLoader()

    def send_file(self, file_path):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        self.send_packet("SEND_SHOW_NAME", file_name)
        self.send_packet("SEND_SHOW_SIZE", str(file_size))
        self.connection.send(f"{file_name}{SEPARATOR}{file_size}".encode())
        self.file_loader.load_file(file_path)
        total_chunks = self.file_loader.array_size()
        for i in range(total_chunks):
            self.connection.sendall(self.file_loader.get_chunk(i))
            #Tools.format_print(f"Sending chunk ({i}/{total_chunks})", self.name)
            self.file_send_progress = int(i/total_chunks*100)


    def send_packet(self, rpc: str, data: str):
        s_packet = {"rpc": rpc, "data": data}
        self.connection.sendall(bytes(json.dumps(s_packet), "utf-8"))
        Tools.format_print(f"sent rpc:{rpc}", self.name)

    def handle_packet(self, packet):
        try:
            json_data = json.loads(packet)
            rpc_name = json_data["rpc"]
            rpc_data = json_data["data"]
        except:
            rpc_name = ""
            rpc_data = ""
        if rpc_name == "CLOSE_CONNECTION":
            Tools.format_print(f"Closed connection: {rpc_data}", self.name)
            self.connected = False
            return False
        elif rpc_name == "CONNECT":
            Tools.format_print(f"Client connected", rpc_data)
            self.name = rpc_data
            self.client_list.add_client(self)
            self.send_packet("CHECK_VERSION", "null")
        elif rpc_name == "CURRENT_VERSION":
            self.last_updated = rpc_data
        elif rpc_name == "START_SHOW_TIME":
            self.show_start_time = rpc_data
            self.show_running = True
        elif rpc_name == "STOP_SHOW_TIME":
            self.show_stop_time = rpc_data
            self.show_running = False
        elif rpc_name == "CHECK_SHOW_BASIC_RESPONSE":
            self.show_running = rpc_data == "True"

    def update(self):
        packet = str(self.connection.recv(1024), "utf-8")
        self.handle_packet(packet)


def __client_thread(connection):
    client_connection = ClientConnection(connection)
    try:
        while True:
            client_connection.update()
    except ConnectionResetError:
        Tools.format_print(f"ConnectionResetError", client_connection.name)
        client_connection.connected = False
    finally:
        Singletons.client_list.remove_client(client_connection.name)
        connection.close()


def accept_clients(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    Tools.format_print(f"Socket is listening on port: {port}")
    MAINLOOP = True
    while MAINLOOP:
        connection, addr = s.accept()
        Tools.format_print(f"Connected to: {addr[0]}:{addr[1]}")
        new_thread = threading.Thread(target=__client_thread, args=(connection,))
        new_thread.start()
    s.close()


