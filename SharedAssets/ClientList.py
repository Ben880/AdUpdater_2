from threading import Lock


class ClientInfo:
    name = "none"
    server_thread = None
    lock = Lock()

    def __init__(self, name: str, server_thread):
        self.name = name
        self.server_thread = server_thread

    def set_name(self, name: str):
        self.lock.acquire()
        self.name = name
        self.lock.release()

    def get_name(self):
        self.lock.acquire()
        name = self.name
        self.lock.release()
        return name

    def get_thread(self):
        self.lock.acquire()
        thread = self.server_thread
        self.lock.release()
        return thread

class ClientList:
    client_list = list()
    list_lock = Lock()

    def __init__(self):
        pass

    def add_client(self, client: ClientInfo):
        self.list_lock.acquire()
        self.client_list.append(client)
        self.list_lock.release()

    def remove_client(self, server_thread):
        self.list_lock.acquire()
        for client in self.client_list:
            if client.server_thread == server_thread:
                self.client_list.remove(client)
                self.list_lock.release()
                return
        self.list_lock.release()

    def get_clients(self):
        self.list_lock.acquire()
        list = self.client_list
        self.list_lock.release()
        return list

    def get_client(self, server_thread):
        self.list_lock.acquire()
        for client in self.client_list:
            if client.server_thread == server_thread:
                info = client
        self.list_lock.release()
        return info


