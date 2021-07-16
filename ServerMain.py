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
import os
from ServerConnections import accept_clients
from ServerUI import server_ui_thread as ui_thread
from SharedAssets import Tools
import threading
from SharedAssets.ClientList import ClientList
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
# =============================== main logic ===========================================================================
# ======================================================================================================================
Tools.format_print(f"Running {projectName}:Client")
# start the ui thread
ui = threading.Thread(target=ui_thread, args=(client_list,))
ui.start()
# start the server thread
server = threading.Thread(target=accept_clients, args=(host, port, client_list,))
server.start()
# main loop act as message broker?
MAINLOOP = True
while MAINLOOP:
    pass

