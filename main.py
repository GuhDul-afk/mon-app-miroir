import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ScreenMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ScreenMirror")
        self.setFixedSize(450, 500)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            background-color: rgba(20, 20, 25, 240);
            border-radius: 20px;
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(0, 0, 0, 200))
        main_widget.setGraphicsEffect(shadow)
        
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(25)
        layout.setContentsMargins(40, 30, 40, 40)
        
        # Bouton fermer
        close_layout = QHBoxLayout()
        close_btn = QLabel("✕")
        close_btn.setAlignment(Qt.AlignRight)
        close_btn.setStyleSheet("color: #555; font-size: 18px; padding: 5px;")
        close_btn.mousePressEvent = lambda event: self.close()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        layout.addSpacing(20)
        
        # Titre
        title = QLabel("ScreenMirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Partage d'écran Android haute qualité")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 14px;
            color: #666666;
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Zone de statut
        self.status_label = QLabel("Prêt à connecter")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        """)
        layout.addWidget(self.status_label)
        
        # Badge qualité
        quality_badge = QLabel("1080p • 60fps • 8Mbps")
        quality_badge.setAlignment(Qt.AlignCenter)
        quality_badge.setStyleSheet("""
            font-size: 12px;
            color: #444444;
            padding: 8px;
            margin-top: 10px;
        """)
        layout.addWidget(quality_badge)
        
        layout.addStretch()
        
        # Bouton principal
        self.action_button = QPushButton("CONNECTER")
        self.action_button.setFixedHeight(56)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 16px;
                font-weight: 600;
                border-radius: 28px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0062CC;
            }
            QPushButton:pressed {
                background-color: #0051A8;
            }
        """)
        self.action_button.clicked.connect(self.toggle_connection)
        layout.addWidget(self.action_button)
        
        layout.addSpacing(10)
        
        main_widget.setLayout(layout)
    
    def toggle_connection(self):
        if self.action_button.text() == "CONNECTER":
            self.start_connection()
        else:
            self.stop_connection()

    def start_connection(self):
        self.status_label.setText("Connexion en cours...")
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #ffffff;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        """)
        
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=10)
            
            if "device" not in result.stdout:
                raise Exception("Aucun appareil détecté. Vérifiez le câble USB et le débogage.")
            
            cmd = [
                self.scrcpy_path,
                "--max-size", "0",
                "--max-fps", "60",
                "--video-bit-rate", "8M",
                "--render-driver", "opengl",
                "--window-title", "ScreenMirror",
                "--always-on-top"
            ]
            
            self.process = subprocess.Popen(cmd)
            
            self.status_label.setText("Connecté - Qualité maximale")
            self.status_label.setStyleSheet("""
                font-size: 16px;
                color: #4cd964;
                padding: 20px;
                background-color: rgba(76, 217, 100, 0.1);
                border-radius: 12px;
            """)
            
            self.action_button.setText("DÉCONNECTER")
            self.action_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    color: white;
                    font-size: 16px;
                    font-weight: 600;
                    border-radius: 28px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #D70015;
                }
            """)
            
        except Exception as e:
            self.status_label.setText(f"Erreur: {str(e)}")
            self.status_label.setStyleSheet("""
                font-size: 16px;
                color: #FF3B30;
                padding: 20px;
                background-color: rgba(255, 59, 48, 0.1);
                border-radius: 12px;
            """)
            self.action_button.setText("Réessayer")

    def stop_connection(self):
        if hasattr(self, 'process'):
            self.process.terminate()
        
        self.status_label.setText("Prêt à connecter")
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        """)
        
        self.action_button.setText("CONNECTER")
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 16px;
                font-weight: 600;
                border-radius: 28px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0062CC;
            }
        """)

if __name__ == "__main__":
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
