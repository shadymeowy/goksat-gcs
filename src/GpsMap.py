import os
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWebEngineWidgets import *
try:
    from .config import *
except ImportError:
    from config import *


class GpsMap(QGroupBox):
    def __init__(self):
        super().__init__()
        r = self.geometry()
        self.view = QWebEngineView(self)
        self.width = r.width()
        self.height = r.height()
        self.view.setParent(self)
        self.view.setHtml(open(os.path.join(PATH_ASSETS, "map.html"), "r").read())
        self.view.setGeometry(0, 0, self.width, self.height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.view.setGeometry(0, 0, self.width, self.height)

    def setLocation(self, a, b):
        self.view.page().runJavaScript(f"""
            setLocation({b},{a});
        """)


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
