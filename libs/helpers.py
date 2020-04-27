import sys
import time
from datetime import timedelta


def print_loader(progress, total, interval, timer, total_number_of_episodes):
    bar = (
        "=" * int(progress / interval)
        + ">"
        + " " * (int(total / interval) - int(progress / interval))
    )
    remaining_time = print_remaining_time_estimation(
        timer, progress, total_number_of_episodes
    )
    sys.stdout.write(f"\r[{bar}] {int(progress / total * 100)}% {remaining_time}")
    sys.stdout.flush()


def print_remaining_time_estimation(
    timer, current_episode_number, number_of_episodes_to_play
):
    if not timer.end_time:
        return ""
    time_string = Timer.seconds_to_str(
        timer.time() * (number_of_episodes_to_play - current_episode_number)
    )
    return f"Minimum {time_string} remaining"


def random_string(string_length=8):
    import string
    import random

    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for i in range(string_length))


def time_list_from_timedelta_string(timedelta):
    return [int(float(tid)) for tid in timedelta.split(":")]


class Timer:
    def __init__(self, timer_id=None, start=False):
        if timer_id is None:
            self.id = random_string()
        else:
            self.id = timer_id
        self.start_time = None
        self.end_time = None
        if start:
            self.start()
        self.cumulative = 0

    def __str__(self):
        return f"{self.id}: {self.time()}"

    def start(self):
        self.start_time = time.time()

    def stop(self, add=False):
        self.end_time = time.time()
        if add:
            self.cumulative += self.time()

    def time(self):
        return self.end_time - self.start_time

    @staticmethod
    def seconds_to_str(seconds):
        time_tuple = Timer.get_seconds_tuple(seconds)
        output = ""
        time_lables = ["days", "hours", "minutes", "seconds"]
        for index, time_value in enumerate(time_tuple):
            if time_value:
                output += f"{time_value} {time_lables[index] if time_value>1 else time_lables[index][:-1]} "
        return output

    def time_str(self):
        Timer.seconds_to_str(self.time())

    @staticmethod
    def get_seconds_tuple(seconds):
        time_d = timedelta(seconds=seconds)
        if time_d.days == 0:
            return tuple([0] + time_list_from_timedelta_string(str(time_d)))
        else:
            return tuple(
                [time_d.days]
                + time_list_from_timedelta_string(str(time_d).split(",")[-1])
            )

    def get_time_tuple(self):
        return Timer.get_seconds_tuple(self.time())


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
