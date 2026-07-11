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
        
        # Configuration de la fenêtre (Mode Sombre et Transparence)
        self.setWindowTitle("ScreenMirror")
        self.setFixedSize(450, 550)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Enlève la barre de titre par défaut
        self.setAttribute(Qt.WA_TranslucentBackground) # Fond transparent
        
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self.setup_ui()
    
    def setup_ui(self):
        # Conteneur principal (Le verre)
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            background-color: rgba(30, 30, 35, 230); 
            border-radius: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        """)
        # Ajouter une ombre portée
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        main_widget.setGraphicsEffect(shadow)
        
        self.setCentralWidget(main_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 40)
        
        # Barre de fermeture personnalisée (tout en haut à droite)
        close_layout = QHBoxLayout()
        close_btn = QLabel("✕")
        close_btn.setAlignment(Qt.AlignRight)
        close_btn.setStyleSheet("color: #666; font-size: 16px; padding: 10px;")
        close_btn.mousePressEvent = lambda event: self.close()
        close_layout.addWidget(close_btn)
        layout.addLayout(close_layout)
        
        # Titre et Logo
        logo = QLabel("📱")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 48px;")
        layout.addWidget(logo)
        
        title = QLabel("ScreenMirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ffffff; margin-bottom: 5px;")
        layout.addWidget(title)
        
        subtitle = QLabel("Partage d'écran Android haute qualité")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 14px; color: #888888; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Carte de Statut (Zone centrale)
        status_card = QWidget()
        status_card.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
        """)
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Prêt à connecter")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #bbbbbb;")
        status_layout.addWidget(self.status_label)
        
        # Indicateur de qualité
        quality_tag = QLabel("1080p • 60fps • 8Mbps")
        quality_tag.setAlignment(Qt.AlignCenter)
        quality_tag.setStyleSheet("""
            font-size: 11px; color: #555; 
            background-color: #1a1a1a; 
            padding: 5px 10px; border-radius: 5px; margin-top: 10px;
        """)
        status_layout.addWidget(quality_tag)
        
        status_card.setLayout(status_layout)
        layout.addWidget(status_card)
        
        layout.addStretch()
        
        # Bouton Principal
        self.action_button = QPushButton("CONNECTER")
        self.action_button.setFixedHeight(55)
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 27px;
                border: none;
                outline: none;
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
        
        main_widget.setLayout(layout)
    
    def toggle_connection(self):
        if self.action_button.text() == "CONNECTER":
            self.start_connection()
        else:
            self.stop_connection()

    def start_connection(self):
        self.status_label.setText("Connexion en cours...")
        self.status_label.setStyleSheet("font-size: 16px; color: #ffffff;")
        
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=10)
            
            if "device" not in result.stdout:
                raise Exception("Aucun appareil détecté.")
            
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
            
            # Mise à jour UI
            self.status_label.setText("Connecté")
            self.status_label.setStyleSheet("font-size: 16px; color: #4cd964; font-weight: bold;")
            
            self.action_button.setText("DÉCONNECTER")
            self.action_button.setStyleSheet("""
                QPushButton {
                    background-color: #FF3B30;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    border-radius: 27px;
                    border: none;
                }
                QPushButton:hover { background-color: #D70015; }
            """)
            
        except Exception as e:
            self.status_label.setText(f"Erreur: {str(e)}")
            self.status_label.setStyleSheet("font-size: 16px; color: #FF3B30;")
            self.action_button.setText("Réessayer")

    def stop_connection(self):
        if hasattr(self, 'process'):
            self.process.terminate()
        
        self.status_label.setText("Prêt à connecter")
        self.status_label.setStyleSheet("font-size: 16px; color: #bbbbbb;")
        
        self.action_button.setText("CONNECTER")
        self.action_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 27px;
                border: none;
            }
            QPushButton:hover { background-color: #0062CC; }
        """)

if __name__ == "__main__":
    # Force le style Fusion pour un rendu propre sur Windows
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 12)
    app.setFont(font)
    
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
