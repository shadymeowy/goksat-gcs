import os
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
try:
    from .config import *
except ImportError:
    from config import *


class GpsMap(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()

    def resizeEvent(self, event):
        QGroupBox.resizeEvent(self, event)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()

    def setLocation(self, a, b):
        pass


if __name__ == "__main__":
    import sys
    import numpy as np

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.timer = QTimer(self)
            self.gpsmap = GpsMap()
            self.gpsmap.setParent(self)
            self.setGeometry(0, 0, 256, 256)
            self.gpsmap.setGeometry(0, 0, 256, 256)
            self.timer.timeout.connect(self.update_widget)
            self.timer.start(32)
            self.data = np.array([32.77763183069467, 39.89293236532307])

        def update_widget(self):
            self.data += .0001
            self.gpsmap.setLocation(*self.data)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec_()
    sys.exit(r)
