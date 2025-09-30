import time


class Timer:
    def __init__(self) -> None:
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def get_time(self):
        time_elapsed = float((self.end_time - self.start_time))
        return time_elapsed

    def reset(self):
        self.end_time = 0
        self.start_time = 0
