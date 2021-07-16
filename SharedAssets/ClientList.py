from threading import Lock



class ClientList:
    client_list = {}
    list_lock = Lock()

    def __init__(self):
        pass

    def add_client(self, client_connection):
        with self.list_lock:
            self.client_list[client_connection.name] = client_connection

    def remove_client(self, client_connection):
        with self.list_lock:
            self.client_list.pop(client_connection.name)

    def get_clients(self):
        with self.list_lock:
            client_list = self.client_list
        return client_list

    def get_client(self, name: str):
        with self.list_lock:
            client = self.client_list[name]
        return client




