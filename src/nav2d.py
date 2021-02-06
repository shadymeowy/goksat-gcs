import PySide2
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from pyqtgraph import mkBrush, mkPen
import numpy as np
from math import cos, sin, sqrt


class Nav2D(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        r = self.geometry()
        self.angle = [0, 0, 0]
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

    def setAngle(self, x, y, z):
        self.angle[0] = x
        self.angle[1] = z
        self.angle[2] = y
        self.update()

    def paintEvent(self, e):
        QGroupBox.paintEvent(self, e)
        x = self.angle[0]*0.0174532925
        y = self.angle[1]*0.0174532925
        z = self.angle[2]*0.0174532925
        ps = np.array([[-0.7, -1, 0], [0.7, -1, 0], [0.7, 1, 0], [-0.7, 1, 0], [-0.6, -0.5, 0], [0.6, -0.5, 0],
                       [0.6, 0.9, 0], [-0.6, 0.9, 0], [-0.67, -0.6, 0], [0.67, -0.6, 0], [0, -0.7, 0], [0, -0.5, 0]])
        a0 = np.sin(z)*ps[:, 1]+np.cos(z)*ps[:, 0]
        a1 = cos(z)*ps[:, 1]-sin(z)*ps[:, 0]
        ps[:,0] = np.cos(y)*a0
        ps[:,1] = np.sin(x)*np.sin(y)*a0+np.cos(x)*a1
        ps[:,2] = np.cos(x)*np.sin(y)*a0-np.sin(x)*a1
        sq2 = sqrt(2)
        ln = [(0, 1), (1, 2), (2, 3), (3, 0)]
        width = self.geometry().width()
        height = self.geometry().height()
        if width > height:
            wd = (width-height)/2
            hd = 0
            w = height
        else:
            wd = 0
            hd = (height-width)/2
            w = width
        m = 10
        a = (w - 2*m) / (2*sq2)
        A = 0.4
        ps[:,2] = A*(ps[:,2]+1+sq2)-A+1
        ps[:,0] = ((ps[:,0]/ps[:,2]+sq2)*a+m) + wd
        ps[:,1] = ((ps[:,1]/ps[:,2]+sq2)*a+m) + hd
        pn = QPainter(self)
        pn.setRenderHint(QPainter.Antialiasing, bool=True)
        poly = QPolygonF()
        for i in range(0, 4):
            poly.append(QPointF(ps[i][0], ps[i][1]))
        pn.setPen(self.fg15)
        pn.setBrush(self.bsbr)
        pn.drawPolygon(poly)
        poly = QPolygonF()
        for i in range(4, 8):
            poly.append(QPointF(ps[i][0], ps[i][1]))
        pn.setPen(Qt.NoPen)
        pn.setBrush(self.hg)
        pn.drawPolygon(poly)
        poly = QPolygonF()
        for i in range(8, 10):
            poly.append(QPointF(ps[i][0], ps[i][1]))
        pn.setPen(self.fg05)
        pn.setBrush(Qt.NoBrush)
        pn.drawPolygon(poly)
        poly = QPolygonF()
        for i in range(10, 12):
            poly.append(QPointF(ps[i][0], ps[i][1]))
        pn.setPen(self.fg05)
        pn.setBrush(Qt.NoBrush)
        pn.drawPolygon(poly)