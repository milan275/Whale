import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class CustomRenderer(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setWindowTitle(f"Whale Renderer - {os.path.basename(path)}")
        self.resize(800, 600)
        
        self.setWindowFlags(Qt.WindowType.Window|Qt.WindowType.WindowMinimizeButtonHint|Qt.WindowType.WindowMaximizeButtonHint|Qt.WindowType.WindowCloseButtonHint)
        
        self.main_layout = QVBoxLayout(self)
        ext = path.lower().split('.')[-1]
        
        if ext in ['txt', 'py', 'json', 'md', 'csv', 'log', 'ini']:
            self.text_edit = QTextEdit()
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.text_edit.setText(f.read())
            except Exception as e:
                self.text_edit.setText(f"Error reading file: {e}")
                
            self.text_edit.setReadOnly(False)
            self.text_edit.textChanged.connect(self.reset_save_button)
            self.main_layout.addWidget(self.text_edit)
            
        elif ext in ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'webp']:
            self.label = QLabel()
            pixmap = QPixmap(path)
            self.label.setPixmap(pixmap.scaled(780, 530, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.label)
            
        else:
            self.lbl = QLabel(f"Internal Renderer handling triggered for file format: .{ext.upper()}\n\nFile Name: {os.path.basename(path)}")
            self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(self.lbl)

        self.bottom_layout = QHBoxLayout()
        self.bottom_layout.addStretch() 
        
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setMinimumWidth(120)

        if ext in ['txt', 'py', 'json', 'md', 'csv', 'log', 'ini']:
            self.save_btn.setVisible(True)
        else:
            self.save_btn.setVisible(False)
            
        self.save_btn.clicked.connect(self.save_file)
        self.bottom_layout.addWidget(self.save_btn)
        
        self.main_layout.addLayout(self.bottom_layout)

    def save_file(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
                
            self.save_btn.setText("Saved ✔")
            self.save_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        except Exception as e:
            self.save_btn.setText("Error Saving ✖")
            self.save_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
            print(f"Failed to save: {e}")

    def reset_save_button(self):
        if self.save_btn.text() != "Save Changes":
            self.save_btn.setText("Save Changes")
            self.save_btn.setStyleSheet("") 

def open_file(path, parent=None):
    dialog = CustomRenderer(path, parent)
    dialog.exec()