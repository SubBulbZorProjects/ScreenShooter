"""Gui main file for ScreenShooter"""

import sys
import os
import configparser
from PyQt5 import QtCore, QtGui, QtWidgets
from frontend.screenshootergui import Ui_MainWindow
from backend.configurator import Config
from backend.jobrunner import JobRunner
from backend.disk_usage import main as disk_usage
from backend.configurator import State

class MyMainWindow(QtWidgets.QMainWindow, Ui_MainWindow): # pylint: disable=(c-extension-no-member)
    ''' Initialize Gui '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self)
        self.disk_percent_limit = 95.00
        self.iteration = 0
        self.folder_name = ""
        self.threadpool = QtCore.QThreadPool()
        self.options = QtWidgets.QFileDialog.Options()
        self.local_path_icons = os.path.join(os.path.dirname(__file__),'frontend','images')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.local_path_icons, 'ScreenIcon.ico')))
        self.flag = False
        self.config_dict = {}
        self.config = Config()
        self.msg = QtWidgets.QMessageBox()
        self.__set_attributes()
        self.__set_slider_attributes()
        self.__set_interval_settings()
        self.__set_icons_settings()
        self.read_config()
        self.__set_tray_menu()
        self.closeAppBtn.clicked.connect(lambda: self.close())
        self.minimizeAppBtn.clicked.connect(lambda: self.hide())
        self.pathButton.clicked.connect(self.get_folder_path)
        self.startButton.clicked.connect(self.start_shooter)
        self.qualitySlider.valueChanged.connect(self.update_quality_line)
        self.qualityEditLine.textChanged.connect(self.update_slider)
        self.browseLabel_3.mousePressEvent = self.open_folder

        self.__press_pos = None
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and event.pos():
            self.__press_pos = event.pos()  # remember starting position

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__press_pos = None

    def mouseMoveEvent(self, event):
        if self.__press_pos :  # follow the mouse
            self.move(self.pos() + (event.pos() - self.__press_pos))

    ## METHODS ##
    def __set_tray_menu(self) -> None:
        hide_action = QtWidgets.QAction("Hide", self)
        quit_action = QtWidgets.QAction("Exit", self)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.close)
        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.show)

    def __set_attributes(self) -> None:
        """Set program attributes"""
        self.startButton.setCheckable(True)
        self.counterLine.setText("_ images")
        self.msg.setWindowTitle("Warning")
        self.tray_icon =  QtWidgets.QSystemTrayIcon(QtGui.QIcon(os.path.join(self.local_path_icons,'ScreenIcon.ico')))

    def __set_icons_settings(self) -> None:
        """Settings for icons"""
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(self.local_path_icons,"cil-folder-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pathButton.setIcon(icon)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(os.path.join(self.local_path_icons,"cil-folder-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pathButton.setIcon(icon)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(os.path.join(self.local_path_icons,"icon_close.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closeAppBtn.setIcon(icon1)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(os.path.join(self.local_path_icons,"icon_minimize.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimizeAppBtn.setIcon(icon2)

    def __set_interval_settings(self) -> None:
        """Settings for interval edit line"""
        self.intervalEditLine.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("[1-9][0-9]*")))
        self.intervalEditLine.setText("2") 

    def __set_slider_attributes(self) -> None:
        """Settings for slider"""
        self.qualitySlider.setTickInterval(10)
        self.qualitySlider.setSingleStep(1)
        self.qualitySlider.setRange(1,100)
        self.qualitySlider.setValue(40)
        self.qualityEditLine.setText("40")
        self.qualityEditLine.setValidator(QtGui.QRegExpValidator(QtCore.QRegExp("^[1-9]$|^[1-9][0-9]$|^(100)$")))

    def open_folder(self, *args) -> None:
        """Open folder with screenshoots"""
        if self.folder_name:
            os.startfile(self.folder_name)

    def read_config(self) -> None:
        """Read config / If config not exist make custom"""
        try:
            self.config_dict = self.config.read_config()
        except configparser.NoOptionError as error:
            print("read_config", error)
            
        if self.config_dict != State.CONFIG_ERROR:
            try:
                self.intervalEditLine.setText(self.config_dict['interval'])
                self.qualityEditLine.setText(self.config_dict['quality'])
                self.qualitySlider.setValue(int(self.config_dict["quality"]))
                self.folder_name = self.config_dict['destination']
                self.pathEditLine.setText(self.folder_name)
                self.browseLabel_3.setText("Open folder")
                self.set_disk_percent()

            except ValueError as value_error: # TODO dywersyfikacja wyjątków
                print(value_error)
                self.intervalEditLine.setText("2")
                self.qualityEditLine.setText("40")
                self.qualitySlider.setValue(40)
            except KeyError as dict_error:
                print("Invalid key!", dict_error)

    def show_message(self, text: str) -> None:
        """Show Message by text"""
        self.msg.setIcon(QtWidgets.QMessageBox.Warning)
        self.msg.setText(text)
        self.msg.exec_()

    def set_disk_percent(self) -> None:
        """Set disk usege to label"""
        disk = disk_usage(self.folder_name)
        diskPercentUsage = round(disk['Used']*100/disk['Total'], 2)
        self.diskUsageEdit.setText(str(diskPercentUsage) + " %")

    def update_quality_line(self, value: int) -> None:
        """Update quality line by value"""
        self.qualityEditLine.setText(str(value))

    def update_slider(self) -> None:
        """Update slider by text in edit line"""
        if self.qualityEditLine.text() != "":
            self.qualitySlider.setValue(int(self.qualityEditLine.text()))

    def update_progress(self, n: int) -> None:
        """Updating image progress by signal"""
        self.counterLine.setText(str(n) + " images")

    def update_disk_percent(self, n: int) -> None:
        """Updating disk useg by signal"""
        self.diskUsageEdit.setText(n + " %")
        if float(n) >= self.disk_percent_limit:
            self.runner.kill()
            self.update_start_button()
            self.show_message("Not enough memory in this disk, \nChange destination folder")

    def update_start_button(self) -> None:
        """Change visuality of gui after start program"""
        self.pathButton.setDisabled(False)
        self.intervalEditLine.setDisabled(False)
        self.qualityEditLine.setDisabled(False)
        self.qualitySlider.setDisabled(False)
        self.startButton.setStyleSheet("border: 2px solid rgb(52, 59, 72);\n"
                                        "border-radius: 5px;    \n"
                                        "background-color: rgb(52, 59, 72);\n")
        self.startButton.setText("Start")

    def set_buttons_disabled(self) -> None:
        self.pathButton.setDisabled(True)
        self.intervalEditLine.setDisabled(True)
        self.qualityEditLine.setDisabled(True)
        self.qualitySlider.setDisabled(True)

    def start_job_runner(self) -> None:
        self.runner = JobRunner(path=self.folder_name, quality=int(self.qualityEditLine.text()), interval=self.interval)
        self.threadpool.start(self.runner)
        self.runner.signals.progress.connect(self.update_progress)
        self.runner.signals.progress_percent.connect(self.update_disk_percent)
        self.startButton.setStyleSheet("border: 2px solid rgb(52, 59, 72);\n"
                                        "border-radius: 5px;    \n"
                                        "background-color: rgb(255, 121, 198);\n")
        self.startButton.setText("Stop")


    def start_shooter(self) -> None:
        """Method after start program"""
        if self.qualityEditLine.text() != "" and self.intervalEditLine != "" and self.folder_name != "":
            self.set_buttons_disabled()
            self.pathEditLine.setText(str(self.folder_name))
            self.interval = int(self.intervalEditLine.text())
            self.set_disk_percent()
            if float(self.diskUsageEdit.text().replace(" %", "")) >= self.disk_percent_limit:
                self.show_message("Not enough memory in this disk. \nChange destination folder")
            else:
                try:
                    self.config.create_config(path=self.folder_name, interval=self.interval, quality=int(self.qualityEditLine.text()))
                except Exception as error:
                    print("save ",error)

                if self.startButton.isChecked():
                    self.start_job_runner()
                else:
                    self.runner.kill()
                    self.update_start_button()
        else:
            self.show_message("Update parameters")

    def get_folder_path(self) -> None:
        """Open filedialog to get folder path"""
        self.folder_name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder')
        if self.folder_name:
            self.browseLabel_3.setText("Open folder")
            self.set_disk_percent()
        else:
            self.browseLabel_3.setText("Browse folder")
        self.pathEditLine.setText(self.folder_name)

    def closeEvent(self, event) -> None: ## ?? event ??
        """Close event method"""
        reply = QtWidgets.QMessageBox.question(self, 'Close window',
            'Are you sure you want to close the window?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No) 

        if reply == QtWidgets.QMessageBox.Yes: 
            event.accept()
            print('Window closed')
        else:
            event.ignore()

    ## /METHODS

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv) 
    MyMainWindow = MyMainWindow()
    MyMainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    MyMainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    MyMainWindow.show()
    sys.exit(app.exec_())
