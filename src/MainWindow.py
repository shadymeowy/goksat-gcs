import PySide2
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from datetime import datetime
try:
    from .Nav2D import Nav2D
    from .Navball import Navball
    from .Player import Player
    from .config import *
    from .blend_image import blend_image
    from .GpsMap import GpsMap
    from .CustomGraph import CustomGraph
    from .TelemetryThread import TelemetryThread, available_ports
except ImportError:
    from Nav2D import Nav2D
    from Navball import Navball
    from Player import Player
    from config import *
    from blend_image import blend_image
    from GpsMap import GpsMap
    from CustomGraph import CustomGraph
    from TelemetryThread import TelemetryThread, available_ports


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Göksat 1 Yer İstasyonu Yazılımı")
        self.setWindowIcon(QIcon('assets/icon.ico'))
        self.setGeometry(0, 0, 1366, 768-24)
        self.maximumSize = (1366, 768-24)
        self.minimumSize = (1366, 768-24)
        self.graphs = [None]*(max(map(lambda x: x[2], telemetry.values()))+1)
        for t, p in telemetry.items():
            self.addGraph(t, p)
        self.navball = self.addWidget(Navball(), 570, 543, 795, 767)
        self.player = self.addWidget(Player(), 190, 24, 1175, 542)
        self.nav2d = self.addWidget(Nav2D(), 1175, 119, 1365, 308)
        self.gpsmap = self.addWidget(GpsMap(), 0, 119, 190, 308)
        label = self.addWidget(QLabel(), 15, 32, 175, 112)
        label.setPixmap(QPixmap("assets/goksat.bmp"))
        label.setScaledContents(True)
        self.addText("Takım No: ", "50626", 1165, 24, 1360, 53, 1267, True)
        self.status_text = self.addText(
            "Uydu Statüsü: ", "-", 1165, 55, 1360, 84, 1267, True)
        self.time_text = self.addText(
            "Geçen Süre: ", "-", 1165, 86, 1360, 115, 1267, True)
        self.port_text = self.addWidget(QComboBox(self), 274, 547, 411, 576)
        ports = ["debug", "latest"] + \
            list(map(lambda ps: list(ps)[0], available_ports()))
        self.port_text = self.addCombobox(
            "Port: ", ports, 191, 547, 411, 576, 274, True)
        self.pcount_text = self.addText(
            "Paket Sayısı: ", "-", 191, 581, 411, 610, 274, True)
        self.connect_button = self.addButton(
            "Bağlan", 414, 547, 565, 576, self.toggle_connection)
        self.addButton("Manual Ayrılma", 414, 581, 565, 610, self.send_cmd)
        self.video_text = self.addText(
            "Video Konumu: ", "/home/shady/Other/goksat/final/latest.avi", 799, 547, 1138, 576, 904, alignment=Qt.AlignLeft)
        self.video_stream_button = self.addButton(
            "Başlat", 800, 580, 906, 609, self.video_stream)
        self.progresbar = self.addWidget(QProgressBar(), 922, 579, 1170, 610)
        self.progresbar.setValue(0)
        self.addButton("...", 1141, 547, 1170, 576, self.select_path)
        self.tth = None
        self.setAcceptDrops(True)

    def addWidget(self, item, x1, y1, x2, y2):
        item.setGeometry(x1, y1-24, x2-x1+1, y2-y1+1)
        item.setParent(self)
        return item

    def addGraph(self, name, p):
        graph = self.addWidget(
            CustomGraph(name), 0 + 190*p[0] + 225*(p[0] > 2), 155 + 153*p[1], 190 + 190*p[0] + 225*(p[0] > 2), 308 + 153*p[1])
        self.graphs[p[2]] = graph
        return graph

    def addButton(self, text, x1, y1, x2, y2, callback=None):
        r = self.addWidget(QPushButton(text=text), x1, y1, x2, y2)
        if callback:
            r.clicked.connect(callback)
        return r

    def addText(self, label_text, text, x1, y1, x2, y2, x3, disabled=False, alignment=Qt.AlignCenter):
        ledit = self.addWidget(QLineEdit(), x3, y1, x2, y2)
        ledit.setText(text)
        ledit.setAlignment(alignment)
        ledit.setReadOnly(disabled)
        label = self.addWidget(QLabel(), x1, y1, x3, y2)
        label.setText(label_text)
        label.setAlignment(Qt.AlignRight)
        return ledit

    def addCombobox(self, label_text, items, x1, y1, x2, y2, x3, disabled=False, alignment=Qt.AlignCenter):
        comb = self.addWidget(QComboBox(), x3, y1, x2, y2)
        comb.addItems(items)
        comb.setEditable(True)
        comb.lineEdit().setReadOnly(disabled)
        comb.lineEdit().setAlignment(alignment)
        label = self.addWidget(QLabel(), x1, y1, x3, y2)
        label.setText(label_text)
        label.setAlignment(Qt.AlignRight)
        return comb

    def select_path(self):
        r = QFileDialog.getOpenFileName(
            self, "Video dosyasını aç", None, "Video Files (*.mp4 *.avi *.webm)")
        if r and r[0] != "":
            self.video_text.setText(r[0])

    def toggle_connection(self):
        if not self.tth or self.tth.exit:
            self.pcount = 0
            self.tth = TelemetryThread(self)
            self.tth.changeTelemetry = self.update_ui
            self.player.select_index(self.port_text.currentText())
            if not self.tth.start_at_port(self.port_text.currentText()):
                QMessageBox.critical(
                    self, "Yer İstasyonu Yazılımı", "Seçilen port ile bağlantı kurulamadı")
                self.tth = None
                return
            self.start_date = datetime.today()
            self.connect_button.setText("Durdur")
            self.player.start_video()
        elif self.tth:
            self.tth.stop()
            self.tth = None
            self.player.stop_video()
            self.connect_button.setText("Baglan")

    def cleanup(self):
        if self.tth:
            self.tth.stop()
            self.tth = None
            self.player.stop_video()

    def update_ui(self):
        self.pcount += 1
        r = self.tth.data
        for p in telemetry.values():
            g = self.graphs[p[2]]
            g.x = r[2]
            g.y = r[p[2]]
            g.plot()
        self.pcount_text.setText(str(self.pcount))
        self.navball.setAngle(r[12][-1], r[13][-1], r[14][-1])
        self.nav2d.setAngle(r[12][-1], r[13][-1], r[14][-1])
        self.gpsmap.setLocation(r[8][-1], r[9][-1])
        delta = datetime.now()-self.start_date
        delta = datetime(2000, 1, 1) + delta
        self.time_text.setText(f"{delta.minute:02} : {delta.second:02}")
        self.status_text.setText(status[r[11][-1]])
        if self.tth.perc == 99:
            self.tth.perc = 100
        self.progresbar.setValue(self.tth.perc)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            file_name = url.toLocalFile()
            self.port_text.addItem(file_name)

    def send_cmd(self):
        if self.tth:
            self.tth.cmd = True

    def video_stream(self):
        path = self.video_text.text()
        if os.path.isfile(path):
            if self.tth:
                self.tth.start_stream(path)
            else:
                QMessageBox.critical(
                    self, "Yer İstasyonu Yazılımı", "Bağlantı açık değil!")
        else:
            QMessageBox.critical(self, "Yer İstasyonu Yazılımı",
                                 "Seçilen video dosyası bulunamadı")
