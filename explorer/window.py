import sys, os, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QEvent
from window import title_bar
from .panel import explorer_pane
from shatter import ShatterEngine


class toggle_switch(QFrame):

    def __init__(self, callback=None):
        super().__init__()
        self._on = False
        self._cb = callback
        self.setFixedHeight(24)
        self.setStyleSheet("background:transparent;")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self._lbl_off = QLabel("Custom")
        self._lbl_off.setStyleSheet("color:#aaa;font-size:11px;background:transparent;")
        lay.addWidget(self._lbl_off)

        self._track = QFrame()
        self._track.setFixedSize(36, 18)
        self._track.setStyleSheet("background:#2a2a2a;border-radius:9px;border:1px solid #444;")
        self._track.setCursor(Qt.PointingHandCursor)
        self._track.mousePressEvent = lambda e: self._toggle()

        self._knob = QFrame(self._track)
        self._knob.setFixedSize(14, 14)
        self._knob.move(2, 2)
        self._knob.setStyleSheet("background:#666;border-radius:7px;border:none;")
        lay.addWidget(self._track)

        self._lbl_on = QLabel("System")
        self._lbl_on.setStyleSheet("color:#444;font-size:11px;background:transparent;")
        lay.addWidget(self._lbl_on)

    def _toggle(self):
        self._on = not self._on
        if self._on:
            self._knob.move(20, 2)
            self._knob.setStyleSheet("background:#aaa;border-radius:7px;border:none;")
            self._lbl_off.setStyleSheet("color:#444;font-size:11px;background:transparent;")
            self._lbl_on.setStyleSheet("color:#aaa;font-size:11px;background:transparent;")
        else:
            self._knob.move(2, 2)
            self._knob.setStyleSheet("background:#666;border-radius:7px;border:none;")
            self._lbl_off.setStyleSheet("color:#aaa;font-size:11px;background:transparent;")
            self._lbl_on.setStyleSheet("color:#444;font-size:11px;background:transparent;")
        if callable(self._cb):
            self._cb(self._on)


def _purge(path):
    try:
        import winshell
        winshell.delete_file(path, no_confirm=True, allow_undo=False, silent=True)
    except Exception:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except Exception:
            pass


class window(QMainWindow):

    def __init__(self, root_path, vault_name="Vault"):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setStyle("Fusion")
        super().__init__()
        self._root = root_path
        self.minimized = False

        self.resize(1000, 680)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        root = QFrame()
        root.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setCentralWidget(root)

        tb = title_bar(parent=self, options=['-','[]','X'],
                       title="Whale Explorer", logo="./icons/logo.png")
        self._toggle = toggle_switch(callback=self._on_toggle)
        self._toggle.setStyleSheet("background:transparent;padding-right:8px;")
        tb.layout.insertWidget(3, self._toggle)
        lay.addWidget(tb)

        self._pane = explorer_pane(root_path)
        lay.addWidget(self._pane)

        self.show()
        self._app.exec()

    def _on_toggle(self, use_system):
        self._pane.set_system_mode(use_system)

    def maximize(self):
        self.geo = [self.geometry(), self.screen().availableGeometry()]
        self.change_state_to("full")

    def normalize(self):
        self.showNormal()
        self.setGeometry(self.geo[1])
        self.change_state_to("normal")

    def change_state_to(self, state="normal"):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.geo[0 if state=="full" else 1])
        self.animation.setEndValue(self.geo[1 if state=="full" else 0])
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.finished.connect(self.showMaximized if state=="full" else self.showNormal)
        self.animation.start()

    def minimize(self):
        self.winGeo = self.geometry()
        screenGeo = self.screen().availableGeometry()
        self.x = self.winGeo.x() + self.winGeo.width() // 2
        self.y = screenGeo.height()
        final = QRect(self.x, self.y, 0, 0)

        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(250)
        animation.setStartValue(self.winGeo)
        animation.setEndValue(final)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(1)
        fade.setEndValue(0)

        def finish_anim():
            self.showMinimized()
            self.minimized = True

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(animation)
        self.group.addAnimation(fade)
        self.group.finished.connect(finish_anim)
        self.group.start()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self.minimized:
                self.minimized = False
                self.restore_anim()
        super().changeEvent(event)

    def restore_anim(self):
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(250)
        animation.setStartValue(QRect(self.x, self.y, 0, 0))
        animation.setEndValue(self.winGeo)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self, b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0)
        fade.setEndValue(1)

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(animation)
        self.group.addAnimation(fade)
        self.group.start()

    def shatter(self):
        def finish():
            self._cleanup()
            self.close()
            self._app.quit()
        ShatterEngine(self, on_finish=finish).start()

    def closeEvent(self, e):
        self._cleanup()
        super().closeEvent(e)
        self._app.quit()

    def _cleanup(self):
        _purge(self._root)
