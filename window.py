from PySide6.QtWidgets import QApplication,QMainWindow,QFrame,QWidget,QVBoxLayout,QHBoxLayout,QPushButton,QLabel
from PySide6.QtCore import Qt,QPropertyAnimation,QEasingCurve,QRect
from PySide6.QtGui import QPixmap

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
                butt.clicked.connect(parent.close)
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
                    butt.clicked.connect(parent.showMinimized)
                self.layout.addWidget(butt)

        self.setEdge(f"{borderRad}px") #sets initial styling + manage border rad later

        
    def toggle_state(self):
        if self.state == 0:
            self.parent.showMaximized()
            self.max_btn.setText('❐')
            self.max_btn.setStyleSheet(f"""QPushButton{{background-color:{self.bg_color};color:{self.color};border:None;border-radius:0;font-size:15px;}}
                QPushButton:hover{{background-color:{self.hover_color};font-weight:bold;}}
                """)
            self.state=1
            self.setEdge(0)
        else:
            self.parent.showNormal()
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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Window = window()
    Window.show()
    sys.exit(app.exec())