import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox
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
        self.setFixedSize(500, 400)
        self.setStyleSheet("background-color: #f5f5f7;")
        
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Titre
        title = QLabel("📱 ScreenMirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #1d1d1f; margin: 20px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Partage d'écran Android haute qualité")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #86868b; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Séparateur
        separator = QLabel("________________________________________")
        separator.setAlignment(Qt.AlignCenter)
        separator.setStyleSheet("color: #d2d2d7;")
        layout.addWidget(separator)
        
        layout.addSpacing(30)
        
        # Bouton Connecter
        self.connect_button = QPushButton("🔌 Connecter")
        self.connect_button.setFixedHeight(60)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
            QPushButton:pressed {
                background-color: #005ecb;
            }
        """)
        self.connect_button.clicked.connect(self.connect_usb)
        layout.addWidget(self.connect_button)
        
        # Bouton Déconnecter
        self.disconnect_button = QPushButton(" Déconnecter")
        self.disconnect_button.setFixedHeight(60)
        self.disconnect_button.setStyleSheet("""
            QPushButton {
                background-color: #ff3b30;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 12px;
                border: none;
            }
            QPushButton:hover {
                background-color: #ff453a;
            }
            QPushButton:pressed {
                background-color: #e6352b;
            }
        """)
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.setVisible(False)
        layout.addWidget(self.disconnect_button)
        
        layout.addStretch()
        
        # Status
        self.status_label = QLabel("⚪ Prêt à connecter")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 15px; color: #86868b; padding: 20px;")
        layout.addWidget(self.status_label)
        
        # Info qualité
        quality_label = QLabel("🎬 1080p • 60fps • 8Mbps")
        quality_label.setAlignment(Qt.AlignCenter)
        quality_label.setStyleSheet("font-size: 12px; color: #86868b; background-color: white; padding: 10px; border-radius: 8px;")
        layout.addWidget(quality_label)
        
        central_widget.setLayout(layout)
    
    def connect_usb(self):
        self.status_label.setText("🔵 Connexion en cours...")
        self.status_label.setStyleSheet("font-size: 15px; color: #0071e3; padding: 20px; font-weight: bold;")
        
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
                "--audio-bit-rate", "128K",
                "--render-driver", "opengl",
                "--window-title", "ScreenMirror",
                "--always-on-top"
            ]
            
            self.process = subprocess.Popen(cmd)
            
            self.status_label.setText("🟢 Connecté - Qualité maximale")
            self.status_label.setStyleSheet("font-size: 15px; color: #34c759; padding: 20px; font-weight: bold;")
            
            self.connect_button.setVisible(False)
            self.disconnect_button.setVisible(True)
            
        except subprocess.TimeoutExpired:
            self.show_error("La connexion a pris trop de temps. Réessayez.")
        except Exception as e:
            self.show_error(str(e))
    
    def disconnect(self):
        try:
            if hasattr(self, 'process'):
                self.process.terminate()
            
            self.status_label.setText("⚪ Prêt à connecter")
            self.status_label.setStyleSheet("font-size: 15px; color: #86868b; padding: 20px;")
            
            self.connect_button.setVisible(True)
            self.disconnect_button.setVisible(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur: {str(e)}")
    
    def show_error(self, message):
        self.status_label.setText("🔴 Erreur")
        self.status_label.setStyleSheet("font-size: 15px; color: #ff3b30; padding: 20px; font-weight: bold;")
        QMessageBox.critical(self, "Erreur", message)
        self.connect_button.setVisible(True)
        self.disconnect_button.setVisible(False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 13)
    app.setFont(font)
    
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
