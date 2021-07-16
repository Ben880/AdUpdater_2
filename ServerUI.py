import tkinter as tk
from ServerConnections import ClientConnection
from SharedAssets import Tools
from SharedAssets.ClientList import ClientList


class ClientGroup:

    def __init__(self, window, client_connection: ClientConnection):
        self.client_connection = client_connection
        self.label_frame = tk.LabelFrame(window, text=client_connection.name)
        self.button = tk.Button(self.label_frame, text="send to server", command=lambda: self.handle_click())
        self.button.pack()
        self.label_frame.pack()

    def handle_click(self):
        self.client_connection.send_packet("UIRPC", "test")

    def destroy(self):
        self.button.destroy()
        self.label_frame.destroy()


class UI:

    cui_dict = {}
    client_list = None
    window = None

    def __init__(self, window, client_list):
        self.window = window
        self.client_list = client_list
        self.window.title('Ad Updater')
        greeting = tk.Label(self.window, text="This is a message")
        text = tk.Label(text="")
        greeting.pack()
        text.pack()

    def add_client_group(self, client_connection: ClientConnection):
        self.cui_dict[client_connection.name] = ClientGroup(self.window, client_connection)

    def update(self):
        groups = self.cui_dict.keys()
        clients = self.client_list.get_clients().keys()
        if not len(groups) == len(clients):
            extra_keys = groups - clients
            for item in extra_keys:
                self.cui_dict.pop(str(item))
            extra_clients = clients - groups
            for item in extra_clients:
                Tools.format_print(item, "UI_Thread")
                self.add_client_group(self.client_list.get_clients()[str(item)])


def server_ui_thread(client_list: ClientList):
    window = tk.Tk()
    ui = UI(window, client_list)
    while True:
        ui.update()
        window.update()





