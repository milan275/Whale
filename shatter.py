from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPointF, Property, QObject
from PySide6.QtGui import QPixmap, QPainter, QPolygonF, QPainterPath
import random,math

class ShatterOverlay(QWidget):
    
    def __init__(self, pixmap, win_geo, screen_geo, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.pixmap = pixmap
        self._progress = 0.0
        
        self.offset_x = win_geo.x() - screen_geo.x()
        self.offset_y = win_geo.y() - screen_geo.y()
        
        self.shards = []
        self.generate_shards()
        
    def generate_shards(self):
        cols, rows = 8, 8
        w, h = self.pixmap.width(), self.pixmap.height()
        cw, ch = w / cols, h / rows
        
        nodes = []
        for r in range(rows + 1):
            row_nodes = []
            for c in range(cols + 1):
                x = c * cw
                y = r * ch
                if 0 < c < cols: x += random.uniform(-0.4, 0.4) * cw
                if 0 < r < rows: y += random.uniform(-0.4, 0.4) * ch
                row_nodes.append(QPointF(x, y))
            nodes.append(row_nodes)
            
        shards_data = []
        for r in range(rows):
            for c in range(cols):
                p_tl, p_tr = nodes[r][c], nodes[r][c+1]
                p_br, p_bl = nodes[r+1][c+1], nodes[r+1][c]
                
                cx = (c + 0.5) * cw + random.uniform(-0.3, 0.3) * cw
                cy = (r + 0.5) * ch + random.uniform(-0.3, 0.3) * ch
                p_c = QPointF(cx, cy)
                
                shards_data.extend([[p_tl, p_tr, p_c], [p_tr, p_br, p_c], [p_br, p_bl, p_c], [p_bl, p_tl, p_c]])
                
        for poly_pts in shards_data:
            polygon = QPolygonF(poly_pts)
            boundingRect = polygon.boundingRect().toRect()
            boundingRect.adjust(-1, -1, 1, 1) 
            boundingRect = boundingRect.intersected(QRect(0, 0, w, h))
            
            if boundingRect.width() <= 2 or boundingRect.height() <= 2: continue
                
            shard_pix = QPixmap(boundingRect.size())
            shard_pix.fill(Qt.transparent)
            
            painter = QPainter(shard_pix)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            
            path = QPainterPath()
            offset_poly = QPolygonF([p - QPointF(boundingRect.topLeft()) for p in poly_pts])
            path.addPolygon(offset_poly)
            
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, self.pixmap, boundingRect.x(), boundingRect.y(), boundingRect.width(), boundingRect.height())
            painter.end()
            
            cx, cy = boundingRect.center().x(), boundingRect.center().y()
            dir_x, dir_y = cx - (w / 2), cy - (h / 2)
            dist = math.hypot(dir_x, dir_y) + 0.1
            nx, ny = dir_x / dist, dir_y / dist
            
            speed = random.uniform(50, 400)
            self.shards.append({
                'pix': shard_pix, 'x': boundingRect.x(), 'y': boundingRect.y(),
                'cx': shard_pix.width() / 2, 'cy': shard_pix.height() / 2,
                'vx': nx * speed + random.uniform(-50, 50),
                'vy': ny * speed + random.uniform(-200, 50),
                'rot': random.uniform(-200, 200)
            })

    def get_progress(self): return self._progress
        
    def set_progress(self, val):
        self._progress = val
        self.setWindowOpacity(max(0.0, 1.0 - (val ** 1.5)))
        self.update() 
        
    progress = Property(float, get_progress, set_progress)
    
    def paintEvent(self, event):
        if not self.shards: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        t = self._progress
        gravity = 1200 * (t ** 2)
        
        for s in self.shards:
            px, py = self.offset_x + s['x'] + s['vx'] * t, self.offset_y + s['y'] + s['vy'] * t + gravity
            painter.save()
            painter.translate(px + s['cx'], py + s['cy'])
            painter.rotate(s['rot'] * t)
            painter.translate(-s['cx'], -s['cy'])
            painter.drawPixmap(0, 0, s['pix'])
            painter.restore()

class ShatterEngine(QObject):
    
    def __init__(self, target_window, on_finish=None):
        super().__init__(target_window)
        self.window = target_window
        self.on_finish = on_finish
        
    def start(self):
        scrn = self.window.grab()
        win_geo = self.window.geometry()
        screen_geo = self.window.screen().geometry()
        
        self.overlay = ShatterOverlay(scrn, win_geo, screen_geo)
        self.overlay.setGeometry(screen_geo)
        self.overlay.show()
        
        self.window.hide()
        
        self.anim = QPropertyAnimation(self.overlay, b"progress")
        self.anim.setDuration(1200) 
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.OutQuad) 
        self.anim.finished.connect(self._finish)
        self.anim.start()

    def _finish(self):
        self.overlay.close()
        self.overlay.deleteLater()
        
        if self.on_finish and callable(self.on_finish):
            self.on_finish()
        else:
            self.window.close()
            QApplication.instance().quit()

