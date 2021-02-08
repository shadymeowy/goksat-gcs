import sys
import PySide2
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from pyqtgraph import mkBrush, mkPen
from time import sleep, time
import numpy as np
from math import cos, sin, sqrt


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.map3d = Map3D()
        self.addWidget(self.map3d, 0, 0, 720, 720)
        self.setGeometry(0, 0, 720, 720)
        self.angles = np.zeros(3)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_2d)
        self.timer.start(8)

    def addWidget(self, item, x1, y1, x2, y2):
        item.setGeometry(x1, y1, x2-x1+1, y2-y1+1)
        item.setParent(self)
        return item

    def update_2d(self):
        self.map3d.update()


class Map3D(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.update_style()
        QApplication.instance().paletteChanged.connect(self.update_style)

    def update_style(self, palette=None):
        palette = palette or self.palette()
        self.fg15 = mkPen(
            width=1.5, color=palette.color(QPalette.WindowText))
        self.fg05 = mkPen(
            width=0.5, color=palette.color(QPalette.WindowText))
        self.hg = mkBrush(color=palette.color(
            QPalette.Active, QPalette.Highlight))
        self.bsbr = mkBrush(color=palette.color(QPalette.Base))

    def drawPolygon(self, x, y, pen=Qt.NoPen, brush=Qt.NoBrush):
        poly = QPolygonF()
        for i in range(len(x)):
            poly.append(QPointF(x[i], y[i]))
        self.painter.setPen(self.fg15)
        self.painter.setBrush(self.bsbr)
        self.painter.drawPolygon(poly)

    def paintEvent(self, e):
        super().paintEvent(e)
        self.painter = QPainter(self)
        self.painter.setRenderHint(QPainter.Antialiasing, bool=True)
        self.drawPolygon([0, 10, 10, 0], [0, 0, 10, 10], self.fg15)
        self.painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec_()
    sys.exit(r)
