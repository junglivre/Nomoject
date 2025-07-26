import os
import sys
import pyuac
import winreg
import locale
import gettext
import urllib3
import warnings
import subprocess
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QListWidget, QPushButton, QMessageBox, QFileDialog,
                           QLabel, QListWidgetItem, QHBoxLayout, QFrame,
                           QStatusBar, QStyleFactory, QRadioButton, QButtonGroup)

# Suppress warnings from deprecated modules and other warnings
os.environ['PYTHONWARNINGS'] = 'ignore::DeprecationWarning'
warnings.filterwarnings('ignore', message='.*sipPyTypeDict.*')
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning, module='sip')
warnings.filterwarnings('ignore', category=urllib3.exceptions.InsecureRequestWarning)

def get_locales_path():
    """Returns the correct path to the locales folder, whether in development or compiled"""
    if getattr(sys, 'frozen', False):
        # If running as a compiled executable
        return os.path.join(sys._MEIPASS, 'locales')
    else:
        # If running in development
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locales')

class DeviceListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.NoSelection)  # Disable selection highlighting
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 5px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #2d2d2d;
            }
        """)

class NomojectMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Detect system language
        system_lang = locale.getdefaultlocale()[0]
        self.current_lang = 'pt_BR' if system_lang and system_lang.startswith('pt') else 'en'
        
        # Setup translation
        self.setup_translation()
        
        self.setWindowTitle(self._("Nomoject - Device Manager"))
        self.setMinimumSize(500, 400)
        self.resize(600, 450)
        
        # Set application style
        self.setStyle(QStyleFactory.create('Fusion'))
        self.setup_dark_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create header with language selector
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Add title row with language selector
        title_row = QHBoxLayout()
        title = QLabel("Nomoject")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title.setOpenExternalLinks(True)
        title.setText("<a href='https://github.com/junglivre/Nomoject' style='color: #ffffff; text-decoration: none;'>Nomoject</a>")
        title.setCursor(Qt.PointingHandCursor)
        
        # Language selector container
        lang_container = QFrame()
        lang_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                padding: 8px;
            }
        """)
        
        lang_layout = QVBoxLayout(lang_container)
        lang_layout.setSpacing(5)
        lang_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create radio buttons for language selection
        self.lang_group = QButtonGroup(self)
        self.radio_en = QRadioButton("English")
        self.radio_pt = QRadioButton("Português")
        
        # Set initial state based on current language
        self.radio_en.setChecked(self.current_lang == "en")
        self.radio_pt.setChecked(self.current_lang == "pt_BR")
        
        # Add radio buttons to group and layout
        self.lang_group.addButton(self.radio_en)
        self.lang_group.addButton(self.radio_pt)
        lang_layout.addWidget(self.radio_en)
        lang_layout.addWidget(self.radio_pt)
        
        # Connect language change signal
        self.lang_group.buttonClicked.connect(self.on_language_changed)
        
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(lang_container)
        header_layout.addLayout(title_row)
        
        description = QLabel(self._("Select devices to hide from Eject popup"))
        description.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(description)
        main_layout.addWidget(header_frame)
        
        # Create list widget with custom styling
        self.device_list = DeviceListWidget()
        main_layout.addWidget(self.device_list)
        
        # Create button container
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        refresh_button = QPushButton(self._("Refresh Devices"))
        refresh_button.clicked.connect(self.load_devices)
        self.generate_button = QPushButton(self._("Generate Registry File"))
        self.generate_button.clicked.connect(self.generate_registry_file)
        
        # Style buttons
        button_style = """
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
        """
        refresh_button.setStyleSheet(button_style)
        self.generate_button.setStyleSheet(button_style)
        
        # Add buttons to layout
        button_layout.addWidget(refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.generate_button)
        main_layout.addWidget(button_container)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #cccccc;
                padding: 5px;
            }
        """)
        
        # Add author link to the right side of status bar
        author_label = QLabel()
        author_label.setStyleSheet("""
            QLabel {
                color: #666666;
                padding-right: 5px;
            }
            QLabel a {
                color: #666666;
                text-decoration: none;
            }
        """)
        author_label.setOpenExternalLinks(True)
        author_label.setText("<a href='https://jung.moe' style='color: #666666; text-decoration: none;'>by jung</a>")
        author_label.setCursor(Qt.PointingHandCursor)
        self.statusBar.addPermanentWidget(author_label)
        
        self.setStatusBar(self.statusBar)
        
        # Load devices
        self.load_devices()
    
    def setup_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.WindowText, QColor("#ffffff"))
        palette.setColor(QPalette.Base, QColor("#252525"))
        palette.setColor(QPalette.AlternateBase, QColor("#2d2d2d"))
        palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ToolTipText, QColor("#ffffff"))
        palette.setColor(QPalette.Text, QColor("#ffffff"))
        palette.setColor(QPalette.Button, QColor("#333333"))
        palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor("#0078d4"))
        palette.setColor(QPalette.Highlight, QColor("#0078d4"))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        self.setPalette(palette)
        
        # Global application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QRadioButton {
                color: #ffffff;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border: 1.2px solid #666666;
                border-radius: 8px;
                background-color: transparent;
            }
            QRadioButton::indicator:hover {
                border-color: #0078d4;
            }
            QRadioButton::indicator:checked {
                border: 1.2px solid #0078d4;
                background: qradialgradient(
                    cx:0.5, cy:0.5,
                    fx:0.5, fy:0.5,
                    radius:0.45,
                    stop:0 #0078d4,
                    stop:0.6 #0078d4,
                    stop:0.7 transparent
                );
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QMessageBox {
                background-color: #1e1e1e;
            }
            QMessageBox QLabel {
                color: #ffffff;
            }
            QMessageBox QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1084d8;
            }
            QMessageBox QPushButton:pressed {
                background-color: #006cbd;
            }
        """)
    
    def setup_translation(self):
        """Sets up translation based on current language"""
        localedir = get_locales_path()
        self.translate = gettext.translation('nomoject', localedir, languages=[self.current_lang], fallback=True)
        self._ = self.translate.gettext
    
    def on_language_changed(self, button):
        """Changes the application language when a radio button is selected"""
        new_lang = "pt_BR" if button == self.radio_pt else "en"
        if new_lang != self.current_lang:
            self.current_lang = new_lang
            self.setup_translation()
            self.retranslate_ui()
    
    def retranslate_ui(self):
        """Updates all interface texts with the new language"""
        self.setWindowTitle(self._("Nomoject - Device Manager"))
        
        # Update description - looking for specific text to ensure we get the correct label
        for label in self.findChildren(QLabel):
            if label.text() == "Nomoject":
                continue  # Skip the title that should not be translated
            if "Select devices" in label.text() or "Selecione os dispositivos" in label.text():
                label.setText(self._("Select devices to hide from Eject popup"))
                break
        
        # Update buttons
        refresh_button = None
        for button in self.findChildren(QPushButton):
            if "Refresh" in button.text() or "Atualizar" in button.text():
                button.setText(self._("Refresh Devices"))
            elif "Generate" in button.text() or "Gerar" in button.text():
                button.setText(self._("Generate Registry File"))
        
        # Reload devices to update messages
        self.load_devices()
    
    def load_devices(self):
        self.statusBar.showMessage(self._("Loading devices..."))
        self.device_list.clear()
        self.devices = []
        
        try:
            pci_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                    r"SYSTEM\CurrentControlSet\Enum\PCI",
                                    0, winreg.KEY_READ)
            
            i = 0
            while True:
                try:
                    vendor_key_name = winreg.EnumKey(pci_key, i)
                    vendor_key = winreg.OpenKey(pci_key, vendor_key_name)
                    
                    j = 0
                    while True:
                        try:
                            instance_name = winreg.EnumKey(vendor_key, j)
                            instance_key = winreg.OpenKey(vendor_key, instance_name)
                            
                            try:
                                capabilities, _ = winreg.QueryValueEx(instance_key, "Capabilities")
                                if capabilities == 6:  # Removable device
                                    try:
                                        device_desc, _ = winreg.QueryValueEx(instance_key, "DeviceDesc")
                                        if ';' in device_desc:
                                            device_desc = device_desc.split(';')[-1]
                                        
                                        full_path = f"SYSTEM\\CurrentControlSet\\Enum\\PCI\\{vendor_key_name}\\{instance_name}"
                                        self.devices.append({
                                            'path': full_path,
                                            'desc': device_desc,
                                            'vendor_key': vendor_key_name,
                                            'instance': instance_name
                                        })
                                        
                                        item = QListWidgetItem()
                                        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                                        item.setCheckState(Qt.Unchecked)
                                        item.setText(device_desc)
                                        self.device_list.addItem(item)
                                    except WindowsError:
                                        pass
                            except WindowsError:
                                pass
                            
                            j += 1
                        except WindowsError:
                            break
                        finally:
                            try:
                                winreg.CloseKey(instance_key)
                            except:
                                pass
                    
                    i += 1
                except WindowsError:
                    break
                finally:
                    try:
                        winreg.CloseKey(vendor_key)
                    except:
                        pass
                        
            self.statusBar.showMessage(self._("Found %d removable device(s)") % len(self.devices))
            
        except WindowsError as e:
            QMessageBox.critical(self, self._("Error"), self._("Failed to access registry: %s") % str(e))
            self.statusBar.showMessage(self._("Error loading devices"))
        finally:
            try:
                winreg.CloseKey(pci_key)
            except:
                pass
    
    def create_scheduled_task(self, reg_file_path):
        """Creates a scheduled task to apply the registry file at system startup"""
        try:
            # Create _utils directory if it doesn't exist
            system_drive = os.environ['SystemDrive']
            utils_dir = os.path.join(system_drive + "\\", "Windows", "System32", "_utils")
            os.makedirs(utils_dir, exist_ok=True)
            
            # Copy registry file to _utils directory
            new_reg_path = os.path.join(utils_dir, os.path.basename(reg_file_path))
            import shutil
            shutil.copy2(reg_file_path, new_reg_path)
            
            # Create task command with correct path
            task_name = "NomojectRegistryApply"
            task_cmd = f'schtasks /Create /TN "{task_name}" /TR "regedit.exe /s \\"%SystemDrive%\\Windows\\System32\\_utils\\{os.path.basename(reg_file_path)}\\"" /SC ONSTART /RU SYSTEM /RL HIGHEST /F'
            
            # Execute command as administrator
            result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(result.stderr)
                
            return True, new_reg_path
            
        except Exception as e:
            return False, str(e)

    def generate_registry_file(self):
        selected_items = [self.device_list.item(i) for i in range(self.device_list.count())
                         if self.device_list.item(i).checkState() == Qt.Checked]
        
        if not selected_items:
            QMessageBox.warning(self, self._("Warning"), self._("Please select at least one device."))
            return
        
        selected_indices = [self.device_list.row(item) for item in selected_items]
        selected_devices = [self.devices[i] for i in selected_indices]
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self._("Save Registry File"),
            "",
            self._("Registry Files (*.reg);;All Files (*.*)")
        )
        
        if not file_path:
            return
            
        if not file_path.endswith('.reg'):
            file_path += '.reg'
        
        try:
            self.statusBar.showMessage(self._("Generating registry file..."))
            with open(file_path, 'w', encoding='utf-16') as f:
                f.write("Windows Registry Editor Version 5.00\n\n")
                
                for device in selected_devices:
                    f.write(f"[HKEY_LOCAL_MACHINE\\{device['path']}]\n")
                    f.write('"Capabilities"=dword:00000002\n\n')
            
            self.statusBar.showMessage(self._("Registry file generated successfully"))
            
            reply = QMessageBox.question(
                self,
                self._("Success"),
                self._("Registry file generated successfully. Would you like to create a startup task to apply it automatically?"),
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success, result = self.create_scheduled_task(file_path)
                if success:
                    QMessageBox.information(
                        self,
                        self._("Success"),
                        self._("Startup task created successfully. The registry changes will be applied automatically at system startup.")
                    )
                    self.statusBar.showMessage(self._("Startup task created successfully"))
                    
                    # Perguntar se quer executar agora
                    reply = QMessageBox.question(
                        self,
                        self._("Run Now"),
                        self._("Would you like to run the task now?"),
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        task_name = "NomojectRegistryApply"
                        run_cmd = f'schtasks /Run /TN "{task_name}"'
                        subprocess.run(run_cmd, shell=True)
                        self.statusBar.showMessage(self._("Task executed successfully"))
                else:
                    QMessageBox.critical(
                        self,
                        self._("Error"),
                        self._("Failed to create startup task: %s") % result
                    )
                    self.statusBar.showMessage(self._("Error creating startup task"))
            else:
                reply = QMessageBox.question(
                    self,
                    self._("Apply Now"),
                    self._("Would you like to apply the registry changes now?"),
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    os.startfile(file_path)
                    self.statusBar.showMessage(self._("Applying registry changes..."))
            
        except Exception as e:
            QMessageBox.critical(self, self._("Error"), self._("Failed to save registry file: %s") % str(e))
            self.statusBar.showMessage(self._("Error generating registry file"))

def main():
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))  # Use Fusion style for better dark theme support
    window = NomojectMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        pyuac.runAsAdmin()
    else:
        main()