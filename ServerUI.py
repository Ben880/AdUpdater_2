# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# UI for server
# ======================================================================================================================
import os
import threading
import tkinter as tk
from tkinter import ttk
import time

import ServerConnections
from ServerConnections import ClientConnection
from SharedAssets import Tools, FileTools
from SharedAssets.ClientList import ClientList
from SharedAssets.Config import Config
from SharedAssets import ServerSingletons as Singletons


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
        self.label_frame.grid(column=0, row=2, sticky="we")
        # Connected
        self.connected = tk.Label(self.label_frame, anchor="w")
        self.connected.grid(column=0, row=row.same(), columnspan=3, sticky="we")
        # show running
        self.show_running = tk.Label(self.label_frame, anchor="w")
        self.show_running.grid(column=0, row=row.add(), columnspan=3, sticky="we")
        # last  updated
        self.last_updated = tk.Label(self.label_frame)
        self.last_updated.config(text=f"Last Updated: {time.ctime(float(self.client_connection.last_updated))}")
        self.last_updated.grid(column=0, row=row.add(), sticky="w", columnspan=3)
        # show stop/start
        self.btn_start = tk.Button(self.label_frame, text="start show", command=lambda: self.event_start_show())
        self.btn_start.grid(column=0, row=row.add(), sticky="w")
        self.btn_end = tk.Button(self.label_frame, text="end show", command=lambda: self.event_stop_show())
        self.btn_end.grid(column=1, row=row.same(), sticky="w")
        self.btn_check = tk.Button(self.label_frame, text="check status", command=lambda: self.event_check_show())
        self.btn_check.grid(column=2, row=row.same(), sticky="w")
        # send show
        self.btn_check = tk.Button(self.label_frame, text="send show", command=lambda: self.event_send_show())
        self.btn_check.grid(column=0, row=row.add(), sticky="w")
        self.send_progress_label = tk.Label(self.label_frame)
        self.send_progress_label.config(text=f"")
        self.send_progress_label.grid(column=0, row=row.add(), sticky="w", columnspan=3)
        self.send_progress = ttk.Progressbar(self.label_frame, orient="horizontal", length=100, mode='determinate')
        self.send_progress['maximum'] = 100
        self.send_progress.grid(column=0, row=row.add(), columnspan=3)

    def update(self):
        if self.client_connection.connected:
            self.connected.config(text=f"Client Connected", bg="green")
        else:
            self.connected.config(text="Client Disconnected", bg="red")
        if self.client_connection.show_running:
            approximate_time = Tools.approximate_time_difference(self.client_connection.show_start_time)
            self.show_running.config(text=f"Status: Running (for {approximate_time})", bg="green")
        else:
            approximate_time = Tools.approximate_time_difference(self.client_connection.show_stop_time)
            self.show_running.config(text=f"Status: Stopped (for {approximate_time})", bg="red")
        self.send_progress_label.config(text=f"%{self.client_connection.file_send_progress}")
        self.send_progress['value'] = self.client_connection.file_send_progress

    # set grid position
    def set_grid(self, num: int):
        self.label_frame.grid(column=1, row=num+1)

    # this should not be called
    def destroy(self):
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

    def event_send_show(self):
        if self.client_connection.connected:
            show_name = FileTools.get_most_recent(Singletons.power_point_dir, "ppsx")
            show_path = os.path.join(Singletons.power_point_dir, show_name)
            target_method = ServerConnections.ClientConnection.send_file
            new_thread = threading.Thread(target=target_method, args=(self.client_connection,show_path))
            new_thread.start()

# ======================================================================================================================
# =============================== Main UI ==============================================================================
# ======================================================================================================================

# handles main window and client groups

class UI:

    client_groups = {}
    client_list = None
    window = None
    file_cache = None

    def __init__(self, window):
        self.window = window
        self.client_list = Singletons.client_list
        self.window.title('Ad Updater')
        self.window.geometry("300x400")
        self.window.columnconfigure(1, weight=1)
        self.counter = Tools.Counter()
        self.client_list.subscribe_update("UI")
        self.label_frame = tk.LabelFrame(window, text="Server")
        self.label_frame.grid(column=self.counter.add(), row=0, sticky="we")
        self.most_recent_show = tk.Label(self.label_frame, text="No Loaded Show", anchor="w")
        self.most_recent_show.grid(column=0, row=0)

    def add_client_group(self, client_connection: ClientConnection):
        self.client_groups[client_connection.name] = ClientGroup(self.window, client_connection, self)
        self.client_groups[client_connection.name].set_grid(self.counter.add())

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
        self.most_recent_show.config(text=f"Latest show: NotProgramed")


# ======================================================================================================================
# =============================== Thread Function ======================================================================
# ======================================================================================================================

# function to be called to create new thread
def server_ui_thread():
    window = tk.Tk()
    ui = UI(window)
    while True:
        ui.update()
        window.update()





