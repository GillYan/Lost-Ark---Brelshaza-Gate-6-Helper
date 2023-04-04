import sys
import time
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from threading import Thread, Lock, Event
from functools import partial
from pynput import mouse
from collections import namedtuple
import get_timer

Point = namedtuple("Point", ["x", "y"])
timer = get_timer.Timer()
begin = None
end = None


class Brelshaza:
    def __init__(self, countdown_label, meteor_label, floor_label):
        self.total_mins = 20
        self.timer_label = countdown_label
        self.meteor_label = meteor_label
        self.floor_label = floor_label

        self.meteor_thread = None
        self.meteor_stop_flag = Event()
        self.meteor_lock = Lock()

        self.next_meteor_min = 0
        self.next_meteor_sec = 0
        self.next_floor_min = 0
        self.next_floor_sec = 0
        self.reset_timer()
        self.set_meteor_text(reset=True)
        self.set_floor_text(reset=True)

    # start the timer in a thread
    def check_timer(self):
        mins, secs, success = get_current_time(max_mins=self.total_mins)
        if success == -1:
            self.timer_label.setText("<h1>Failed to detect</h1>")
            return
        elif success == 0:
            snip_area(self.check_timer, max_mins=self.total_mins)
            mins, secs, success = get_current_time(max_mins=self.total_mins)

        prev = self.timer_label.text()
        if prev != "<h1>Failed to detect</h1>":
            if mins * 60 + secs <= int(prev[4:6]) * 60 + int(prev[7:9]):
                self.timer_label.setText(f"<h1>{mins:02d}:{secs:02d}</h1>")
        else:
            self.timer_label.setText(f"<h1>{mins:02d}:{secs:02d}</h1>")

    # kill the thread running the timer and reset the berserk timer
    def reset_timer(self):
        if self.meteor_thread is not None:
            # set the timer and meteor stop flags and wait for the threads to stop
            self.meteor_stop_flag.set()
            self.meteor_thread.join()
            self.meteor_thread = None

        # reset all values
        self.next_meteor_min = 0
        self.next_meteor_sec = 0
        self.next_floor_min = 0
        self.next_floor_sec = 0

        self.set_meteor_text(reset=True)
        self.set_floor_text(reset=True)
        self.timer_label.setText(f"<h1>{self.total_mins:02d}:{0:02d}</h1>")

    # calculate and display the next time meteors will drop (1 minute)
    def drop_meteor(self):
        while True:
            self.check_timer()
            # compare the timer to when next meteor will drop every second
            mins, secs, success = get_current_time(max_mins=self.next_meteor_min)

            if success == 1 and mins * 60 + secs <= self.next_meteor_min * 60 + self.next_meteor_sec:
                # use a lock to prevent user input and thread update from interfering with each other
                with self.meteor_lock:
                    self.next_meteor_min -= 1

                    # automatically stop the thread once the timer reaches 0
                    if self.next_meteor_min < 0:
                        self.next_meteor_min = 0
                        self.next_meteor_sec = 0
                        self.meteor_stop_flag.set()

                    self.set_meteor_text()
            elif self.meteor_stop_flag.is_set():
                sys.exit()

            time.sleep(1)

    # calculate and display the time when floors will be restored (1 minute 40 seconds)
    def break_floor(self):
        self.check_timer()

        mins, secs, success = get_current_time()

        if success != 1:
            return

        self.next_floor_min = mins - 1
        self.next_floor_sec = secs - 40

        if self.next_floor_sec < 0:
            self.next_floor_min -= 1
            self.next_floor_sec += 60

        if self.next_floor_min < 0:
            self.next_floor_min = 0
            self.next_floor_sec = 0

        self.set_floor_text()

    # drop a yellow meteor, which resets the meteor timer and breaks the floor
    def drop_yellow_meteor(self):
        self.set_meteor_time()
        self.break_floor()

        # clear meteor flag
        if self.meteor_stop_flag.is_set():
            self.meteor_stop_flag.clear()

        # start automatic meteor timer if not active
        if self.meteor_thread is None:
            self.meteor_thread = Thread(target=self.drop_meteor)
            self.meteor_thread.daemon = True
            self.meteor_thread.start()

    # calculate the time until the next meteor drops
    def set_meteor_time(self):
        # use a lock to prevent user input and thread update from interfering with each other
        with self.meteor_lock:
            mins, secs, success = get_current_time()
            if success == 1:
                self.next_meteor_min = mins - 1
                self.next_meteor_sec = secs
                self.set_meteor_text()

    # re-set the text for the next meteor time
    def set_meteor_text(self, reset=False):
        if reset:
            self.meteor_label.setText("<h3></h3>")
        else:
            self.meteor_label.setText(f"<h3>Next meteor drops at: {self.next_meteor_min:02d}:{self.next_meteor_sec:02d}</h3>")

    # re-set the text for next floor time
    def set_floor_text(self, reset=False):
        if reset:
            self.floor_label.setText("<h3></h3>")
        else:
            self.floor_label.setText(f"<h3>Floors are restored at: {self.next_floor_min:02d}:{self.next_floor_sec:02d}</h3>")


