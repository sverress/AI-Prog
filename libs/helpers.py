import sys
import time


def print_loader(progress, total, interval):
    bar = (
        "=" * int(progress / interval)
        + ">"
        + " " * (int(total / interval) - int(progress / interval))
    )
    sys.stdout.write(f"\r[{bar}] {int(progress / total * 100)}%")
    sys.stdout.flush()


class Timer:
    def __init__(self, timer_id: str, start=False):
        self.id = timer_id
        self.start_time = None
        self.end_time = None
        if start:
            self.start()

    def __str__(self):
        return f"{self.id}: {self.time()}"

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def time(self):
        return self.end_time - self.start_time


class TimerManager:
    def __init__(self):
        self.timers = []

    def __str__(self):
        output = ""
        for timer in self.timers:
            output += f"{timer.__str__()} \n"
        return output

    def get_timer(self, timer_id: str) -> Timer:
        return [timer for timer in self.timers if timer.id == timer_id][0]

    def start_new_timer(self, timer_id: str):
        self.timers.append(Timer(timer_id, start=True))

    def stop_timer(self, timer_id: str):
        timer = self.get_timer(timer_id)
        timer.stop()
