import hashlib
import json
import os
import socket
import threading
import datetime as dt
import tqdm

from SharedAssets import Tools
from SharedAssets.ClientList import ClientList
from SharedAssets.Config import Config


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

    def __init__(self, connection, client_list: ClientList):
        self.connection = connection
        self.client_list = client_list
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.cfg = Config(configFile="servercfg.json", fileDir=os.path.join(self.dir_path, "Config"))
        self.cfg.load()
        self.power_point_dir = os.path.join(self.dir_path, self.cfg.getVal("power_point_dir"))

    def send_show(self, name: str):
        named_dir = os.path.join(self.power_point_dir, name)
        versions_dir = os.path.join(named_dir, "Versions")
        if os.path.isdir(versions_dir):
            filenames = next(os.walk(versions_dir), (None, None, []))[2]  # [] if no file
            largest = (0,"")
            for fname in filenames:
                slp_ex = fname.split(".")
                if slp_ex[1] == "ppsx":
                    spl_t = slp_ex[0].split("-")
                    time = dt.datetime(int(spl_t[0]),int(spl_t[1]),int(spl_t[2]),int(spl_t[3]),int(spl_t[4])).timestamp()
                    if time > largest[0]:
                        largest = (time, fname)
            Tools.format_print(f"Most recent file: {largest[1]}")
            self.send_packet("SEND_SHOW_NAME", largest[1])
            file = os.path.join(versions_dir, largest[1])
            self.send_packet("SEND_SHOW_SIZE", str(os.path.getsize(file)))
            filesize = os.path.getsize(file)
            SEPARATOR = "<SEPARATOR>"
            self.connection.send(f"{file}{SEPARATOR}{filesize}".encode())
            total = 0
            with open(file, "rb") as f:
                while True:
                    # read the bytes from the file
                    bytes_read = f.read(40960)
                    if not bytes_read:
                        # file transmitting is done
                        break
                    # we use sendall to assure transimission in
                    # busy networks
                    self.connection.sendall(bytes_read)
                    total += len(bytes_read)
                    Tools.format_print(f"sent ({total}/{filesize})")


            """file = open(os.path.join(versions_dir, largest[1]))
            f_bytes = file.read(1024)"""
            """buff = bytes()
            file = os.path.join(versions_dir, largest[1])
            
            with open(file, "rb") as f:
                while byte := f.read(1):
                    buff += byte
                    if len(buff) >= 99000:
                        self.connection.sendall(buff)
                        buff = bytes()
            self.send_packet("SEND_SHOW_END", hashlib.md5("filename.exe").hexdigest())"""
            """while f_bytes:
                self.connection.sendall(f_bytes)
                f_bytes = file.read(1024)
            file.close()"""

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


def client_thread(c, client_list: ClientList):
    client_connection = ClientConnection(c, client_list)
    try:
        while True:
            client_connection.update()
    except ConnectionResetError:
        Tools.format_print(f"ConnectionResetError", client_connection.name)
        client_connection.connected = False
    finally:
        client_list.remove_client(client_connection.name)
        c.close()


def accept_clients(host, port, client_list: ClientList):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    Tools.format_print(f"Socket bound to port: {port}")
    s.listen(5)
    Tools.format_print(f"Socket is listening on port: {port}")
    MAINLOOP = True
    # start server
    while MAINLOOP:
        # establish connection with client
        c, addr = s.accept()
        Tools.format_print(f"Connected to: {addr[0]}:{addr[1]}")
        # Start a new thread and return its identifier
        new_thread = threading.Thread(target=client_thread, args=(c, client_list))
        new_thread.start()
    s.close()


