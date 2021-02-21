import cv2
import PySide2
import qimage2ndarray
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from time import time, sleep
from datetime import datetime
from shutil import copyfile
try:
    from .config import *
except ImportError:
    from config import *


class Player(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.th = None
        self.cam_index = None
        self.record = True
        self.time = None

    def resizeEvent(self, event):
        QGroupBox.resizeEvent(self, event)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        if self.th:
            self.th.width = self.width
            self.th.height = self.height
        self.label.setGeometry(2, 1, self.width-2, self.height-2)

    def start_video(self):
        if not self.th and self.cam_index != None:
            self.stime = time()
            self.th = PlayerThread(self, self.width, self.height)
            self.th.record = self.record
            self.th.delay = not self.record
            self.th.changePixmap.connect(self.setImage)
            self.th.cam_index = self.cam_index
            self.th.start()

    def stop_video(self):
        if self.th:
            self.th.exit = True
            if hasattr(self.th, "fcount"):
                cmd = "ffmpeg -y -r {} -i \"{}\" \"{}\"".format(int(self.th.fcount/(
                    time()-self.stime)), PATH_VIDEOS_RLATEST, PATH_VIDEOS_LATEST)
                print(cmd)
                os.system(cmd)
                copyfile(PATH_VIDEOS_LATEST, os.path.join(
                    PATH_VIDEOS, datetime.now().strftime("%m.%d.%Y_%H.%M.%S.avi")))
            self.th = None

    def select_index(self, port):
        if port == "latest":
            self.cam_index = PATH_VIDEOS_LATEST
            self.record = False
        else:
            index = 1
            arr = []
            i = 10
            while i > 0:
                cap = cv2.VideoCapture(index)
                if cap.read()[0]:
                    arr.append(index)
                    cap.release()
                index += 1
                i -= 1
            print(arr)
            arr = arr
            if len(arr) == 0:
                self.cam_index = None
                QMessageBox.critical(self, "Yer İstasyonu Yazılımı",
                                     "Hiçbir video girişi bulunamadı.")
                return
            while not self.cam_index in arr:
                if len(arr) > 1:
                    self.cam_index = int(QInputDialog.getItem(
                        self, "Yer istasyonu yazılımı", "Video giriş indexi: ", list(map(str, arr)), 0, False)[0])
                elif len(arr) == 0:
                    return
                else:
                    self.cam_index = 0

    @ Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))


class PlayerThread(QThread):
    changePixmap = Signal(QImage)

    def __init__(self, parent, width, height):
        QThread.__init__(self, parent)
        self.width = width
        self.height = height
        self.cam_index = -1
        self.exit = False
        self.record = True
        self.out = None

    def start_record(self, width, height):
        if self.record:
            self.fcount = 0
            self.out = cv2.VideoWriter(
                PATH_VIDEOS_RLATEST, cv2.VideoWriter_fourcc(*'XVID'), 25, (width, height))

    def stop_record(self):
        if self.out:
            self.out.release()
            self.out = None

    def write_record(self, data):
        if self.out:
            self.fcount += 1
            self.out.write(data)

    def run(self):
        cap = cv2.VideoCapture(self.cam_index)
        ret = False
        if self.delay:
            delay = 1/cap.get(cv2.CAP_PROP_FPS)
        else:
            delay = 0
        while not ret:
            ret, frame = cap.read()
            width = frame.shape[1]
            height = frame.shape[0]
            sleep(0.01)
        self.start_record(width, height)
        while cap.isOpened() and not self.exit:
            ret, frame = cap.read()
            if ret:
                self.write_record(frame)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                r = qimage2ndarray.array2qimage(rgbImage)
                p = r.scaled(self.width-4, self.height-4,
                             Qt.KeepAspectRatio, Qt.FastTransformation)
                self.changePixmap.emit(p)
                del frame
            sleep(delay)
        self.stop_record()
