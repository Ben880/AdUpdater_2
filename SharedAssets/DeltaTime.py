import time


class DeltaTime:
    time = 0
    def __init__(self):
        self.time = time.time()

    def get(self):
        new = time.time()
        delta = new - self.time
        self.time = new
        return delta
