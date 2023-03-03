import sys
import time
from countdown import Countdown
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from threading import Thread, Lock, Event


class Brelshaza:
    def __init__(self, countdown_label, meteor_label, floor_label):
        self.berserk_mins = 20
        self.timer = Countdown(num_mins=self.berserk_mins, label=countdown_label)
        self.timer_label = countdown_label
        self.meteor_label = meteor_label
        self.floor_label = floor_label
        self.timer_thread = None

        self.meteor_thread = None
        self.meteor_stop_flag = Event()
        self.meteor_lock = Lock()
        self.next_meteor_min = 0
        self.next_meteor_sec = 0
        self.next_floor_min = 0
        self.next_floor_sec = 0

    # start the timer in a thread
    def start_timer(self):
        if self.timer_thread is None:
            # clear stop flags to allow threads to run properly
            self.timer.clear_stop_flag()
            self.meteor_stop_flag.clear()

            # create and run the timer and meteor threads that will run in the background
            self.timer_thread = Thread(target=self.timer.start_countdown)
            self.timer_thread.daemon = True

            self.meteor_thread = Thread(target=self.drop_meteor)
            self.meteor_thread.daemon = True

            self.timer_thread.start()
            self.meteor_thread.start()

    # kill the thread running the timer and reset the berserk timer
    def reset_timer(self):
        if self.timer_thread is not None:
            # set the timer and meteor stop flags and wait for the threads to stop
            self.timer.set_stop_flag()
            self.meteor_stop_flag.set()
            self.timer_thread.join()
            self.meteor_thread.join()
            self.timer_thread = None
            self.meteor_thread = None

            # reset all values
            self.timer.reset_timer(self.berserk_mins)
            self.next_meteor_min = 0
            self.next_meteor_sec = 0
            self.next_floor_min = 0
            self.next_floor_sec = 0

            self.timer.set_text()
            self.set_meteor_text(reset=True)
            self.set_floor_text(reset=True)

    # calculate and display the next time meteors will drop (1 minute)
    def drop_meteor(self):
        while True:
            # compare the timer to when next meteor will drop every second
            if self.timer.get_min() * 60 + self.timer.get_sec() <= self.next_meteor_min * 60 + self.next_meteor_sec:
                # use a lock to prevent user input and thread update from interfering with each other
                with self.meteor_lock:
                    self.next_meteor_min = self.timer.get_min() - 1
                    self.next_meteor_sec = self.timer.get_sec()

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
        self.next_floor_min = self.timer.get_min() - 1
        self.next_floor_sec = self.timer.get_sec() - 40

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

    # calculate the time until the next meteor drops
    def set_meteor_time(self):
        # use a lock to prevent user input and thread update from interfering with each other
        with self.meteor_lock:
            self.next_meteor_min = self.timer.get_min() - 1
            self.next_meteor_sec = self.timer.get_sec()
            self.meteor_label.setText(f"<h3>Next meteor drops at: {self.next_meteor_min:02d}:{self.next_meteor_sec:02d}</h3>")

    # re-set the text for the next meteor time
    def set_meteor_text(self, reset=False):
        if reset:
            self.meteor_label.setText("")
        else:
            self.meteor_label.setText(f"<h3>Next meteor drops at: {self.next_meteor_min:02d}:{self.next_meteor_sec:02d}</h3>")

    # re-set the text for next floor time
    def set_floor_text(self, reset=False):
        if reset:
            self.floor_label.setText("")
        else:
            self.floor_label.setText(f"<h3>Floors are restored at: {self.next_floor_min:02d}:{self.next_floor_sec:02d}</h3>")


def main():
    # create the ui window
    app = QApplication([])
    window = QWidget()
    layout = QVBoxLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    window.setWindowTitle("Brelshaza Gate 6 Helper")
    window.setGeometry(100, 100, 300, 100)

    # make the text labels and center-align them
    countdown_label = QLabel("")
    meteor_label = QLabel("")
    floor_label = QLabel("")

    countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    meteor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    floor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # create an object to reference the timer
    boss = Brelshaza(countdown_label=countdown_label, meteor_label=meteor_label, floor_label=floor_label)

    # create the buttons to control the timer
    start_timer = QPushButton("Start")
    start_timer.clicked.connect(boss.start_timer)
    start_timer.setFixedHeight(25)

    reset_timer = QPushButton("Reset")
    reset_timer.clicked.connect(boss.reset_timer)
    reset_timer.setFixedHeight(25)

    # put the timer buttons side by side
    timer_buttons = QWidget()
    timer_buttons_layout = QHBoxLayout(timer_buttons)
    timer_buttons_layout.addWidget(start_timer)
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

    # structure the GUI
    layout.addWidget(timer_buttons)
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
