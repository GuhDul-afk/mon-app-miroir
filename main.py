import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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
        self.setFixedSize(420, 400)
        
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self.setup_ui()
    
    def setup_ui(self):
        # Style global de la fenêtre
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1f;
            }
        """)
        
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1a1a1f;")
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 30, 40, 30)
        
        # Titre
        title = QLabel("ScreenMirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: 600;
            color: #ffffff;
        """)
        layout.addWidget(title)
        
        subtitle = QLabel("Partage d'écran Android haute qualité")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #555555;
        """)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Zone de statut
        self.status_label = QLabel("Prêt à connecter")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(50)
        self.status_label.setStyleSheet("""
            font-size: 15px;
            color: #888888;
            padding: 12px 20px;
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 10px;
        """)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Bouton principal
        self.action_button = QPushButton("CONNECTER")
        self.action_button.setFixedHeight(52)
        self.action_button.setCursor(Qt.PointingHandCursor)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 10px;
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
        
        central_widget.setLayout(layout)
    
    def toggle_connection(self):
        if self.action_button.text() == "CONNECTER":
            self.start_connection()
        else:
            self.stop_connection()

    def start_connection(self):
        self.status_label.setText("Connexion en cours...")
        self.status_label.setStyleSheet("""
            font-size: 15px;
            color: #ffffff;
            padding: 12px 20px;
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 10px;
        """)
        
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=30)
            
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
                font-size: 15px;
                color: #4cd964;
                padding: 12px 20px;
                background-color: rgba(76, 217, 100, 0.1);
                border-radius: 10px;
            """)
            
            self.action_button.setText("DÉCONNECTER")
            self.action_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    border-radius: 10px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #D70015;
                }
            """)
            
        except subprocess.TimeoutExpired:
            self.status_label.setText("Timeout : ADB n'a pas répondu à temps.")
            self.status_label.setStyleSheet("""
                font-size: 15px;
                color: #FF3B30;
                padding: 12px 20px;
                background-color: rgba(255, 59, 48, 0.1);
                border-radius: 10px;
            """)
            self.action_button.setText("RÉESSAYER")
        except Exception as e:
            self.status_label.setText(f"Erreur : {str(e)}")
            self.status_label.setStyleSheet("""
                font-size: 15px;
                color: #FF3B30;
                padding: 12px 20px;
                background-color: rgba(255, 59, 48, 0.1);
                border-radius: 10px;
            """)
            self.action_button.setText("RÉESSAYER")

    def stop_connection(self):
        if hasattr(self, 'process') and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        self.status_label.setText("Prêt à connecter")
        self.status_label.setStyleSheet("""
            font-size: 15px;
            color: #888888;
            padding: 12px 20px;
            background-color: rgba(255, 255, 255, 0.04);
            border-radius: 10px;
        """)
        
        self.action_button.setText("CONNECTER")
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 15px;
                font-weight: 600;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0062CC;
            }
        """)

    def closeEvent(self, event):
        if hasattr(self, 'process') and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        event.accept()

if __name__ == "__main__":
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
