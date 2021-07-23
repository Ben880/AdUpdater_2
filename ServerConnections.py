import json
import socket
import threading
from SharedAssets import Tools
from SharedAssets.ClientList import ClientList


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

    def send_packet(self, rpc: str, data: str):
        s_packet = {"rpc": rpc, "data": data}
        self.connection.sendall(bytes(json.dumps(s_packet), "utf-8"))
        Tools.format_print(f"sent rpc:{rpc}", self.name)

    def handle_packet(self, packet):
        json_data = json.loads(packet)
        rpc_name = json_data["rpc"]
        rpc_data = json_data["data"]
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
        client_connection.connected=False
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


