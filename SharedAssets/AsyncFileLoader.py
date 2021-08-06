# ======================================================================================================================
# By: Benjamin Wilcox (bwilcox@ltu.edu),
# AdUpdater_2- 6/2/2021
# ======================================================================================================================
# Description:
# Load files in another thread
# ======================================================================================================================
import math
import os
import threading
from typing import BinaryIO
from SharedAssets import Tools

module_name = "AsyncFileLoader"


class AsyncFileLoader:
    """Load binary file to memory in another thread

    Attributes:
        file -- TextIOWrapper opened file
        chunk_size -- size in bytes of each chunk default 4096
    """

    lock = threading.Lock()
    buffer = None
    thread = None
    file = None
    total_chunks = 0
    __load_next = False
    __last_returned_chunk = 0

    def __init__(self, chunk_size: int = 4096):
        self.counter = Tools.Counter()
        self.chunk_size = chunk_size
        self.thread = threading.Thread(target=self.__load_thread())
        self.thread.start()

    def set_file(self, file: BinaryIO):
        self.file = file
        self.total_chunks = math.ceil(os.path.getsize(self.file.name) / self.chunk_size)

    def start_load(self):
        self.__load_next = True
        return

    def __load_thread(self):
        while True:
            if self.__load_next:
                self.__load_next = False
                with self.lock:
                    self.buffer = self.file.read(self.chunk_size)
                Tools.format_print(f"Loading chunk {self.counter.add()} of {self.total_chunks}", module_name)

    def result(self):
        Tools.format_print("Get Result", module_name)
        while not self.__last_returned_chunk == self.counter.i:
            pass
        with self.lock:
            return self.buffer

    def get_chunk_pos(self):
        return self.counter.i

    def get_total_chunks(self):
        return self.total_chunks

    def close(self):
        self.file.close()

