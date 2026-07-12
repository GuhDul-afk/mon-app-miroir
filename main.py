import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QHBoxLayout, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QRegion, QPainter, QBitmap

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
        self.setFixedSize(450, 520)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
        self._drag_pos = None
        
        self.setup_ui()
    
    def setup_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            background-color: rgba(20, 20, 25, 180);
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
        layout.setContentsMargins(40, 20, 40, 30)
        
        # Barre de contrôle
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(0)
        
        btn_style = """
            QLabel {
                color: #555;
                font-size: 16px;
                font-weight: bold;
                padding: 6px 12px;
                background-color: rgba(255,255,255,0.05);
                border-radius: 10px;
            }
            QLabel:hover {
                background-color: rgba(255,255,255,0.1);
                color: #888;
            }
        """
        
        minimize_btn = QLabel("—")
        minimize_btn.setAlignment(Qt.AlignCenter)
        minimize_btn.setStyleSheet(btn_style)
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.mousePressEvent = lambda event: self.showMinimized()
        
        close_btn = QLabel("✕")
        close_btn.setAlignment(Qt.AlignCenter)
        close_btn.setStyleSheet(btn_style)
        close_btn.setFixedSize(32, 32)
        close_btn.mousePressEvent = lambda event: self.close()
        
        control_layout.addStretch()
        control_layout.addWidget(minimize_btn)
        control_layout.addWidget(close_btn)
        layout.addLayout(control_layout)
        
        layout.addSpacing(30)
        
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
        self.status_label.setWordWrap(True)
        self.status_label.setMinimumHeight(60)
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            padding: 15px 20px;
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
        
        layout.addSpacing(20)
        
        main_widget.setLayout(layout)
    
    # Masque arrondi pour supprimer les coins carrés transparents
    def paintEvent(self, event):
        path = QPainter(self).path()
        path.addRoundedRect(self.rect(), 20, 20)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)
    
    # Permettre le déplacement de la fenêtre
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def closeEvent(self, event):
        if hasattr(self, 'process') and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        event.accept()
    
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
            padding: 15px 20px;
            background-color: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
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
                font-size: 16px;
                color: #4cd964;
                padding: 15px 20px;
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
            
        except subprocess.TimeoutExpired:
            self.status_label.setText("Timeout : ADB n'a pas répondu à temps.")
            self.status_label.setStyleSheet("""
                font-size: 16px;
                color: #FF3B30;
                padding: 15px 20px;
                background-color: rgba(255, 59, 48, 0.1);
                border-radius: 12px;
            """)
            self.action_button.setText("Réessayer")
        except Exception as e:
            self.status_label.setText(f"Erreur: {str(e)}")
            self.status_label.setStyleSheet("""
                font-size: 16px;
                color: #FF3B30;
                padding: 15px 20px;
                background-color: rgba(255, 59, 48, 0.1);
                border-radius: 12px;
            """)
            self.action_button.setText("Réessayer")

    def stop_connection(self):
        if hasattr(self, 'process') and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        self.status_label.setText("Prêt à connecter")
        self.status_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            padding: 15px 20px;
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
