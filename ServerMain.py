# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Handles connection with ad clients
# ======================================================================================================================
import time
import threading

from ServerConnections import accept_clients
from ServerUI import server_ui_thread as ui_thread
from SharedAssets import Tools
from SharedAssets import ServerSingletons as Singletons
# ======================================================================================================================
# =============================== load cfg vars ========================================================================
# ======================================================================================================================
host = Singletons.config.getVal("host")
port = Singletons.config.getVal("port")  # Port to listen on (non-privileged ports are > 1023)
projectName = Singletons.config.getVal("project_name")
# ======================================================================================================================
# =============================== main logic ===========================================================================
# ======================================================================================================================
Tools.format_print(f"Running {projectName}: Server")
# start the ui thread
ui = threading.Thread(target=ui_thread, args=())
ui.start()
# start the server thread
server = threading.Thread(target=accept_clients, args=(host, port))
server.start()
# left empty for future use
MAINLOOP = True
while MAINLOOP:
    time.sleep(10)

