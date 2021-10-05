"""Job runner for screenshooter"""

import time
from PyQt5 import QtCore
from backend.screen import Screen
from backend.disk_usage import main as disk_usage


class WorkerSignals(QtCore.QObject):
    """Signals for JobRunner"""
    progress = QtCore.pyqtSignal(int)
    progress_percent = QtCore.pyqtSignal(str)

class JobRunner(QtCore.QRunnable):
    """Job Runner to do thread"""
    signals = WorkerSignals()

    def __init__(self, path, quality, interval):
        """Constructor of Job Runner"""
        super().__init__()
        self.path = path
        self.quality = quality
        self.interval = interval
        self.iteration = 0
        self.is_killed = False
        
    @QtCore.pyqtSlot()
    def run(self):
        """Run thread to make screen"""
        screen = Screen(path=self.path, quality=self.quality, interval=self.interval)
        while True:
            disk = disk_usage(self.path)
            disk_percent_usage = str(round(disk['Used']*100/disk['Total'], 2))
            self.iteration += 1
            screen.start_job()
            self.signals.progress.emit(self.iteration)
            self.signals.progress_percent.emit(disk_percent_usage)
            time.sleep(self.interval)
            if self.is_killed:
                break

    def kill(self):
        """Kill thread after signal"""
        self.is_killed = True
