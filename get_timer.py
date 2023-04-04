import cv2
import os
import numpy as np
from easyocr import Reader
from PIL import ImageGrab

path = r"C:\Users\gillian.sanchez\Desktop\times"


def cleanup_text(text):
    # filter out anything except numbers
    return "".join([c if 48 <= ord(c) <= 57 else "" for c in text]).strip()


class Timer:
    def __init__(self):
        lang = ["en"]
        use_gpu = False
        self.reader = Reader(lang_list=lang, gpu=use_gpu, verbose=False)

    def get_timer(self, begin, end):
        x1 = min(begin.x, end.x)
        y1 = min(begin.y, end.y)
        x2 = max(begin.x, end.x)
        y2 = max(begin.y, end.y)

        image = np.array(ImageGrab.grab(bbox=(x1, y1, x2, y2)))
        results = self.reader.readtext(image)

        if not results:
            return None, None

        bbox, text, prob = results[0]
        text = cleanup_text(text)

        if len(text) < 4:
            return None, None

        return int(text[-4:-2]), int(text[-2:])


if __name__ == '__main__':
    timer = Timer()
    for img in os.listdir(path):
        mins, secs = timer.get_timer(os.path.join(path, img))

        print(f"{mins}:{secs}")
