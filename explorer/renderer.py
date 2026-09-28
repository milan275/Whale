import os, subprocess, sys
from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QTextEdit, QSlider, QPushButton, QFrame)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

TEXT_EXTS = {
    # plain text / config
    'txt', 'log', 'ini', 'cfg', 'yaml', 'yml', 'toml', 'env',
    # markup / data
    'md', 'markdown', 'rst', 'html', 'htm', 'xml', 'json', 'csv', 'tsv',
    # web
    'js', 'mjs', 'cjs', 'ts', 'tsx', 'jsx', 'css', 'scss', 'sass', 'less',
    # systems / compiled languages
    'c', 'h', 'cpp', 'cc', 'cxx', 'hpp', 'hxx',
    'cs', 'java', 'kt', 'kts', 'go', 'rs', 'swift',
    # scripting
    'py', 'pyw', 'rb', 'pl', 'pm', 'php', 'lua', 'sh', 'bash', 'zsh',
    'fish', 'ps1', 'psm1', 'bat', 'cmd',
    # other dev
    'r', 'scala', 'groovy', 'dart', 'ex', 'exs', 'erl', 'hrl',
    'hs', 'lhs', 'ml', 'mli', 'clj', 'cljs', 'lisp', 'el',
    'vim', 'sql', 'graphql', 'proto', 'tf', 'hcl', 'dockerfile',
    'makefile', 'mk', 'gradle',
}
IMAGE_EXTS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
VIDEO_EXTS = {'mp4', 'mov', 'avi', 'mkv'}
AUDIO_EXTS = {'wav', 'mp3', 'flac'}
RENDERABLE = TEXT_EXTS | IMAGE_EXTS | VIDEO_EXTS | AUDIO_EXTS | {'pdf'}


def open_system(path):
    if sys.platform == "win32":
        os.startfile(path)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class _base(QWidget):

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setStyleSheet("background:#121212;")
        self._lay = QVBoxLayout(self)
        self._lay.setContentsMargins(0, 0, 0, 0)
        self._lay.setSpacing(0)


class text_renderer(_base):

    def __init__(self, path):
        super().__init__(path)
        self._path = path
        self._modified = False

        # ── toolbar ──────────────────────────────────────────────────────────
        self._toolbar = QFrame()
        self._toolbar.setFixedHeight(34)
        self._toolbar.setStyleSheet(
            "background:#1e1e1e;border-bottom:1px solid #2a2a2a;")
        tb_lay = QHBoxLayout(self._toolbar)
        tb_lay.setContentsMargins(10, 0, 10, 0)
        tb_lay.setSpacing(8)

        self._status = QLabel("No changes")
        self._status.setStyleSheet("color:#555;font-size:11px;background:transparent;")
        tb_lay.addWidget(self._status)
        tb_lay.addStretch()

        self._save_btn = QPushButton("Save")
        self._save_btn.setFixedSize(60, 22)
        self._save_btn.setEnabled(False)
        self._save_btn.setStyleSheet(
            "QPushButton{background:#1a3a1a;color:#4a9a4a;border:1px solid #2a5a2a;"
            "border-radius:4px;font-size:11px;}"
            "QPushButton:hover{background:#1e4a1e;color:#5ab05a;}"
            "QPushButton:disabled{background:#1a1a1a;color:#333;border-color:#222;}")
        self._save_btn.clicked.connect(self._save)
        tb_lay.addWidget(self._save_btn)

        self._lay.addWidget(self._toolbar)

        # ── editor ───────────────────────────────────────────────────────────
        self._editor = QTextEdit()
        self._editor.setReadOnly(False)
        self._editor.setStyleSheet("""
            QTextEdit{background:#161616;color:#d4d4d4;border:none;
            font-family:'Consolas','Courier New',monospace;font-size:13px;padding:12px;}
            QScrollBar:vertical{width:8px;background:#1a1a1a;}
            QScrollBar::handle:vertical{background:#3a3a3a;border-radius:4px;}
            QScrollBar:horizontal{height:8px;background:#1a1a1a;}
            QScrollBar::handle:horizontal{background:#3a3a3a;border-radius:4px;}
        """)
        try:
            with open(path, 'r', errors='replace') as f:
                self._editor.setPlainText(f.read())
        except Exception as e:
            self._editor.setPlainText(f"[Error: {e}]")
            self._editor.setReadOnly(True)

        self._editor.document().contentsChanged.connect(self._on_change)
        self._lay.addWidget(self._editor)

    def _on_change(self):
        if not self._modified:
            self._modified = True
            self._status.setText("Unsaved changes")
            self._status.setStyleSheet("color:#c8a020;font-size:11px;background:transparent;")
            self._save_btn.setEnabled(True)

    def _save(self):
        try:
            with open(self._path, 'w', encoding='utf-8') as f:
                f.write(self._editor.toPlainText())
            self._modified = False
            self._status.setText("Saved")
            self._status.setStyleSheet("color:#4a9a4a;font-size:11px;background:transparent;")
            self._save_btn.setEnabled(False)
        except Exception as e:
            self._status.setText(f"Save failed: {e}")
            self._status.setStyleSheet("color:#c84040;font-size:11px;background:transparent;")


