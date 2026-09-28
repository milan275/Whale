from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QEvent
from .renderer import make_renderer, open_system


class renderer_window(QMainWindow):

    def __init__(self, path, use_system=False):
        super().__init__()
        self._path = path
        self.minimized = False

        if use_system:
            open_system(path)
            return

        name = Path(path).name
        self.resize(900, 620)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        root = QFrame()
        root.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setCentralWidget(root)

        lay.addWidget(self._build_titlebar(name))

        renderer = make_renderer(path)
        if renderer:
            lay.addWidget(renderer)
        else:
            ph = QLabel("No renderer available for this file type.")
            ph.setAlignment(Qt.AlignCenter)
            ph.setStyleSheet("color:#555;font-size:13px;background:#121212;")
            lay.addWidget(ph)

        self.show()

    def _build_titlebar(self, name):
        bar = QFrame()
        bar.setFixedHeight(35)
        bar.setStyleSheet("background:#2b2b2b;border-top-left-radius:8px;border-top-right-radius:8px;")
        self._dragging = False

        lay = QHBoxLayout(bar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        close = QLabel("×")
        close.setFixedSize(35, 35)
        close.setAlignment(Qt.AlignCenter)
        close.setStyleSheet("QLabel{background-color:#2b2b2b;color:white;border:None;border-radius:0;border-top-left-radius:8px;font-size:22px;padding-bottom:2px;}QLabel:hover{background-color:red;}")
        close.setCursor(Qt.PointingHandCursor)
        close.mousePressEvent = lambda e: self.close()
        lay.addWidget(close)

        min_btn = QLabel("-")
        min_btn.setFixedSize(35, 35)
        min_btn.setAlignment(Qt.AlignCenter)
        min_btn.setStyleSheet("QLabel{background-color:#2b2b2b;color:white;border:None;border-radius:0;font-size:22px;padding-bottom:3px;}QLabel:hover{background-color:#545454;}")
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.mousePressEvent = lambda e: self.minimize()
        lay.addWidget(min_btn)

        lay.addStretch()

        title = QLabel(name if len(name) <= 50 else name[:48] + "…")
        title.setStyleSheet("color:white;font-size:13px;padding:10px;background:transparent;")
        lay.addWidget(title)

        bar.mousePressEvent = self._bar_press
        bar.mouseMoveEvent = self._bar_move
        bar.mouseReleaseEvent = self._bar_release
        return bar

    def _bar_press(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start = e.globalPosition().toPoint() - self.pos()

    def _bar_move(self, e):
        if self._dragging:
            self.move(e.globalPosition().toPoint() - self._drag_start)

    def _bar_release(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = False

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_start = e.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, e):
        if self._dragging:
            self.move(e.globalPosition().toPoint() - self._drag_start)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._dragging = False

    def minimize(self):
        self.winGeo = self.geometry()
        sg = self.screen().availableGeometry()
        self.cx = self.winGeo.x() + self.winGeo.width() // 2
        self.cy = sg.height()

        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(250)
        anim.setStartValue(self.winGeo)
        anim.setEndValue(QRect(self.cx, self.cy, 0, 0))
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(1)
        fade.setEndValue(0)

        def finish_anim():
            self.showMinimized()
            self.minimized = True

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(anim)
        self.group.addAnimation(fade)
        self.group.finished.connect(finish_anim)
        self.group.start()

    def changeEvent(self, e):
        if e.type() == QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self.minimized:
                self.minimized = False
                self._restore()
        super().changeEvent(e)

    def _restore(self):
        anim = QPropertyAnimation(self, b"geometry")
        anim.setDuration(250)
        anim.setStartValue(QRect(self.cx, self.cy, 0, 0))
        anim.setEndValue(self.winGeo)
        anim.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0)
        fade.setEndValue(1)

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(anim)
        self.group.addAnimation(fade)
        self.group.start()
