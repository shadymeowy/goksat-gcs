import PySide2
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import numpy as np
try:
    from .config import *
    from .blend_image import blend_image
except ImportError:
    from config import *
    from blend_image import blend_image


class Navball(QGroupBox):
    def __init__(self):
        QGroupBox.__init__(self)
        self.glw = NavballGL(self)
        r = self.geometry()
        self.glw.setGeometry(2, 2, r.width()-4, r.height()-4)
        self.cursor = QLabel(self)
        self.cursor.setGeometry(2, 2, r.width()-4, r.height()-4)
        self.cursor.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.update_style()
        QApplication.instance().paletteChanged.connect(self.update_style)

    def update_style(self, palette=None):
        palette = palette or self.palette()
        color = palette.color(QPalette.Highlight)
        self.cursor.setPixmap(QPixmap(blend_image("cursor_mask.png", color)))

    def resizeEvent(self, e):
        QGroupBox.resizeEvent(self, e)
        r = self.geometry()
        self.glw.setGeometry(2, 2, r.width()-4, r.height()-4)
        self.cursor.setGeometry(2, 2, r.width()-4, r.height()-4)

    def setAngle(self, x, y, z):
        self.glw.angle[0] = x
        self.glw.angle[1] = y
        self.glw.angle[2] = z
        self.glw.update()


class NavballGL(QOpenGLWidget):
    def __init__(self, parent):
        QOpenGLWidget.__init__(self, parent)
        r = self.geometry()
        self.width = r.width()
        self.height = r.height()
        self.angle = [0, 0, 0]
        self.update_gl = True
        self.tex = None
        QApplication.instance().paletteChanged.connect(self.update_style)

    def update_style(self):
        self.update_gl = True

    def initializeGL(self):
        glEnable(GL_MULTISAMPLE)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        lightZeroPosition = [10., 4., 10., 1.]
        lightZeroColor = [0.8, 1.0, 0.8, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        glEnable(GL_LIGHT0)

    def paintGL(self):
        if self.update_gl:
            self.update_gl = False
            color = self.palette().color(QPalette.Window)
            glClearColor(color.redF(), color.greenF(), color.blueF(), 1)
            img = Image.open(blend_image("navball_mask.png", color))
            img_data = np.array(list(img.getdata()), np.int8)
            if self.tex:
                glDeleteTextures(1, self.tex)
            self.tex = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.tex)
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
            fmt = GL_RGB if img.mode == "RGB" else GL_RGBA
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
                         fmt, GL_UNSIGNED_BYTE, img_data)
        w, h = self.width, self.height
        glEnable(GL_MULTISAMPLE)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        qobj = gluNewQuadric()
        gluQuadricTexture(qobj, GL_TRUE)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glRotatef(self.angle[2] + 180, 0, 0, 1)
        glRotatef(-self.angle[0], 1, 0, 0)
        glRotatef(self.angle[1], 0, 1, 0)
        gluSphere(qobj, 3.2, 360, 360)
        gluDeleteQuadric(qobj)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def resizeGL(self, w, h):
        self.width = w
        self.height = h
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(40., 1., 1., 40.)
        glMatrixMode(GL_MODELVIEW)
        gluLookAt(0, 0, 10,
                  0, 0, 0,
                  0, 1, 0)
        glPushMatrix()


if __name__ == "__main__":
    import sys

    class MainWindow(QMainWindow):
        def __init__(self, parent=None):
            super(MainWindow, self).__init__(parent)
            self.timer = QTimer(self)
            self.navball = Navball()
            self.navball.setParent(self)
            self.setGeometry(0, 0, 256, 256)
            self.navball.setGeometry(0, 0, 256, 256)
            self.timer.timeout.connect(self.update_widget)
            self.timer.start(1000/60)
            self.data = np.zeros(3)

        def update_widget(self):
            self.data += 1
            self.navball.setAngle(*self.data)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    r = app.exec_()
    sys.exit(r)