class image_renderer(_base):

    def __init__(self, path):
        super().__init__(path)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:#121212;}")
        inner = QWidget()
        inner.setStyleSheet("background:#121212;")
        lay = QVBoxLayout(inner)
        lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel()
        pix = QPixmap(path)
        if not pix.isNull():
            lbl.setPixmap(pix.scaled(900, 700, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            lbl.setText("Cannot load image")
            lbl.setStyleSheet("color:#888;")
        lay.addWidget(lbl)
        scroll.setWidget(inner)
        self._lay.addWidget(scroll)


class pdf_renderer(_base):

    def __init__(self, path):
        super().__init__(path)
        self._pages = []
        self._current = 0
        self._load(path)
        self._build_ui()

    def _load(self, path):
        try:
            import fitz
            from PySide6.QtGui import QImage
            doc = fitz.open(path)
            for page in doc:
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                self._pages.append(QPixmap.fromImage(img))
            doc.close()
        except Exception as e:
            self._error = str(e)

    def _build_ui(self):
        if not self._pages:
            lbl = QLabel(getattr(self, '_error', 'Install pymupdf: pip install pymupdf'))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#888;font-size:13px;padding:20px;")
            self._lay.addWidget(lbl)
            return

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet("QScrollArea{border:none;background:#1e1e1e;}")
        self._canvas = QLabel()
        self._canvas.setAlignment(Qt.AlignCenter)
        self._canvas.setStyleSheet("background:#1e1e1e;padding:10px;")
        self._scroll.setWidget(self._canvas)
        self._lay.addWidget(self._scroll)

        nav = QFrame()
        nav.setStyleSheet("background:#1a1a1a;border-top:1px solid #2a2a2a;")
        nav.setFixedHeight(38)
        nl = QHBoxLayout(nav)
        nl.setContentsMargins(12, 4, 12, 4)

        self._prev = QPushButton("‹")
        self._next = QPushButton("›")
        self._page_lbl = QLabel()
        self._page_lbl.setStyleSheet("color:#aaa;font-size:13px;")
        self._page_lbl.setAlignment(Qt.AlignCenter)

        for b in [self._prev, self._next]:
            b.setFixedSize(28, 28)
            b.setStyleSheet("QPushButton{background:#2a2a2a;color:#ccc;border:none;border-radius:4px;font-size:18px;}QPushButton:hover{background:#3a3a3a;}")
        self._prev.clicked.connect(lambda: self._go(-1))
        self._next.clicked.connect(lambda: self._go(1))
        nl.addStretch()
        nl.addWidget(self._prev)
        nl.addWidget(self._page_lbl)
        nl.addWidget(self._next)
        nl.addStretch()
        self._lay.addWidget(nav)
        self._show_page()

    def _go(self, d):
        self._current = max(0, min(len(self._pages) - 1, self._current + d))
        self._show_page()

    def _show_page(self):
        self._canvas.setPixmap(self._pages[self._current])
        self._page_lbl.setText(f"{self._current + 1} / {len(self._pages)}")
        self._prev.setEnabled(self._current > 0)
        self._next.setEnabled(self._current < len(self._pages) - 1)


class video_renderer(_base):

    def __init__(self, path):
        super().__init__(path)
        try:
            from PySide6.QtMultimediaWidgets import QVideoWidget
            self._player = QMediaPlayer()
            self._audio = QAudioOutput()
            self._player.setAudioOutput(self._audio)
            self._video_widget = QVideoWidget()
            self._video_widget.setStyleSheet("background:black;")
            self._player.setVideoOutput(self._video_widget)
            self._player.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
            self._lay.addWidget(self._video_widget)
            self._lay.addWidget(self._build_controls())
        except Exception as e:
            lbl = QLabel(f"Cannot render video: {e}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#888;")
            self._lay.addWidget(lbl)

    def _build_controls(self):
        bar = QFrame()
        bar.setStyleSheet("background:#1a1a1a;border-top:1px solid #2a2a2a;")
        bar.setFixedHeight(48)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(12, 4, 12, 4)
        lay.setSpacing(8)

        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(30, 30)
        self._play_btn.setStyleSheet("QPushButton{background:#2a2a2a;color:white;border:none;border-radius:4px;font-size:14px;}QPushButton:hover{background:#3a3a3a;}")
        self._play_btn.clicked.connect(self._toggle_play)

        slider_ss = "QSlider::groove:horizontal{height:4px;background:#333;border-radius:2px;}QSlider::handle:horizontal{width:12px;height:12px;background:#aaa;border-radius:6px;margin:-4px 0;}QSlider::sub-page:horizontal{background:#777;border-radius:2px;}"

        self._seek = QSlider(Qt.Horizontal)
        self._seek.setStyleSheet(slider_ss)
        self._seek.sliderMoved.connect(lambda v: self._player.setPosition(v))

        self._vol = QSlider(Qt.Horizontal)
        self._vol.setFixedWidth(80)
        self._vol.setRange(0, 100)
        self._vol.setValue(80)
        self._vol.setStyleSheet(slider_ss)
        self._vol.valueChanged.connect(lambda v: self._audio.setVolume(v / 100))

        self._time_lbl = QLabel("0:00")
        self._time_lbl.setStyleSheet("color:#888;font-size:11px;")
        self._time_lbl.setFixedWidth(38)

        vol_lbl = QLabel("🔊")
        vol_lbl.setStyleSheet("color:#888;font-size:13px;background:transparent;")

        lay.addWidget(self._play_btn)
        lay.addWidget(self._seek)
        lay.addWidget(self._time_lbl)
        lay.addWidget(vol_lbl)
        lay.addWidget(self._vol)

        self._player.playbackStateChanged.connect(self._on_state)
        self._player.durationChanged.connect(lambda d: self._seek.setRange(0, d))
        self._player.positionChanged.connect(self._on_pos)
        return bar

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_state(self, state):
        self._play_btn.setText("⏸" if state == QMediaPlayer.PlayingState else "▶")

    def _on_pos(self, pos):
        self._seek.setValue(pos)
        s = pos // 1000
        self._time_lbl.setText(f"{s//60}:{s%60:02d}")


class audio_renderer(_base):

    def __init__(self, path):
        super().__init__(path)
        try:
            self._player = QMediaPlayer()
            self._audio = QAudioOutput()
            self._player.setAudioOutput(self._audio)
            self._player.setSource(QUrl.fromLocalFile(os.path.abspath(path)))
            self._lay.addWidget(self._build_ui(path))
        except Exception as e:
            lbl = QLabel(f"Cannot render audio: {e}")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color:#888;")
            self._lay.addWidget(lbl)

    def _build_ui(self, path):
        wrap = QFrame()
        wrap.setStyleSheet("background:#161616;")
        lay = QVBoxLayout(wrap)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(16)

        icon = QLabel("♫")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("color:#aaa;font-size:72px;")
        lay.addWidget(icon)

        name_lbl = QLabel(Path(path).name)
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setStyleSheet("color:#ccc;font-size:14px;")
        lay.addWidget(name_lbl)

        self._seek = QSlider(Qt.Horizontal)
        self._seek.setStyleSheet("QSlider::groove:horizontal{height:4px;background:#333;border-radius:2px;}QSlider::handle:horizontal{width:12px;height:12px;background:#aaa;border-radius:6px;margin:-4px 0;}QSlider::sub-page:horizontal{background:#777;border-radius:2px;}")
        self._seek.setFixedWidth(300)
        self._seek.sliderMoved.connect(lambda v: self._player.setPosition(v))
        lay.addWidget(self._seek, alignment=Qt.AlignCenter)

        self._play_btn = QPushButton("▶")
        self._play_btn.setFixedSize(44, 44)
        self._play_btn.setStyleSheet("QPushButton{background:#333;color:white;border:none;border-radius:22px;font-size:18px;}QPushButton:hover{background:#444;}")
        self._play_btn.clicked.connect(self._toggle_play)
        lay.addWidget(self._play_btn, alignment=Qt.AlignCenter)

        self._time_lbl = QLabel("0:00 / 0:00")
        self._time_lbl.setAlignment(Qt.AlignCenter)
        self._time_lbl.setStyleSheet("color:#666;font-size:12px;")
        lay.addWidget(self._time_lbl)

        self._player.playbackStateChanged.connect(self._on_state)
        self._player.durationChanged.connect(lambda d: self._seek.setRange(0, d))
        self._player.positionChanged.connect(self._on_pos)
        return wrap

    def _toggle_play(self):
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def _on_state(self, state):
        self._play_btn.setText("⏸" if state == QMediaPlayer.PlayingState else "▶")

    def _on_pos(self, pos):
        self._seek.setValue(pos)
        dur = self._player.duration()
        s = pos // 1000
        d = dur // 1000
        self._time_lbl.setText(f"{s//60}:{s%60:02d} / {d//60}:{d%60:02d}")


def make_renderer(path):
    ext = Path(path).suffix.lstrip('.').lower()
    if ext in TEXT_EXTS:  return text_renderer(path)
    if ext in IMAGE_EXTS: return image_renderer(path)
    if ext == 'pdf':      return pdf_renderer(path)
    if ext in VIDEO_EXTS: return video_renderer(path)
    if ext in AUDIO_EXTS: return audio_renderer(path)
    return None
