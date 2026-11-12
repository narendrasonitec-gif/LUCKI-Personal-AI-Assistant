import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer, Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QBrush, QPen, QColor, QRadialGradient, QConicalGradient

class AnimatedOrb(QWidget):
    """Animated Lucki core: red/white orbit loops and a gently animated face."""
    def __init__(self):
        super().__init__()
        self.phase = 0.0
        self.active = False
        self.setMinimumSize(300, 260)
        self.setMaximumHeight(360)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.anim)
        self.timer.start(30)

    def anim(self):
        self.phase = (self.phase + 2.2) % 360
        self.update()

    def set_active(self, value):
        self.active = bool(value)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        scale = min(w, h) / 290.0
        r = 66 * scale + (3.5 * scale * math.sin(math.radians(self.phase * 2)))
        # Subtle ground glow
        glow = QRadialGradient(QPointF(cx, cy + 65*scale), 105*scale)
        glow.setColorAt(0.0, QColor(230, 15, 48, 55))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen); p.setBrush(QBrush(glow))
        p.drawEllipse(QRectF(cx-115*scale, cy-60*scale, 230*scale, 230*scale))
        # Animated elliptical orbit rings
        for i, (rx, ry, width, offset) in enumerate([(103, 43, 3.0, 0), (116, 54, 1.4, 115), (92, 35, 1.3, 235)]):
            p.save(); p.translate(cx, cy); p.rotate(self.phase * (1 if i % 2 == 0 else -0.72) + offset)
            pen = QPen(QColor(255, 45 if i != 1 else 255, 72 if i != 1 else 255, 205 if i == 0 else 115), width*scale)
            pen.setCapStyle(Qt.RoundCap); p.setPen(pen); p.setBrush(Qt.NoBrush)
            p.drawEllipse(QRectF(-rx*scale, -ry*scale, 2*rx*scale, 2*ry*scale))
            # Bright moving orbit particle
            a = math.radians((self.phase * (1 if i % 2 == 0 else -0.72) + offset) % 360)
            dot = QPointF(rx*scale*math.cos(a), ry*scale*math.sin(a))
            p.setPen(Qt.NoPen); p.setBrush(QColor(255, 255, 255, 235)); p.drawEllipse(dot, 3.2*scale, 3.2*scale)
            p.restore()
        # Core gradient
        core = QRadialGradient(QPointF(cx-r*.28, cy-r*.35), r*1.8)
        core.setColorAt(0.0, QColor(83, 83, 91)); core.setColorAt(0.42, QColor(22, 22, 27)); core.setColorAt(0.78, QColor(3, 3, 5)); core.setColorAt(1.0, QColor(0, 0, 0))
        p.setPen(QPen(QColor(255, 255, 255, 220), 2.2*scale)); p.setBrush(QBrush(core))
        p.drawEllipse(QPointF(cx, cy), r, r)
        p.setPen(QPen(QColor(255, 26, 61, 235), 5*scale)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r*.76, r*.76)
        # Face plate
        face_r = r*.57
        p.setPen(Qt.NoPen); p.setBrush(QColor(5, 5, 8)); p.drawEllipse(QPointF(cx, cy), face_r, face_r)
        # Blink briefly every cycle; smile subtly changes height for a lively expression.
        phase = self.phase % 180
        blink = phase > 169
        eye_pen = QPen(QColor(255, 255, 255), 3.4*scale, Qt.SolidLine, Qt.RoundCap)
        p.setPen(eye_pen)
        eye_y = cy - 5*scale
        eye_dx = 17*scale
        if blink:
            p.drawLine(QPointF(cx-eye_dx-5*scale, eye_y), QPointF(cx-eye_dx+5*scale, eye_y))
            p.drawLine(QPointF(cx+eye_dx-5*scale, eye_y), QPointF(cx+eye_dx+5*scale, eye_y))
        else:
            eye_h = (7 + 2*math.sin(math.radians(self.phase*3))) * scale
            p.drawArc(QRectF(cx-eye_dx-6*scale, eye_y-eye_h, 12*scale, 2*eye_h), 0, 180*16)
            p.drawArc(QRectF(cx+eye_dx-6*scale, eye_y-eye_h, 12*scale, 2*eye_h), 0, 180*16)
        smile_h = (7 + 2*math.sin(math.radians(self.phase*2))) * scale
        p.setPen(QPen(QColor(255, 48, 78), 2.7*scale, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(QRectF(cx-15*scale, cy+3*scale, 30*scale, smile_h*2), 205*16, 130*16)
        # Small animated audio bars below core
        p.setPen(Qt.NoPen)
        for i in range(17):
            x = cx + (i-8)*5*scale
            bar_h = (2 + (7 if self.active else 4) * abs(math.sin(math.radians(self.phase*3 + i*23))))*scale
            p.setBrush(QColor(255, 35, 65, 180 if i%2 else 240))
            p.drawRoundedRect(QRectF(x-1.1*scale, cy+r+20*scale-bar_h, 2.2*scale, bar_h), scale, scale)
        p.end()
