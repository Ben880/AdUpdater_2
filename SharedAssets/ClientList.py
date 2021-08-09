# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Handles a list of clients for use by components
# ======================================================================================================================

from threading import Lock

client_list_singleton = None


class ClientList:
    client_list = {}
    list_lock = Lock()
    update = {}

    def __init__(self):
        pass

    def add_client(self, client_connection):
        with self.list_lock:
            self.client_list[client_connection.name] = client_connection
        self.trigger_update()

    def remove_client(self, name: str):
        self.trigger_update()

    def get_clients(self):
        with self.list_lock:
            client_list = self.client_list
        return client_list

    def get_client(self, name: str):
        with self.list_lock:
            client = self.client_list[name]
        return client

    def trigger_update(self):
        for key in self.update.keys():
            self.update[key] = True

    def subscribe_update(self, name: str):
        with self.list_lock:
            self.update[name] = False

    def is_updated(self, name):
        with self.list_lock:
            res = self.update[name]
            self.update[name] = False
        return res