def get_current_time(max_mins=None, verbose=False):
    # check if any coordinates are saved
    if begin is None or end is None:
        if verbose:
            print("no coords")
        return None, None, 0

    # get the time and validate
    mins, secs = timer.get_timer(begin, end)
    if mins is None or secs is None or (max_mins is not None and mins > max_mins):
        if verbose:
            print("failed to get time")
        return None, None, -1
    return mins, secs, 1


def snip_area(check, max_mins=None):
    global begin
    global end

    begin = None
    end = None
    success = 0

    def on_click(x, y, button, pressed):
        btn = button.name

        if btn == "right" and pressed:
            global begin
            begin = Point(x=x, y=y)
        elif btn == "right" and not pressed:
            global end
            end = Point(x=x, y=y)
            listener.stop()

    while success != 1:
        listener = mouse.Listener(on_click=on_click)
        listener.start()
        listener.join()

        _, _, success = get_current_time(max_mins=max_mins)

    check()


def main():
    # create the ui window
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    window.setWindowTitle("Brelshaza Gate 6 Helper")
    window.setGeometry(100, 100, 300, 240)
    window.setMinimumWidth(211)
    window.setMaximumSize(300, 240)

    # make the text labels and center-align them
    countdown_label = QLabel("")
    meteor_label = QLabel("")
    floor_label = QLabel("a")

    countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    meteor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    floor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # create an object to reference the timer
    boss = Brelshaza(countdown_label=countdown_label, meteor_label=meteor_label, floor_label=floor_label)

    # create the buttons to control the timer
    check_timer = QPushButton("Check Time")
    check_timer.clicked.connect(boss.check_timer)
    check_timer.setFixedHeight(25)

    reset_timer = QPushButton("Reset")
    reset_timer.clicked.connect(boss.reset_timer)
    reset_timer.setFixedHeight(25)

    # put the timer buttons side by side
    timer_buttons = QWidget()
    timer_buttons_layout = QHBoxLayout(timer_buttons)
    timer_buttons_layout.addWidget(check_timer)
    timer_buttons_layout.addWidget(reset_timer)
    timer_buttons_layout.setContentsMargins(0, 0, 0, 0)

    # create the buttons to calculate new times
    yellow_meteor_button = QPushButton("Yellow Meteor")
    yellow_meteor_button.clicked.connect(boss.drop_yellow_meteor)
    yellow_meteor_button.setFixedHeight(40)

    meteor_button = QPushButton("Drop Meteor")
    meteor_button.clicked.connect(boss.set_meteor_time)
    meteor_button.setFixedHeight(30)

    floor_button = QPushButton("Break Floor")
    floor_button.clicked.connect(boss.break_floor)
    floor_button.setFixedHeight(30)

    # put the drop meteor and break floor buttons side by side
    sub_buttons = QWidget()
    sub_buttons_layout = QHBoxLayout(sub_buttons)
    sub_buttons_layout.addWidget(meteor_button)
    sub_buttons_layout.addWidget(floor_button)
    sub_buttons_layout.setContentsMargins(0, 0, 0, 0)

    # create the buttons to calculate new times
    select_button = QPushButton("Select Area")
    partial_snip = partial(snip_area, boss.check_timer, None)
    select_button.clicked.connect(partial_snip)
    select_button.setFixedHeight(25)


    # structure the GUI
    layout.addWidget(timer_buttons)
    layout.addWidget(select_button)
    layout.addWidget(countdown_label)
    layout.addWidget(meteor_label)
    layout.addWidget(floor_label)
    layout.addWidget(yellow_meteor_button)
    layout.addWidget(sub_buttons)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
