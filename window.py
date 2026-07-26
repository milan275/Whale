from PySide6.QtWidgets import QApplication,QMainWindow,QFrame,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel,QGraphicsOpacityEffect
from PySide6.QtCore import Qt,QPropertyAnimation,QEasingCurve,QRect,QParallelAnimationGroup,QEvent
from PySide6.QtGui import QPixmap
import random

class title_bar(QFrame):

    def __init__(self,parent,options=['-','[]','X'],prop={'bg-color':'#2b2b2b','color':'white','hover-color':'#545454'},borderRad='8px',title="Untitled Window",logo=""):

        super().__init__()

        self.bg_color = prop['bg-color']
        self.color = prop['color']
        self.hover_color = prop['hover-color']
        self.state = 0 #0=small 1=full screen
        self.parent=parent
        self.layout = QHBoxLayout(self)
        self.setFixedHeight(35)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)

        if logo:
            pixmap = QPixmap(logo).scaled(35,35, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo = QLabel()
            self.logo.setPixmap(pixmap)
            self.logo.setFixedSize(42,35)
            self.logo.setStyleSheet("padding-left:10px;padding-right:0px;")
            self.layout.addWidget(self.logo)


        self.title = QLabel(title)
        self.title.setStyleSheet("padding-left:10px;font-size:14px")
        self.layout.addWidget(self.title)
        self.layout.addStretch()

        for option in options:
            if option == 'X': 
                butt = QPushButton('×')
                butt.setFixedSize(35,35)
                butt.clicked.connect(parent.shatter)
                self.layout.addWidget(butt)
                self.close_btn = butt
            else:
                symbol = '□' if option =='[]' else '-'
                pb = 5 if option == '[]' else 3
                butt = QPushButton(symbol)
                butt.setStyleSheet(f"""QPushButton{{background-color:{self.bg_color};color:{self.color};border:None;border-radius:0;font-size:22px;padding-bottom:{pb}px;}}
                QPushButton:hover{{background-color:{self.hover_color};font-weight:bold;}}
                """)
                butt.setFixedSize(35,35)
                if option == '[]':
                    butt.clicked.connect(self.toggle_state)
                    self.max_btn = butt
                else:
                    butt.clicked.connect(parent.minimize)
                self.layout.addWidget(butt)

        self.setEdge(borderRad) #sets initial styling + manage border rad later

        
    def toggle_state(self):
        if self.state == 0:
            self.parent.maximize()
            self.max_btn.setText('❐')
            self.max_btn.setStyleSheet(f"""QPushButton{{background-color:{self.bg_color};color:{self.color};border:None;border-radius:0;font-size:15px;}}
                QPushButton:hover{{background-color:{self.hover_color};font-weight:bold;}}
                """)
            self.state=1
            self.setEdge(0)
        else:
            self.parent.normalize()
            self.state=0
            self.max_btn.setText('□')
            self.max_btn.setStyleSheet(f"""QPushButton{{background-color:{self.bg_color};color:{self.color};border:None;border-radius:0;font-size:22px;padding-bottom:5px;}}
                QPushButton:hover{{background-color:{self.hover_color};font-weight:bold;}}
                """)
            self.setEdge('8px')

    def setEdge(self,borderRad):
        self.setStyleSheet(f"color:{self.color};background-color:{self.bg_color};border:None;border-top-left-radius:{borderRad};border-top-right-radius:{borderRad};margin:0;")
        self.close_btn.setStyleSheet(f"""QPushButton{{background-color:{self.bg_color};color:{self.color};border:None;border-radius:0;border-top-right-radius:{borderRad};font-size:22px;padding-bottom:2px;}}
                QPushButton:hover{{background-color:red;font-weight:bold;color:white}}
                """)

class canvas(QFrame):

    def __init__(self,options=['-','[]','X'],prop={'bg-color':'#000000','color':'white'},borderRad='8px',margins=[10]):

        super().__init__()

        color = prop['color']
        bg_color = prop['bg-color']
        
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(f"color:{color};background-color:{bg_color};border:None;border-bottom-left-radius:{borderRad};border-bottom-right-radius:{borderRad};")



class window(QMainWindow):

    def __init__(self,size=(600,400)):
        super().__init__()
        self.resize(*size)
        self.size = size
        self.minimized = False
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.win = QFrame()
        self.layout = QVBoxLayout(self.win)
        self.win.setStyleSheet("background:transparent")
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setCentralWidget(self.win)

        titleBar = title_bar(parent=self,title="Whale Explorer",logo="./icons/logo.png")
        self.layout.addWidget(titleBar)

        Canvas = canvas()
        self.layout.addWidget(Canvas)

    def change_state_to(self,state="normal"):

        if state == "full":
            self.geo = [self.geometry(),self.screen().availableGeometry()] # [size,full screen size]
        self.animation  = QPropertyAnimation(self,b"geometry")
        self.animation.setDuration(250)
        self.animation.setStartValue(self.geo[0 if state=="full" else 1])
        self.animation.setEndValue(self.geo[1 if state=="full" else 0])
        self.animation.setEasingCurve(QEasingCurve.InOutQuad) #makes start and end smooth

        self.animation.finished.connect(self.showMaximized if state == "full" else self.showNormal) 
        self.animation.start()

    def maximize(self):
        self.change_state_to("full")
    def normalize(self):
        self.showNormal()
        self.setGeometry(self.geo[1])
        self.change_state_to("normal")
    def minimize(self):
        self.winGeo = self.geometry()
        screenGeo = self.screen().availableGeometry()
        self.x = self.winGeo.x()+self.winGeo.width()//2 # x of window's center
        self.y = screenGeo.height() #bottom
        final = QRect(self.x,self.y,0,0) #size=0
        
        animation = QPropertyAnimation(self,b"geometry")
        animation.setDuration(250)
        animation.setStartValue(self.winGeo)
        animation.setEndValue(final)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self,b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(1)
        fade.setEndValue(0)

        def finish_anim():
            self.showMinimized()
            self.minimized=True

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
        animation = QPropertyAnimation(self,b"geometry")
        animation.setDuration(250)
        animation.setStartValue(QRect(self.x,self.y,0,0))
        animation.setEndValue(self.winGeo)
        animation.setEasingCurve(QEasingCurve.InOutQuad)

        fade = QPropertyAnimation(self,b"windowOpacity")
        fade.setDuration(250)
        fade.setStartValue(0)
        fade.setEndValue(1)

        self.group = QParallelAnimationGroup(self)
        self.group.addAnimation(animation)
        self.group.addAnimation(fade)
        self.group.start()

    def shatter(self,func=None):

        def finish():
            for shard in self.frags:
                shard.deleteLater()
            self.frags.clear()
            if callable(func):
                func()
            else:
                self.close()

        self.shatterAnimation = QParallelAnimationGroup()
        scrn = self.grab()
        rows,cols = 8,8
        h,w = self.height()//rows,self.width()//cols
        self.win.hide()
        self.frags=[]
        
        for r in range(rows):
            for c in range(cols):

                #crration
                strtGeo = QRect(w*c,h*r,w,h)
                img = scrn.copy(strtGeo)
                shard = QLabel(self)
                shard.setPixmap(img)
                shard.setGeometry(strtGeo)
                self.frags += [shard]
                shard.show()

                #explosion
                dx = random.randint(-250,250)
                dy = random.randint(300,700)
                endGeo = QRect(strtGeo.x()+dx,strtGeo.y()+dy,w,h)

                geoAnimation = QPropertyAnimation(shard,b"geometry")
                geoAnimation.setStartValue(strtGeo)
                geoAnimation.setEndValue(endGeo)
                geoAnimation.setEasingCurve(QEasingCurve.InQuad)
                geoAnimation.setDuration(600)

                #ghost effect
                ghost_eff = QGraphicsOpacityEffect(shard)
                shard.setGraphicsEffect(ghost_eff)
                fadeAnim = QPropertyAnimation(ghost_eff,b"opacity")
                fadeAnim.setStartValue(1)
                fadeAnim.setEndValue(0)
                fadeAnim.setDuration(600)

                self.shatterAnimation.addAnimation(geoAnimation)
                self.shatterAnimation.addAnimation(fadeAnim)


        self.shatterAnimation.finished.connect(finish)
        self.shatterAnimation.start()
            
        

def run():
    import sys
    app = QApplication(sys.argv)
    Window = window()
    Window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()