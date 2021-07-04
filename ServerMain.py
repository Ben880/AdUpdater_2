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
from SharedAssets import Tools
import select
import threading
import socketserver

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
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    connect = True

    def setup(self):
        Tools.format_print("ThreadedTCPRequestHandler Started")
        client = ClientInfo("None", self)
        client_list.add_client(client)

    def handle(self):
        while self.connect:
            r,w,e = select.select([self.request],[],[],0.01)
            for rs in r:
                if rs == self.request:
                    packet = str(self.request.recv(1024), "utf-8")
                    json_data = json.loads(packet)
                    rpc_name = json_data["rpc"]
                    rpc_data = json_data["data"]
                    if rpc_name == "CLOSE_CONNECTION":
                        return
                    elif rpc_name == "CONNECT":
                        Tools.format_print(f"Client connected name:{rpc_data}")
                        client_info: ClientInfo = client_list.get_client(self)
                        client_info.set_name(rpc_data)

    def send(self, packet):
        server.sen

    def finish(self):
        Tools.format_print("ThreadedTCPRequestHandler Ended")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


def passtime():
    pass


# ======================================================================================================================
# =============================== main logic ===========================================================================
# ======================================================================================================================
Tools.format_print(f"Running {projectName}:Client")
# Create threaded server
server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
ip, port = server.server_address
server_thread = threading.Thread(target=server.serve_forever)
# start server
server_thread.daemon = True
server_thread.start()
Tools.format_print("Server Started")
while server_thread:
    passtime()

