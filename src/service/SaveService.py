from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, QMetaObject


class SaveService(QObject):
    should_save = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._emit_should_save)
        self.is_waiting = False

    def trigger(self):
        if self.is_waiting:
            print("Ignoring save trigger")
            return
        print("Triggering save in 10 seconds")
        self.timer.start(10000)
        self.is_waiting = True

    def _emit_should_save(self):
        self.should_save.emit()
        self.is_waiting = False


class SaveServiceThread(QThread):
    def __init__(self):
        super().__init__()
        self.save_service = SaveService()

    def run(self):
        self.save_service.moveToThread(self)
        self.exec_()

    def trigger_save(self):
        self.save_service.trigger()

    def connect(self, handler):
        self.save_service.should_save.connect(handler)

    def pending_save(self):
        return self.save_service.is_waiting
