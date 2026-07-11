import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QMessageBox, QListWidget, QDialog, 
                             QDialogButtonBox, QListWidgetItem, QInputDialog)
from PyQt5.QtCore import Qt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ScreenMirrorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mon App Miroir - Partage d'écran Android")
        self.setGeometry(100, 100, 500, 400)
        
        # Utilisation de la fonction magique pour les chemins
        self.scrcpy_path = resource_path(os.path.join("scrcpy-windows", "scrcpy.exe"))
        self.adb_path = resource_path(os.path.join("scrcpy-windows", "adb.exe"))
        
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
        
        # Bouton Configurer Wi-Fi
        wifi_config_button = QPushButton("️ Configurer Wi-Fi")
        wifi_config_button.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                font-size: 16px;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        wifi_config_button.clicked.connect(self.configure_wifi)
        layout.addWidget(wifi_config_button)
        
        # Bouton Wi-Fi
        wifi_button = QPushButton(" Connexion Wi-Fi")
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
    
    def configure_wifi(self):
        self.status_label.setText("⚙️ Configuration Wi-Fi en cours...")
        QApplication.processEvents()
        try:
            # Vérifier si un appareil est connecté en USB (timeout 30s)
            devices_result = subprocess.run([self.adb_path, "devices"], 
                                          capture_output=True, text=True, timeout=30)
            
            # Compter les appareils connectés (ignorer la ligne d'en-tête)
            lines = devices_result.stdout.strip().split('\n')
            device_count = sum(1 for line in lines[1:] if line.strip() and "device" in line and "unauthorized" not in line)
            
            if device_count == 0:
                raise Exception("Aucun appareil connecté en USB. Branchez d'abord le câble.")
            
            # Configurer ADB en mode TCP/IP (timeout 30s)
            result = subprocess.run([self.adb_path, "tcpip", "5555"],
                                  capture_output=True, text=True, timeout=30)
            
            if "restarting in TCP mode" not in result.stdout.lower() and result.returncode != 0:
                raise Exception(f"Erreur lors de la configuration : {result.stderr}")
            
            self.status_label.setText("✅ Configuration Wi-Fi réussie ! Débranchez le câble.")
            QMessageBox.information(self, "Succès", 
                                  "Configuration Wi-Fi réussie !\n\n"
                                  "1️⃣ Débranchez le câble USB\n"
                                  "2️⃣ Cliquez sur 'Connexion Wi-Fi'")
        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Erreur", 
                               "La commande ADB a pris trop de temps.\n\n"
                               "Vérifiez que :\n"
                               "- Le câble USB est bien branché\n"
                               "- Le débogage USB est activé sur le téléphone\n"
                               "- Vous avez accepté l'autorisation sur le téléphone")
            self.status_label.setText("Prêt à configurer...")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de configurer Wi-Fi :\n{str(e)}")
            self.status_label.setText("Prêt à configurer...")
    
    def connect_usb(self):
        self.status_label.setText(" Connexion USB en cours...")
        self.launch_scrcpy()
    
    def connect_wifi(self):
        self.status_label.setText("🔍 Recherche des téléphones en Wi-Fi...")
        QApplication.processEvents()

        try:
            # Lister les appareils ADB (timeout 30s)
            result = subprocess.run([self.adb_path, "devices", "-l"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"Erreur ADB : {result.stderr}")

            lines = result.stdout.strip().split('\n')
            devices = []
            
            for line in lines[1:]:  # sauter la première ligne
                if not line.strip() or "unauthorized" in line or "offline" in line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                serial = parts[0]
                # Si l'ID contient un :, c'est un appareil Wi-Fi
                if ':' in serial and '.' in serial.split(':')[0]:
                    ip_port = serial
                    # Extraire le nom du modèle
                    model = "Android Device"
                    for part in parts[1:]:
                        if "model:" in part:
                            model = part.replace("model:", "").replace("_", " ")
                            break
                        elif "device:" in part:
                            model = part.replace("device:", "").replace("_", " ")
                    devices.append((ip_port, model))

            if not devices:
                QMessageBox.warning(self, "Aucun appareil", 
                                   "Aucun téléphone en Wi-Fi détecté.\n\n"
                                   "✅ Pour activer le Wi-Fi :\n"
                                   "1️⃣ Branchez le téléphone en USB\n"
                                   "2️⃣ Cliquez sur 'Configurer Wi-Fi'\n"
                                   "3️⃣ Débranchez le câble\n"
                                   "4️⃣ Cliquez sur 'Connexion Wi-Fi'")
                self.status_label.setText("Prêt à connecter...")
                return

            # Créer une boîte de dialogue avec liste
            dialog = QDialog(self)
            dialog.setWindowTitle("Sélectionnez votre téléphone")
            layout = QVBoxLayout()

            list_widget = QListWidget()
            for ip_port, model in devices:
                item = QListWidgetItem(f"{model} ({ip_port})")
                item.setData(Qt.UserRole, ip_port)
                list_widget.addItem(item)

            layout.addWidget(list_widget)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            layout.addWidget(button_box)
            dialog.setLayout(layout)

            def on_ok():
                selected = list_widget.currentItem()
                if selected:
                    ip_port = selected.data(Qt.UserRole)
                    dialog.accept()
                    self.connect_to_device(ip_port)
                else:
                    QMessageBox.warning(dialog, "Erreur", "Veuillez choisir un téléphone.")
            
            button_box.accepted.connect(on_ok)
            button_box.rejected.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                pass

        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Erreur", 
                               "La recherche d'appareils a pris trop de temps.\n\n"
                               "Vérifiez que le téléphone est sur le même réseau Wi-Fi.")
            self.status_label.setText("Prêt à connecter...")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lister les appareils :\n{str(e)}")
            self.status_label.setText("Prêt à connecter...")

    def connect_to_device(self, ip_port):
        self.status_label.setText(f" Connexion à {ip_port}...")
        try:
            # Se connecter (au cas où ce n'est pas encore fait) (timeout 30s)
            connect_result = subprocess.run([self.adb_path, "connect", ip_port],
                                          capture_output=True, text=True, timeout=30)
            if "connected" not in connect_result.stdout.lower():
                raise Exception(f"Échec de connexion : {connect_result.stderr}")

            # Lancer scrcpy
            cmd = [self.scrcpy_path, "--tcpip"]
            subprocess.Popen(cmd)
            self.status_label.setText("✅ Partage d'écran Wi-Fi actif")

        except subprocess.TimeoutExpired:
            QMessageBox.critical(self, "Erreur", 
                               "La connexion a pris trop de temps.\n\n"
                               "Vérifiez que le téléphone est allumé et sur le même Wi-Fi.")
            self.status_label.setText("Prêt à connecter...")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de lancer le partage :\n{str(e)}")
            self.status_label.setText("Prêt à connecter...")

    def launch_scrcpy(self):
        try:
            # Commande scrcpy de base
            cmd = [self.scrcpy_path]
            
            # Paramètres de qualité
            cmd.extend(["--max-size", "1080"])  # Résolution max 1080p
            cmd.extend(["--max-fps", "60"])      # 60 FPS
            cmd.extend(["--video-bit-rate", "2M"])  # Bitrate 2 Mbps
            
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
