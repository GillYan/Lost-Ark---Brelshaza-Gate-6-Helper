import time
import sys
from threading import Event


class Countdown:
    def __init__(self, label, num_mins, num_secs=0):
        self.min = num_mins
        self.sec = num_secs
        self.label = label
        self.stop_flag = Event()
        self.set_text()

    # start counting down until it reaches 0 seconds or until the stop_flag has been set
    def start_countdown(self):
        while True:
            if (self.min == 0 and self.sec == -1) or self.stop_flag.is_set():
                sys.exit()

            if self.sec == -1:
                self.sec = 59
                self.min -= 1

            self.set_text()

            time.sleep(1)
            self.sec -= 1

    def reset_timer(self, num):
        self.min = num
        self.sec = 0

    def set_text(self):
        self.label.setText(f"<h1>{self.min:02d}:{self.sec:02d}</h1>")

    def set_stop_flag(self):
        self.stop_flag.set()

    def clear_stop_flag(self):
        self.stop_flag.clear()

    def get_min(self):
        return self.min

    def get_sec(self):
        return self.sec

