from pathlib import Path
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QGridLayout, QPushButton)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QCursor
from .icons import _make_folder_icon, _make_file_icon
from .renderer_window import renderer_window

ICON_SIZE = 56
GRID_ITEM_W = 90
GRID_ITEM_H = 96
GRID_SPACING = 4


class file_item(QFrame):
    clicked = Signal(str)
    double_clicked = Signal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.setFixedSize(GRID_ITEM_W, GRID_ITEM_H)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet("background:transparent;border:none;border-radius:6px;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 6, 4, 4)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self._icon_lbl = QLabel()
        self._icon_lbl.setFixedSize(ICON_SIZE, ICON_SIZE)
        self._icon_lbl.setAlignment(Qt.AlignCenter)
        self._icon_lbl.setStyleSheet("background:transparent;")
        lay.addWidget(self._icon_lbl, alignment=Qt.AlignHCenter)

        name = Path(path).name
        name_lbl = QLabel(name if len(name) <= 14 else name[:12] + "…")
        name_lbl.setAlignment(Qt.AlignCenter)
        name_lbl.setWordWrap(False)
        name_lbl.setStyleSheet("color:#ccc;font-size:11px;background:transparent;")
        lay.addWidget(name_lbl)

        p = Path(path)
        if p.is_dir():
            self._icon_lbl.setPixmap(_make_folder_icon(ICON_SIZE))
        else:
            self._icon_lbl.setPixmap(_make_file_icon(p.suffix.lstrip('.').lower(), ICON_SIZE))

    def set_selected(self, v):
        self.setStyleSheet(
            "background:#1e3a5f;border:1px solid #2e6da4;border-radius:6px;" if v
            else "background:transparent;border:none;border-radius:6px;"
        )

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.path)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.double_clicked.emit(self.path)

    def enterEvent(self, e):
        if "1e3a5f" not in self.styleSheet():
            self.setStyleSheet("background:#1e1e1e;border:none;border-radius:6px;")

    def leaveEvent(self, e):
        if "1e3a5f" not in self.styleSheet():
            self.setStyleSheet("background:transparent;border:none;border-radius:6px;")


