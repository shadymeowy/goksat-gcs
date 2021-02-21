import io
import PySide2
import serial.tools.list_ports as lsp
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtCore import QThread, QPointF, Signal
from datetime import datetime
from shutil import copyfile
from time import sleep
from serial import Serial

try:
    from .config import *
except ImportError:
    from config import *


class TelemetryThread(QObject):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.rfile = None
        self.exit = False
        self.timer = QTimer(parent)
        self.dt = 1/60

    def start_at_port(self, port):
        self.data = [list() for _ in range(17)]
        self.port = port
        self.streaming = False
        self.cmd = None
        self.perc = 0
        self.stream = None
        if self.port == "debug":
            self.start_loop()
            return True
        elif self.port == "latest":
            self.stream = open(PATH_TELEMETRY_LATEST, "r")
            self.start_loop()
            return True
        else:
            # try:
            self.stream = TelemetrySerial(port)
            self.start_loop()
            return True
            # except:
            #    pass
            try:
                self.stream = open(port, "r")
                self.start_loop()
                return True
            except:
                pass
            return False

    def stop(self):
        if self.stream:
            self.stream.close()
        self.timer.stop()
        f = self.rfile
        self.rfile = None
        self.close_record()
        filename = os.path.join(
            PATH_TELEMETRY, datetime.now().strftime("%m.%d.%Y_%H.%M.%S.csv"))
        copyfile(PATH_TELEMETRY_LATEST, filename)

    def open_record(self):
        if self.port == "debug" or isinstance(self.stream, TelemetrySerial):
            self.rfile = open(PATH_TELEMETRY_LATEST, "w")

    def write_record(self, data):
        if self.rfile:
            self.rfile.write(",".join([str(data[i][-1]) for i in range(17)]))
            self.rfile.write("\n")
            self.rfile.flush()

    def close_record(self):
        if self.rfile:
            self.rfile.close()

    def start_stream(self, path):
        if isinstance(self.stream, TelemetrySerial):
            self.stream.load_file(path)
            self.streaming = True

    def stop_stream(self, path):
        if isinstance(self.stream, TelemetrySerial):
            self.stream.load_file(path)
            self.streaming = False

    def start_loop(self):
        self.open_record()
        self.timer.timeout.connect(self.loop)
        self.timer.start(int(self.dt*1000))
        if self.port == "debug":
            self.count = 0
            self.x, self.y, self.z = 0, 0, 0
            self.time = 0

    def loop(self):
        if self.port == "debug":
            r = self.data
            dt = self.dt
            r[0].append(50626)
            r[1].append(self.count)
            r[2].append(self.time)
            self.count += 1
            self.time += dt
            time = self.time
            r[11].append(1)
            r[15].append(3)
            r[16].append(0)
            r[12].append(self.x)  # pitch
            r[13].append(self.x)  # roll
            r[14].append(self.x)  # yaw
            self.x += 60*dt
            self.y += 60*dt
            self.z += 60*dt
            self.x %= 360
            self.y %= 360
            self.z %= 360
            for i in range(3, 11):
                r[i].append((((time+i)) % 3-1)*i)
            r[8].append(32.77763183069467+time/2500)
            r[9].append(39.89293236532307+time/2500)
            self.write_record(r)
            self.changeTelemetry()
        elif isinstance(self.stream, TelemetrySerial):
            ser = self.ser
            r = self.data
            data = ser.readline()
            if data:
                data = data[:-2].decode().split(",")
                print(data)
                if len(data) == 17:
                    for i in range(17):
                        r[i].append(num(data[i]))
                    self.write_record(r)
                    self.changeTelemetry()
            if self.cmd:
                ser.cmd = self.cmd
                self.cmd = None
            if self.streaming:
                for _ in range(3):
                    ser.stream()
                self.perc = ser.perc
            ser.manual_trigger()
        else:
            ser = self.stream
            r = self.data
            data = ser.readline().split(",")
            if data[0] == "":
                ser.close()
                self.timer.stop()
                return
            for i in range(17):
                r[i].append(num(data[i]))
            self.write_record(r)
            self.changeTelemetry()


class TelemetrySerial():
    def __init__(self, port):
        self.port = port
        self.ser = Serial(port, 115200, timeout=1)
        self.cmd = None
        self.buf = bytearray()
        self.i = 0
        self.perc = 0
        self.skip = False
        sleep(5)

    def load_file(self, path):
        print("Loading file")
        with open(path, "rb") as f:
            data = f.read()
        hsh = 0
        for c in memoryview(data):
            hsh ^= c
        print("File is loaded. hash = {} len = {}".format(hsh, len(data)))
        self.data = memoryview(data.replace(b"a", b"aa")+b"ac")

    def close(self):
        self.ser.close()
        self.ser = None

    def set_command(self, cmd):
        self.cmd = cmd

    def stream(self, num=1024):
        ser = self.ser
        chunk = self.data[self.i:self.i+min(num, len(self.data))]
        r = False
        if len(chunk) > 0:
            self.i += ser.write(chunk)
            self.perc = (self.i/len(self.data))*100
            r = True
            self.skip = chunk[-1] == 97
        else:
            self.skip = False
        if self.cmd != None and not self.skip:
            ser.write(b"a\n")
            ser.flush()
            self.cmd = None
        return r

    def manual_trigger(self):
        ser = self.ser
        if self.cmd != None and not self.skip:
            ser.write(b"a\n")
            ser.flush()
            self.cmd = None

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.ser.in_waiting))
            data = self.ser.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)
                return None

    def readlines(self):
        r = []
        while line := self.readline():
            r.append(line)
        return r


def available_ports():
    return lsp.comports()


def num(s):
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        return 0
