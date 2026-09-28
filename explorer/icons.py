from PySide6.QtGui import QPixmap, QPainter, QColor, QPainterPath, QLinearGradient, QFont, QImage
from PySide6.QtCore import Qt, QRect, QRectF
from pathlib import Path

EXT_COLOR = {
    'txt':  ('#4a9eda', '#2e6da4'),
    'py':   ('#f5c542', '#c8960a'),
    'js':   ('#f0db4f', '#b8a200'),
    'json': ('#a8d8a8', '#5a9a5a'),
    'html': ('#e87040', '#b04010'),
    'css':  ('#264de4', '#1a35a0'),
    'pdf':  ('#e05555', '#a02020'),
    'png':  ('#9b59b6', '#6c3483'),
    'jpg':  ('#9b59b6', '#6c3483'),
    'jpeg': ('#9b59b6', '#6c3483'),
    'gif':  ('#9b59b6', '#6c3483'),
    'bmp':  ('#9b59b6', '#6c3483'),
    'mp4':  ('#e74c3c', '#922b21'),
    'mov':  ('#e74c3c', '#922b21'),
    'avi':  ('#e74c3c', '#922b21'),
    'wav':  ('#5a9a7a', '#2e6a4a'),
    'mp3':  ('#5a9a7a', '#2e6a4a'),
    'flac': ('#5a9a7a', '#2e6a4a'),
    'zip':  ('#f39c12', '#b07d0a'),
    'rar':  ('#f39c12', '#b07d0a'),
    'exe':  ('#555', '#333'),
    'bat':  ('#555', '#333'),
}

def _make_file_icon(ext, size=64):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    top, bot = EXT_COLOR.get(ext.lower(), ('#555', '#333'))
    grad = QLinearGradient(0, 0, 0, size)
    grad.setColorAt(0, QColor(top))
    grad.setColorAt(1, QColor(bot))

    fold = size * 0.22
    body = QPainterPath()
    body.moveTo(size * 0.1, 0)
    body.lineTo(size - fold, 0)
    body.lineTo(size * 0.9, fold)
    body.lineTo(size * 0.9, size * 0.92)
    body.quadTo(size * 0.9, size * 0.97, size * 0.84, size * 0.97)
    body.lineTo(size * 0.16, size * 0.97)
    body.quadTo(size * 0.1, size * 0.97, size * 0.1, size * 0.92)
    body.closeSubpath()
    p.fillPath(body, grad)

    corner = QPainterPath()
    corner.moveTo(size - fold, 0)
    corner.lineTo(size - fold, fold)
    corner.lineTo(size * 0.9, fold)
    corner.closeSubpath()
    p.fillPath(corner, QColor(0, 0, 0, 60))

    fs = max(8, size // 6)
    p.setFont(QFont("Segoe UI", fs, QFont.Bold))
    p.setPen(QColor(255, 255, 255, 220))
    p.drawText(QRect(int(size * 0.1), int(size * 0.52), int(size * 0.8), int(size * 0.4)),
               Qt.AlignCenter, ext.upper()[:4])
    p.end()
    return pix


def _make_folder_icon(size=64):
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    tab = QPainterPath()
    tab.moveTo(size * 0.08, size * 0.32)
    tab.lineTo(size * 0.38, size * 0.32)
    tab.lineTo(size * 0.45, size * 0.22)
    tab.lineTo(size * 0.65, size * 0.22)
    tab.lineTo(size * 0.65, size * 0.32)
    tab.lineTo(size * 0.92, size * 0.32)
    tab.lineTo(size * 0.92, size * 0.88)
    tab.quadTo(size * 0.92, size * 0.94, size * 0.86, size * 0.94)
    tab.lineTo(size * 0.14, size * 0.94)
    tab.quadTo(size * 0.08, size * 0.94, size * 0.08, size * 0.88)
    tab.closeSubpath()

    grad = QLinearGradient(0, size * 0.22, 0, size * 0.94)
    grad.setColorAt(0, QColor('#fdd866'))
    grad.setColorAt(1, QColor('#e8a020'))
    p.fillPath(tab, grad)

    inner = QPainterPath()
    inner.addRoundedRect(QRectF(size * 0.1, size * 0.38, size * 0.8, size * 0.52), 4, 4)
    grad2 = QLinearGradient(0, size * 0.38, 0, size * 0.9)
    grad2.setColorAt(0, QColor('#ffe080'))
    grad2.setColorAt(1, QColor('#f0b030'))
    p.fillPath(inner, grad2)
    p.end()
    return pix


def _image_preview(path, size):
    pix = QPixmap(path)
    if pix.isNull():
        return None
    return pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def _video_preview(path, size):
    try:
        import cv2
        cap = cv2.VideoCapture(path)
        cap.set(cv2.CAP_PROP_POS_MSEC, 500)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
        base = QPixmap.fromImage(img).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return _overlay_play(base)
    except Exception:
        return None


def _overlay_play(pix):
    out = QPixmap(pix.size())
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.drawPixmap(0, 0, pix)
    w, h = pix.width(), pix.height()
    cx, cy, r = w // 2, h // 2, min(w, h) // 5
    p.setBrush(QColor(0, 0, 0, 120))
    p.setPen(Qt.NoPen)
    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
    tri = QPainterPath()
    tri.moveTo(cx - r // 2, cy - r // 2)
    tri.lineTo(cx + r // 2, cy)
    tri.lineTo(cx - r // 2, cy + r // 2)
    tri.closeSubpath()
    p.fillPath(tri, QColor(255, 255, 255, 200))
    p.end()
    return out


def get_preview_pixmap(path, size=64):
    ext = Path(path).suffix.lstrip('.').lower()
    if ext in ('png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'):
        return _image_preview(path, size)
    if ext in ('mp4', 'mov', 'avi', 'mkv'):
        return _video_preview(path, size)
    return None


def _round_preview(pix, size):
    out = QPixmap(size, size)
    out.fill(Qt.transparent)
    p = QPainter(out)
    p.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(QRectF(0, 0, size, size), 6, 6)
    p.setClipPath(path)
    scaled = pix.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
    x = (scaled.width() - size) // 2
    y = (scaled.height() - size) // 2
    p.drawPixmap(-x, -y, scaled)
    p.end()
    return out


def get_icon_pixmap(path, size=48):
    p = Path(path)
    if p.is_dir():
        return _make_folder_icon(size)
    ext = p.suffix.lstrip('.').lower()
    preview = get_preview_pixmap(path, size)
    if preview:
        return _round_preview(preview, size)
    return _make_file_icon(ext, size)
