import os.path
import threading
import time

from SharedAssets import Tools
from SharedAssets.AsyncFileLoader import AsyncFileLoader

module_name = "SendShowService"


class SendShowService:

    start_send = False
    file_path = ""
    file_name = ""
    file_size = 0

    def __init__(self, connection):
        self.connection = connection
        self.async_loader = AsyncFileLoader()
        new_thread = threading.Thread(target=self.__send_show_thread())
        new_thread.start()

    def send(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.file_size = os.path.getsize(file_path)
        self.async_loader.set_file(open(file_path, 'rb'))
        self.start_send = True

    def __send_show_thread(self):
        while True:
            time.sleep(1)
            if self.start_send:
                self.start_send = False
                self.connection.send_packet("SEND_SHOW_NAME", self.file_name)
                self.connection.send_packet("SEND_SHOW_SIZE", str(self.file_size))
                SEPARATOR = "<SEPARATOR>"
                self.connection.connection.send(f"{self.file_name}{SEPARATOR}{self.file_size}".encode())
                Tools.format_print("Starting async loader", module_name)
                self.async_loader.start_load()
                loop = True
                Tools.format_print("Getting total chunks", module_name)
                total_chunks = self.async_loader.get_total_chunks()
                Tools.format_print("Starting loop", module_name)
                while loop:
                    bytes_read = self.async_loader.result()
                    self.connection.connection.sendall(bytes_read)
                    current_chunk = self.async_loader.get_chunk_pos()
                    Tools.format_print(f"Sending chunk ({current_chunk}/{total_chunks})", module_name)
                    if total_chunks == current_chunk:
                        loop = False

    def progress(self) -> (int, int):
        return self.async_loader.get_chunk_pos(), self.async_loader.get_total_chunks()