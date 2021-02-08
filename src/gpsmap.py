import os
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWebEngineWidgets import *
try:
    from .config import *
    from .blend_image import blend_image
except ImportError:
    from config import *
    from blend_image import blend_image


class GpsMap(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.web = QWebEngineView(self)
        self.web.setHtml(open("assets/map.html", "r").read())
        print(open("assets/map.html", "r").read())
        self.web.setGeometry(2, 2, self.width-4, self.height-4)
        self.web.loadFinished.connect(self.mask_image)
        self.web.setAttribute(Qt.WA_DontShowOnScreen)
        self.cursor = QLabel(self)
        self.cursor.setGeometry(2, 2, r.width()-4, r.height()-4)
        self.cursor.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        QApplication.instance().paletteChanged.connect(self.mask_image)

    def mask_image(self, e=None):
        size = self.web.contentsRect()
        img = QPixmap(size.width(), size.height())
        self.web.render(img)
        img.save(os.path.join(PATH_ASSETS, "map.png"))
        self.cursor.setPixmap(
            QPixmap(blend_image("map.png", self.palette().color(QPalette.Background), reverse=True, p=2)))

    def resizeEvent(self, event):
        QGroupBox.resizeEvent(self, event)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.web.setGeometry(2, 2, self.width-4, self.height-4)
        self.cursor.setGeometry(2, 2, self.width-4, self.height-4)

    def setLocation(self, a, b):
        self.web.page().runJavaScript(f'window.setLocation({a},{b})')
        self.mask_image()


if __name__ == "__main__":
    import sys
    import numpy as np

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.timer = QTimer(self)
            self.navball = GpsMap()
            self.navball.setParent(self)
            self.setGeometry(0, 0, 256, 256)
            self.navball.setGeometry(0, 0, 256, 256)
            self.navball.web.loadFinished.connect(
                lambda: self.timer.timeout.connect(self.update_widget))
            self.timer.start(32)
            self.data = np.array([32.77763183069467, 39.89293236532307])

        def update_widget(self):
            self.data += .0001
            self.navball.setLocation(*self.data)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec_()
    sys.exit(r)
