import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
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
        
        # Configuration fenêtre
        self.setWindowTitle("ScreenMirror")
        self.setFixedSize(600, 500)
        self.setStyleSheet("background-color: #f5f5f7;")
        
        # Chemins
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self.setup_ui()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        
        # Logo/Titre style Apple
        title_container = QWidget()
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Logo (emoji ou icône)
        logo = QLabel("📱")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("font-size: 64px; padding: 20px;")
        title_layout.addWidget(logo)
        
        # Titre principal
        title = QLabel("ScreenMirror")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: 600;
            color: #1d1d1f;
            letter-spacing: -0.5px;
        """)
        title_layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Partage d'écran Android haute qualité")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #86868b;
            font-weight: 400;
        """)
        title_layout.addWidget(subtitle)
        
        title_container.setLayout(title_layout)
        layout.addWidget(title_container)
        
        layout.addSpacing(20)
        
        # Séparateur subtil
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #d2d2d7; min-height: 1px; max-height: 1px;")
        layout.addWidget(separator)
        
        layout.addSpacing(20)
        
        # Bouton Connecter USB - Style Apple
        self.connect_button = self.create_apple_button(
            "Connecter",
            "Branchez votre téléphone et cliquez pour démarrer",
            "#0071e3",  # Bleu Apple
            "#0077ed"
        )
        self.connect_button.clicked.connect(self.connect_usb)
        layout.addWidget(self.connect_button)
        
        # Bouton Déconnecter (caché au début)
        self.disconnect_button = self.create_apple_button(
            "Déconnecter",
            "Arrêter le partage d'écran",
            "#ff3b30",  # Rouge Apple
            "#ff453a"
        )
        self.disconnect_button.clicked.connect(self.disconnect)
        self.disconnect_button.setVisible(False)
        layout.addWidget(self.disconnect_button)
        
        layout.addStretch()
        
        # Status moderne
        self.status_container = QWidget()
        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignCenter)
        
        self.status_icon = QLabel("⚪")
        self.status_icon.setAlignment(Qt.AlignCenter)
        self.status_icon.setStyleSheet("font-size: 24px;")
        status_layout.addWidget(self.status_icon)
        
        self.status_label = QLabel("Prêt à connecter")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #86868b;
            font-weight: 400;
        """)
        status_layout.addWidget(self.status_label)
        
        self.status_container.setLayout(status_layout)
        layout.addWidget(self.status_container)
        
        # Qualité badge
        quality_badge = QLabel("🎬 Qualité Max: 1080p • 60fps • 8Mbps")
        quality_badge.setAlignment(Qt.AlignCenter)
        quality_badge.setStyleSheet("""
            font-size: 12px;
            color: #86868b;
            background-color: #ffffff;
            padding: 8px 16px;
            border-radius: 12px;
        """)
        layout.addWidget(quality_badge)
        
        central_widget.setLayout(layout)
    
    def create_apple_button(self, text, description, color, hover_color):
        button_widget = QWidget()
        button_widget.setFixedHeight(120)
        button_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border-radius: 16px;
            }}
            QWidget:hover {{
                background-color: {hover_color};
            }}
        """)
        
        # Ajouter ombre
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        button_widget.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(8)
        
        # Texte principal
        btn_text = QLabel(text)
        btn_text.setStyleSheet("""
            font-size: 22px;
            font-weight: 600;
            color: white;
            letter-spacing: 0.3px;
        """)
        layout.addWidget(btn_text)
        
        # Description
        btn_desc = QLabel(description)
        btn_desc.setStyleSheet("""
            font-size: 13px;
            color: rgba(255, 255, 255, 0.8);
            font-weight: 400;
        """)
        layout.addWidget(btn_desc)
        
        button_widget.setLayout(layout)
        return button_widget
    
    def connect_usb(self):
        self.status_icon.setText("🔵")
        self.status_label.setText("Connexion en cours...")
        self.status_label.setStyleSheet("color: #0071e3; font-weight: 500;")
        
        try:
            # Vérifier la connexion ADB
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=10)
            
            if "device" not in result.stdout:
                raise Exception("Aucun appareil détecté. Vérifiez le câble USB et le débogage.")
            
            # Lancer scrcpy en qualité MAXIMALE
            cmd = [
                self.scrcpy_path,
                "--max-size", "0",           # Pas de réduction (résolution native)
                "--max-fps", "60",           # 60 FPS
                "--video-bit-rate", "8M",    # 8 Mbps (haute qualité)
                "--audio-bit-rate", "128K",  # Audio haute qualité
                "--render-driver", "opengl", # Rendu OpenGL
                "--window-title", "ScreenMirror",
                "--always-on-top",           # Toujours au premier plan
                "--turn-screen-off"          # Éteindre l'écran du téléphone (optionnel)
            ]
            
            self.process = subprocess.Popen(cmd)
            
            # Mettre à jour l'interface
            self.status_icon.setText("🟢")
            self.status_label.setText("Connecté - Qualité maximale")
            self.status_label.setStyleSheet("color: #34c759; font-weight: 500;")
            
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
            
            self.status_icon.setText("")
            self.status_label.setText("Déconnecté")
            self.status_label.setStyleSheet("color: #86868b; font-weight: 400;")
            
            self.connect_button.setVisible(True)
            self.disconnect_button.setVisible(False)
            
        except Exception as e:
            self.show_error(f"Erreur lors de la déconnexion: {str(e)}")
    
    def show_error(self, message):
        from PyQt5.QtWidgets import QMessageBox
        self.status_icon.setText("🔴")
        self.status_label.setText("Erreur de connexion")
        self.status_label.setStyleSheet("color: #ff3b30; font-weight: 500;")
        
        msg = QMessageBox()
        msg.setWindowTitle("Erreur")
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #1d1d1f;
                font-size: 13px;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0077ed;
            }
        """)
        msg.exec_()
        
        self.connect_button.setVisible(True)
        self.disconnect_button.setVisible(False)

if __name__ == "__main__":
    # Configuration du style global
    app = QApplication(sys.argv)
    
    # Police système moderne
    font = QFont("SF Pro Display", 13)
    if not QFont("SF Pro Display").exactMatch():
        font = QFont("Segoe UI", 13)  # Fallback pour Windows
    app.setFont(font)
    
    window = ScreenMirrorApp()
    window.show()
    sys.exit(app.exec_())
