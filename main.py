import sys
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QComboBox, QSpinBox, QHBoxLayout,
                             QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap

class ScreenMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configuration de la fenêtre
        self.setWindowTitle("Mon App Miroir - Partage d'écran Android")
        self.setGeometry(100, 100, 500, 400)
        
        # Chemin vers scrcpy.exe
        self.scrcpy_path = os.path.join(os.path.dirname(__file__), "scrcpy-windows", "scrcpy.exe")
        self.adb_path = os.path.join(os.path.dirname(__file__), "scrcpy-windows", "adb.exe")
        
        # Créer l'interface
        self.setup_ui()
        
    def setup_ui(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Titre
        title = QLabel("📱 Partage d'écran Android")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Connectez votre téléphone via USB ou Wi-Fi")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Bouton USB
        usb_button = QPushButton("🔌 Connexion USB")
        usb_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        usb_button.clicked.connect(self.connect_usb)
        layout.addWidget(usb_button)
        
        # Bouton Wi-Fi
        wifi_button = QPushButton("📶 Connexion Wi-Fi")
        wifi_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        wifi_button.clicked.connect(self.connect_wifi)
        layout.addWidget(wifi_button)
        
        # Bouton Paramètres
        settings_button = QPushButton("⚙️ Paramètres")
        settings_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        settings_button.clicked.connect(self.show_settings)
        layout.addWidget(settings_button)
        
        layout.addSpacing(20)
        
        # Status
        self.status_label = QLabel("Prêt à connecter...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #34495e; font-style: italic;")
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
    
    def connect_usb(self):
        self.status_label.setText("🔌 Connexion USB en cours...")
        self.launch_scrcpy()
    
    def connect_wifi(self):
        # Récupérer l'IP du téléphone
        ip = self.get_phone_ip()
        if ip:
            self.status_label.setText(f"📶 Connexion Wi-Fi à {ip}...")
            self.launch_scrcpy(is_wifi=True)
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de détecter le téléphone en Wi-Fi")
            self.status_label.setText("Prêt à connecter...")
    
    def get_phone_ip(self):
        try:
            # Exécuter adb pour trouver l'IP
            result = subprocess.run([self.adb_path, "shell", "ip", "route"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'src' in line:
                        parts = line.split()
                        if 'src' in parts:
                            idx = parts.index('src')
                            return parts[idx + 1]
        except Exception as e:
            print(f"Erreur: {e}")
        return None
    
    def launch_scrcpy(self, is_wifi=False):
        try:
            # Commande scrcpy de base
            cmd = [self.scrcpy_path]
            
            # Paramètres de qualité
            cmd.extend(["--max-size", "1080"])  # Résolution max 1080p
            cmd.extend(["--max-fps", "60"])      # 60 FPS
            cmd.extend(["--video-bit-rate", "2M"])  # Bitrate 2 Mbps
            
            # Si Wi-Fi, ajouter le flag TCP
            if is_wifi:
                cmd.append("--tcpip")
            
            # Lancer scrcpy
            self.status_label.setText("✅ Partage d'écran actif")
            subprocess.Popen(cmd)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lancer scrcpy: {str(e)}")
            self.status_label.setText("Prêt à connecter...")
    
    def show_settings(self):
        QMessageBox.information(self, "Paramètres", 
                              "Paramètres actuels :\n"
                              "• Résolution : 1080p\n"
                              "• FPS : 60\n"
                              "• Bitrate : 2 Mbps\n\n"
                              "Les paramètres avancés seront ajoutés bientôt !")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
