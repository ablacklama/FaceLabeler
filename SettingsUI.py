from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt


class settingsWindow(QDialog):
    reloadsignal = pyqtSignal(bool, bool)
    def __init__(self, parent):
        super(settingsWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        loadUi('data/ui/settings.ui',self)
        self.setWindowIcon(QIcon("data/ui/icon.ico"))
        self.parent = parent
        self.loadText()
        self.buttonArray.button(QDialogButtonBox.Discard).clicked.connect(self.loadText)
        self.buttonArray.button(QDialogButtonBox.Save).clicked.connect(lambda: self.reload(False))
        self.buttonArray.button(QDialogButtonBox.RestoreDefaults).clicked.connect(lambda: self.reload(True))

    def loadText(self):
        self.detectionDelay.setValue(self.parent.PhotoData.detectionDelay)
        self.imageDir.setText(self.parent.saver.imageDir)
        self.labelListPath.setText(self.parent.saver.labelListPath)
        self.labelConfigPath.setText(self.parent.saver.labelConfigPath)


    def reload(self, defaults):
        self.reloadsignal.emit(defaults, True)
