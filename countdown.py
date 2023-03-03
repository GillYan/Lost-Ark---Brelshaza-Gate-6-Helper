import time
import sys
from threading import Event


class Countdown:
    def __init__(self, num_mins, num_secs, text):
        self.min = num_mins
        self.sec = num_secs
        self.label = text
        self.stop_flag = Event()
        self.set_text()

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

    def set_text(self):
        self.label.setText(f"<h1>{self.min:02d}:{self.sec:02d}</h1>")

    def get_min(self):
        return self.min

    def get_sec(self):
        return self.sec

