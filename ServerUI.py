# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# UI for server
# ======================================================================================================================
import tkinter as tk
import time
from ServerConnections import ClientConnection
from SharedAssets import Tools
from SharedAssets.ClientList import ClientList


# ======================================================================================================================
# =============================== Client Group =========================================================================
# ======================================================================================================================

# Creates and handles a group of ui elements for each client
class ClientGroup:

    def __init__(self, window, client_connection: ClientConnection, parent):
        row = Tools.Counter()
        # set vars
        Tools.format_print(f"New client group created for {client_connection.name}", "UI")
        self.parent = parent
        self.client_connection = client_connection
        # label frame
        self.label_frame = tk.LabelFrame(window, text=client_connection.name)
        self.label_frame.grid(column=1, row=2, sticky="we")
        # Connected
        self.connected = tk.Label(self.label_frame)
        self.connected.grid(column=0, row=row.same(), sticky="we")
        # show running
        self.show_running = tk.Label(self.label_frame)
        self.show_running.grid(column=0, row=row.add(), sticky="we")
        # last  updated
        self.last_updated = tk.Label(self.label_frame)
        self.last_updated.config(text=f"Last Updated: {time.ctime(float(self.client_connection.last_updated))}")
        self.last_updated.grid(column=0, row=row.add(), sticky="w")
        # show stop/start
        self.btn_start = tk.Button(self.label_frame, text="start show", command=lambda: self.event_start_show())
        self.btn_start.grid(column=0, row=row.add(), sticky="w")
        self.btn_end = tk.Button(self.label_frame, text="end show", command=lambda: self.event_stop_show())
        self.btn_end.grid(column=1, row=row.same(), sticky="w")
        self.btn_check = tk.Button(self.label_frame, text="check status", command=lambda: self.event_check_show())
        self.btn_check.grid(column=2, row=row.add(), sticky="w")

    def update(self):
        if self.client_connection.connected:
            self.connected.config(text=f"Connected", bg="green")
        else:
            self.connected.config(text="Disconnected", bg="red")
        if self.client_connection.show_running:
            self.show_running.config(text=f"Power point: running", bg="green")
        else:
            self.show_running.config(text="Power point: stopped", bg="red")

    def set_grid(self, num: int):
        self.label_frame.grid(column=1, row=num+1)

    def destroy(self):
        self.button.destroy()
        self.label_frame.destroy()

    # ===========
    # button handlers
    # =============

    def event_start_show(self):
        if self.client_connection.connected:
            self.client_connection.send_packet("START_SHOW", "")

    def event_stop_show(self):
        if self.client_connection.connected:
            self.client_connection.send_packet("STOP_SHOW", "")

    def event_check_show(self):
        if self.client_connection.connected:
            self.client_connection.send_packet("CHECK_SHOW_BASIC", "")


# ======================================================================================================================
# =============================== Main UI ==============================================================================
# ======================================================================================================================

# handles main window and client groups

class UI:

    client_groups = {}
    client_list = None
    window = None

    def __init__(self, window, client_list):
        self.window = window
        self.client_list = client_list
        self.window.title('Ad Updater')
        self.window.geometry("300x400")
        self.window.columnconfigure(1, weight=1)
        greeting = tk.Label(self.window, text="This is a message")
        client_list.subscribe_update("UI")

    def add_client_group(self, client_connection: ClientConnection):
        self.client_groups[client_connection.name] = ClientGroup(self.window, client_connection, self)
        i = 0
        for key in self.client_groups.keys():
            self.client_groups[key].set_grid(i)
            i = 1 + i

    def remove_client_group(self, name: str):
        self.client_groups.pop(name)

    def client_change(self):
        Tools.format_print("Client change, updating list", "UI")
        groups = self.client_groups.keys()
        clients = self.client_list.get_clients().keys()
        extra_clients = clients - groups
        for item in extra_clients:
            Tools.format_print(item, "UI_Thread")
            self.add_client_group(self.client_list.get_clients()[str(item)])

    def update(self):
        for key in self.client_groups.keys():
            self.client_groups[key].update()
        if self.client_list.is_updated("UI"):
            self.client_change()


# ======================================================================================================================
# =============================== Thread Function ======================================================================
# ======================================================================================================================

# function to be called to create new thread
def server_ui_thread(client_list: ClientList):
    window = tk.Tk()
    ui = UI(window, client_list)
    while True:
        ui.update()
        window.update()