class file_grid(QWidget):
    item_clicked = Signal(str)
    item_opened = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#161616;")
        self._selected = None
        self._items = {}
        self._entries = []
        self._cols = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            "QScrollArea{border:none;background:#161616;}"
            "QScrollBar:vertical{width:8px;background:#1a1a1a;}"
            "QScrollBar::handle:vertical{background:#3a3a3a;border-radius:4px;}")
        self._inner = QWidget()
        self._inner.setStyleSheet("background:#161616;")
        self._grid = QGridLayout(self._inner)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setSpacing(GRID_SPACING)
        self._scroll.setWidget(self._inner)
        lay.addWidget(self._scroll)

        self._resize_timer = QTimer()
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._relayout)

    def load_path(self, path):
        self._entries = sorted(Path(path).iterdir(),
                               key=lambda x: (not x.is_dir(), x.name.lower()))
        self._selected = None
        self._cols = 0  # force full rebuild regardless of column count
        self._relayout()

    def _relayout(self):
        available = self._scroll.viewport().width() - 24
        cols = max(1, available // (GRID_ITEM_W + GRID_SPACING))
        if cols == self._cols and self._items:
            return
        self._cols = cols

        for i in reversed(range(self._grid.count())):
            w = self._grid.itemAt(i).widget()
            if w:
                w.setParent(None)
        self._items.clear()

        for idx, entry in enumerate(self._entries):
            item = file_item(str(entry))
            item.clicked.connect(self._on_click)
            item.double_clicked.connect(self._on_dbl)
            self._grid.addWidget(item, idx // cols, idx % cols)
            self._items[str(entry)] = item

        self._grid.setColumnStretch(cols, 1)
        rows = (len(self._entries) + cols - 1) // cols
        self._grid.setRowStretch(rows, 1)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._resize_timer.start(50)

    def _on_click(self, path):
        if self._selected and self._selected in self._items:
            self._items[self._selected].set_selected(False)
        self._selected = path
        if path in self._items:
            self._items[path].set_selected(True)
        self.item_clicked.emit(path)

    def _on_dbl(self, path):
        self.item_opened.emit(path)


class breadcrumb(QFrame):
    navigate = Signal(str)
    go_back = Signal()

    def __init__(self, root):
        super().__init__()
        self._root = root
        self.setFixedHeight(32)
        self.setStyleSheet("background:#161616;border-bottom:1px solid #1e1e1e;")
        self._lay = QHBoxLayout(self)
        self._lay.setContentsMargins(8, 0, 12, 0)
        self._lay.setSpacing(2)

        self._back_btn = QPushButton("←")
        self._back_btn.setFixedSize(26, 22)
        self._back_btn.setStyleSheet(
            "QPushButton{background:#222;color:#888;border:none;border-radius:4px;font-size:14px;}"
            "QPushButton:hover{background:#2e2e2e;color:#ccc;}"
            "QPushButton:disabled{color:#333;background:#1a1a1a;}")
        self._back_btn.setCursor(Qt.PointingHandCursor)
        self._back_btn.clicked.connect(self.go_back.emit)
        self._back_btn.setEnabled(False)
        self._lay.addWidget(self._back_btn)

        sep = QFrame()
        sep.setFixedSize(1, 14)
        sep.setStyleSheet("background:#2a2a2a;")
        self._lay.addWidget(sep)

    def set_back_enabled(self, enabled):
        self._back_btn.setEnabled(enabled)

    def set_path(self, path):
        # remove everything after the back button and separator (indices 0 and 1)
        while self._lay.count() > 2:
            item = self._lay.takeAt(2)
            w = item.widget()
            if w:
                w.deleteLater()

        rel = Path(path).relative_to(Path(self._root).parent)
        parts = list(rel.parts)
        full = Path(self._root).parent

        for i, part in enumerate(parts):
            full = full / part
            fp = str(full)
            btn = QPushButton(part)
            btn.setStyleSheet("QPushButton{background:transparent;color:#555;border:none;font-size:11px;padding:2px 4px;}QPushButton:hover{color:#aaa;}")
            btn.clicked.connect(lambda _, p=fp: self.navigate.emit(p))
            self._lay.addWidget(btn)
            if i < len(parts) - 1:
                sep = QLabel("›")
                sep.setStyleSheet("color:#333;font-size:11px;background:transparent;")
                self._lay.addWidget(sep)
        self._lay.addStretch()


class explorer_pane(QWidget):

    def __init__(self, root):
        super().__init__()
        self._root = root
        self._use_system = False
        self._open_windows = []
        self._history = []          # stack of visited paths for back navigation
        self._current_path = None
        self.setStyleSheet("background:#161616;")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self._breadcrumb = breadcrumb(root)
        self._breadcrumb.navigate.connect(self._nav)
        self._breadcrumb.go_back.connect(self._go_back)
        lay.addWidget(self._breadcrumb)

        self._grid = file_grid()
        self._grid.item_clicked.connect(self._on_click)
        self._grid.item_opened.connect(self._on_open)
        lay.addWidget(self._grid)

        self._nav(root)

    def set_system_mode(self, v):
        self._use_system = v

    def _nav(self, path, push_history=True):
        if Path(path).is_dir():
            if push_history and self._current_path and self._current_path != path:
                self._history.append(self._current_path)
            self._current_path = path
            self._grid.load_path(path)
            self._breadcrumb.set_path(path)
            self._breadcrumb.set_back_enabled(len(self._history) > 0)

    def _go_back(self):
        if self._history:
            prev = self._history.pop()
            self._current_path = None          # prevent duplicate push
            self._nav(prev, push_history=False)

    def _on_click(self, path):
        p = Path(path)
        if p.is_dir():
            self._nav(path)          # folders: always use our explorer, ignore system toggle
        else:
            win = renderer_window(path, self._use_system)
            self._open_windows.append(win)

    def _on_open(self, path):
        p = Path(path)
        if p.is_dir():
            self._nav(path)          # folders: always use our explorer, ignore system toggle
        else:
            win = renderer_window(path, self._use_system)
            self._open_windows.append(win)
