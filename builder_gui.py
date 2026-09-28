import sys, os
from PySide6.QtWidgets import (QApplication, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QFrame, QProgressBar, QMainWindow)
from PySide6.QtCore import Qt, QThread, Signal, QRect, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QEvent
from window import title_bar
from vault import vault
from shortcut import Shortcut
from shatter import ShatterEngine


class BuildThread(QThread):
    done = Signal(bool, str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            p = self.params
            os.makedirs(os.path.abspath("./vaults"), exist_ok=True)
            v = vault(name=p['name'], password=p['password'], src=p['src'],
                      fake=p['fake'] or './vaults/empty', fake_pass=p['fake_pass'])
            v.create()
            s = Shortcut(target=p['extract_path'], args=f'"{p["name"]}"',
                         name=p['name'], icon=p['icon_path'])
            s.create(dest_folder=p['shortcut_dest'])
            self.done.emit(True, "")
        except Exception as e:
            self.done.emit(False, str(e))


class field_row(QFrame):

    def __init__(self, label, placeholder="", browse=False, browse_mode="folder"):
        super().__init__()
        self.browse_mode = browse_mode
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        lbl = QLabel(label)
        lbl.setFixedWidth(120)
        lbl.setStyleSheet("color:#aaa;font-size:13px;")
        lay.addWidget(lbl)

        self.entry = QLineEdit()
        self.entry.setPlaceholderText(placeholder)
        self.entry.setStyleSheet("QLineEdit{background:#1e1e1e;color:white;border:1px solid #3a3a3a;border-radius:4px;padding:5px 8px;font-size:13px;}QLineEdit:focus{border:1px solid #555;}")
        lay.addWidget(self.entry)

        if browse:
            btn = QPushButton("…")
            btn.setFixedSize(28, 28)
            btn.setStyleSheet("QPushButton{background:#2e2e2e;color:#ccc;border:1px solid #3a3a3a;border-radius:4px;font-size:16px;}QPushButton:hover{background:#3a3a3a;}")
            btn.clicked.connect(self._browse)
            lay.addWidget(btn)

    def _browse(self):
        if self.browse_mode == "folder":
            path = QFileDialog.getExistingDirectory(self, "Select Folder")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.entry.setText(path)

    def value(self):
        return self.entry.text().strip()


class builder_form(QFrame):

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#0d0d0d;border-bottom-left-radius:8px;border-bottom-right-radius:8px;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(10)

        header = QLabel("Create Vault")
        header.setStyleSheet("color:white;font-size:18px;font-weight:bold;background:transparent;")
        lay.addWidget(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#2a2a2a;border:none;max-height:1px;")
        lay.addWidget(sep)
        lay.addSpacing(4)

        self.f_name = field_row("Vault Name", "my_vault")
        self.f_pass = field_row("Password", "")
        self.f_pass.entry.setEchoMode(QLineEdit.Password)
        self.f_src  = field_row("Source Folder", "", browse=True)
        self.f_fake = field_row("Fake Folder", "", browse=True)
        self.f_fake_pass = field_row("Fake Password", "")
        self.f_fake_pass.entry.setEchoMode(QLineEdit.Password)
        self.f_dest = field_row("Vault Destination", "", browse=True)

        for f in [self.f_name, self.f_pass, self.f_src, self.f_fake, self.f_fake_pass, self.f_dest]:
            lay.addWidget(f)

        lay.addSpacing(8)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("QProgressBar{border:none;background:#1e1e1e;border-radius:2px;}QProgressBar::chunk{background:#aaa;border-radius:2px;}")
        self.progress.hide()
        lay.addWidget(self.progress)

        self.status = QLabel("")
        self.status.setStyleSheet("color:#888;font-size:12px;background:transparent;")
        self.status.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.status)

        self.build_btn = QPushButton("Build Vault")
        self.build_btn.setFixedHeight(36)
        self.build_btn.setStyleSheet("QPushButton{background:#333;color:white;border:none;border-radius:5px;font-size:14px;font-weight:bold;}QPushButton:hover{background:#444;}QPushButton:pressed{background:#222;}QPushButton:disabled{background:#1e1e1e;color:#555;}")
        self.build_btn.clicked.connect(self._start_build)
        lay.addWidget(self.build_btn)

    def _start_build(self):
        name      = self.f_name.value()
        password  = self.f_pass.value()
        src       = self.f_src.value()
        fake      = self.f_fake.value()
        fake_pass = self.f_fake_pass.value()
        dest      = self.f_dest.value() or "./vaults"

        if not name or not password or not src:
            self._set_status("Name, password and source folder are required.", "#e05555")
            return

        if fake and not fake_pass:
            self._set_status("Fake password is required when a fake folder is set.", "#e05555")
            return

        extract_path = os.path.abspath("./extract.py")
        icon_path    = os.path.abspath("./icons/vault_icon.ico")

        self.build_btn.setEnabled(False)
        self.progress.show()
        self._set_status("Building vault…", "#888")

        self._thread = BuildThread({
            'name': name, 'password': password, 'src': src,
            'fake': fake, 'fake_pass': fake_pass, 'shortcut_dest': dest,
            'extract_path': extract_path, 'icon_path': icon_path
        })
        self._thread.done.connect(self._on_done)
        self._thread.start()

    def _on_done(self, success, err):
        self.progress.hide()
        self.build_btn.setEnabled(True)
        if success:
            self._set_status("Vault created successfully.", "#5aaa5a")
        else:
            self._set_status(f"Error: {err}", "#e05555")

    def _set_status(self, text, color):
        self.status.setText(text)
        self.status.setStyleSheet(f"color:{color};font-size:12px;background:transparent;")


class window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(480, 420)
        self.minimized = False
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        root = QFrame()
        root.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        self.setCentralWidget(root)

        tb = title_bar(parent=self, options=['-','X'],
                       title="Whale Builder", logo="./icons/logo.png")
        lay.addWidget(tb)

        self._form = builder_form()
        lay.addWidget(self._form)

    def minimize(self):
        self.winGeo = self.geometry()
        screenGeo = self.screen().availableGeometry()
        self.cx = self.winGeo.x() + self.winGeo.width() // 2
        self.cy = screenGeo.height()

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

        self._grp = QParallelAnimationGroup(self)
        self._grp.addAnimation(anim)
        self._grp.addAnimation(fade)
        self._grp.finished.connect(finish_anim)
        self._grp.start()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self.minimized:
                self.minimized = False
                self._restore()
        super().changeEvent(event)

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

        self._grp = QParallelAnimationGroup(self)
        self._grp.addAnimation(anim)
        self._grp.addAnimation(fade)
        self._grp.start()

    def shatter(self):
        ShatterEngine(self).start()


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = window()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
