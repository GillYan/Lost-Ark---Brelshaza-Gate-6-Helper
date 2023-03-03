import sys
import time
from countdown import Countdown
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from threading import Thread, Lock, Event


class Brelshaza:
    def __init__(self, countdown_label, meteor_label, floor_label):
        self.berserk_mins = 20
        self.timer = Countdown(num_mins=self.berserk_mins, num_secs=0, text=countdown_label)
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
            self.timer.stop_flag.clear()
            self.meteor_stop_flag.clear()
            self.timer_thread = Thread(target=self.timer.start_countdown)
            self.timer_thread.daemon = True

            self.meteor_thread = Thread(target=self.drop_meteor)
            self.meteor_thread.daemon = True

            self.timer_thread.start()
            self.meteor_thread.start()

    # kill the thread running the timer and reset the berserk timer
    def reset_timer(self):
        if self.timer_thread is not None:
            self.timer.stop_flag.set()
            self.meteor_stop_flag.set()
            self.timer_thread.join()
            self.meteor_thread.join()
            self.timer_thread = None
            self.meteor_thread = None

            self.timer.min = self.berserk_mins
            self.timer.sec = 0
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
            if self.timer.get_min() * 60 + self.timer.get_sec() <= self.next_meteor_min * 60 + self.next_meteor_sec:
                with self.meteor_lock:
                    self.next_meteor_min = self.timer.get_min() - 1
                    self.next_meteor_sec = self.timer.get_sec()

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

    def set_meteor_time(self):
        with self.meteor_lock:
            self.next_meteor_min = self.timer.get_min() - 1
            self.next_meteor_sec = self.timer.get_sec()
            self.meteor_label.setText(f"<h3>Next meteor drops at: {self.next_meteor_min:02d}:{self.next_meteor_sec:02d}</h3>")

    def set_meteor_text(self, reset=False):
        if reset:
            self.meteor_label.setText("")
        else:
            self.meteor_label.setText(f"<h3>Next meteor drops at: {self.next_meteor_min:02d}:{self.next_meteor_sec:02d}</h3>")

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
    timer_buttons = QWidget()
    timer_buttons_layout = QHBoxLayout(timer_buttons)
    start_timer = QPushButton("Start")
    reset_timer = QPushButton("Reset")
    start_timer.clicked.connect(boss.start_timer)
    reset_timer.clicked.connect(boss.reset_timer)
    start_timer.setFixedHeight(25)
    reset_timer.setFixedHeight(25)
    timer_buttons_layout.addWidget(start_timer)
    timer_buttons_layout.addWidget(reset_timer)

    # create the buttons to calculate new times
    meteor_button = QPushButton("Drop Meteor")
    floor_button = QPushButton("Break Floor")
    meteor_button.clicked.connect(boss.set_meteor_time)
    floor_button.clicked.connect(boss.break_floor)
    meteor_button.setFixedHeight(40)
    floor_button.setFixedHeight(40)

    # structure the GUI
    layout.addWidget(timer_buttons)
    layout.addWidget(countdown_label)
    layout.addWidget(meteor_label)
    layout.addWidget(floor_label)
    layout.addWidget(meteor_button)
    layout.addWidget(floor_button)
    window.setLayout(layout)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
