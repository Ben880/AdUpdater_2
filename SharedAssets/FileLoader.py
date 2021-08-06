import io
import itertools

from SharedAssets import Tools

module_name = "FileLoader"


class FileLoader:

    def __init__(self, chunk_size: int = 4096):
        self.chunk_size = chunk_size
        self.array = list()

    def load_file(self, file_path):
        self.array = []
        cache = bytearray(self.chunk_size*100)
        f = io.FileIO(file_path)
        for i in itertools.count():
            Tools.format_print(f"Loading large file chunk: {i}", module_name)
            read = f.readinto(cache)
            if not read:
                return
            for i in range(0, 100*self.chunk_size, self.chunk_size):
                self.array.append(bytes(cache[i:i+self.chunk_size]))

    def array_size(self):
        return len(self.array)

    def get_chunk(self, i: int) -> bytes:
        return self.array[i]


