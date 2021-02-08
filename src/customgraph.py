import PySide2
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from pyqtgraph import PlotWidget, AxisItem, mkPen, setConfigOptions, PlotItem, mkBrush
try:
    from .config import *
except ImportError:
    from config import *


class CustomGraph(QGroupBox):
    def __init__(self, title, *args, **kargs):
        QGroupBox.__init__(self)
        setConfigOptions(antialias=True)
        self.title = title
        self.graph = PlotWidget(self, title=title, *args, **kargs)
        r = self.geometry()
        self.graph.setGeometry(2, 2, r.width()-4-17, r.height()-4)
        self.x = []
        self.y = []
        self.range = [-1, 1]
        self.plotdata = None
        self.update_style()
        QApplication.instance().paletteChanged.connect(self.update_style)

    def resizeEvent(self, e):
        QGroupBox.resizeEvent(self, e)
        r = self.geometry()
        self.graph.setGeometry(2, 2, r.width()-4-17, r.height()-4)

    def plot(self):
        rn = self.range
        x = self.x
        y = self.y
        if not self.plotdata:
            self.plotdata = self.graph.plot(
                x, y, pen=mkPen(color=self.hcolor, width=2))
        while y[-1] > rn[1]:
            rn[1] *= 2
        while y[-1] < rn[0]:
            rn[0] *= 2
        self.graph.plotItem.setRange(
            xRange=(0, (x[-1]//20+1)*20), yRange=rn, disableAutoRange=True)
        self.plotdata.setData(x, y)

    def update_style(self, palette=None):
        palette = palette or self.palette()
        bgcolor = palette.color(self.backgroundRole())
        bcolor = palette.color(QPalette.Base)
        fgcolor = palette.color(QPalette.WindowText)
        self.hcolor = palette.color(QPalette.Active, QPalette.Highlight)
        self.graph.setBackground(bgcolor)
        self.setStyleSheet("background-color:{};".format(bgcolor.name()))
        self.graph.plotItem.vb.setBackgroundColor(bcolor)
        self.graph.setTitle(
            "<span style=\"color:{};font-family:Sans-serif;font-size:7pt\">{}</span>".format(fgcolor.name(), self.title))
        l = self.graph.getAxis("left")
        b = self.graph.getAxis("bottom")
        t = self.graph.getAxis("top")
        r = self.graph.getAxis("right")
        self.graph.showAxis('top')
        self.graph.showAxis('right')
        t.style['showValues'] = False
        r.style['showValues'] = False
        small_font = QFont(small_font_family)
        small_font.setPixelSize(small_font_size)
        l.setTickFont(small_font)
        b.setTickFont(small_font)
        pen = mkPen(fgcolor, width=1)
        l.setTextPen(pen)
        b.setTextPen(pen)
        l.setStyle(tickTextOffset=2)
        b.setStyle(tickTextOffset=0)
        l.setZValue(0)
        b.setZValue(0)
        t.setZValue(0)
        r.setZValue(0)
        l.setPen(pen)
        b.setPen(pen)
        t.setPen(pen)
        r.setPen(pen)
        l.style['tickLength'] = 5
        b.style['tickLength'] = 5
        t.style['tickLength'] = 0
        r.style['tickLength'] = 0
        l.setWidth(18)
        if self.plotdata:
            self.plotdata = None
            self.plot()


if __name__ == "__main__":
    import sys
    import numpy as np

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.timer = QTimer(self)
            self.customgraph = CustomGraph("Sine")
            self.customgraph.setParent(self)
            self.setGeometry(0, 0, 512, 512+256)
            self.customgraph.setGeometry(0, 0, 512, 512+256)
            self.timer.timeout.connect(self.update_widget)
            self.timer.start(1000/60)
            self.time = 0

        def update_widget(self):
            self.time += 1/60
            self.customgraph.x = np.linspace(0, self.time, int(self.time*10)+10)
            self.customgraph.y = np.sin(self.customgraph.x)
            self.customgraph.plot()

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec_()
    sys.exit(r)
